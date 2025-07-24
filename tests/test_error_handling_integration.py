"""
Integration test to demonstrate error handling mapping from C++ to Python.

This test simulates how the error handling would work when C++ exceptions
are properly mapped to Python exceptions through the pybind11 bindings.
"""

import unittest
import os
import tempfile
import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from python_gpr.exceptions import *
    EXCEPTIONS_AVAILABLE = True
except ImportError:
    EXCEPTIONS_AVAILABLE = False


class TestErrorHandlingIntegrationDemo(unittest.TestCase):
    """
    Demonstrate how the error handling system would work in practice.
    
    This simulates the integration between C++ and Python error handling
    that would occur once the module is fully built.
    """
    
    def setUp(self):
        if not EXCEPTIONS_AVAILABLE:
            self.skipTest("Exception classes not available")
    
    def test_file_operation_error_mapping(self):
        """Demonstrate how file operation errors would be mapped."""
        
        # Simulate a C++ function that detects file not found
        def simulate_cpp_file_operation(filepath):
            """Simulates what happens in the C++ layer."""
            if not os.path.exists(filepath):
                # In real C++, this would be: throw GPRFileError(message, filepath, -2)
                # The pybind11 binding would catch this and map it to Python
                raise map_error_code(-2, f"File not found: {filepath}", 
                                    {"filepath": filepath})
            return True
        
        # Test the error mapping
        with self.assertRaises(GPRFileNotFoundError) as context:
            simulate_cpp_file_operation("/nonexistent/file.gpr")
        
        exception = context.exception
        self.assertEqual(exception.error_code, -2)
        self.assertEqual(exception.filepath, "/nonexistent/file.gpr")
        self.assertIn("not found", str(exception).lower())
        self.assertIn("/nonexistent/file.gpr", str(exception))
    
    def test_parameter_validation_error_mapping(self):
        """Demonstrate how parameter validation errors would be mapped."""
        
        def simulate_cpp_parameter_validation(dtype):
            """Simulates parameter validation in C++ layer."""
            valid_dtypes = ["uint16", "float32"]
            if dtype not in valid_dtypes:
                # In C++: throw GPRParameterError(message, parameter_name, -20)
                raise map_error_code(-20, f"Unsupported dtype '{dtype}'. Supported: {', '.join(valid_dtypes)}", 
                                    {"parameter": "dtype", "supported_types": valid_dtypes})
            return True
        
        # Test parameter error mapping
        with self.assertRaises(GPRParameterError) as context:
            simulate_cpp_parameter_validation("invalid_type")
        
        exception = context.exception
        self.assertEqual(exception.error_code, -20)
        self.assertEqual(exception.parameter_name, "dtype")
        self.assertIn("dtype", str(exception).lower())
        self.assertIn("supported", str(exception).lower())
    
    def test_memory_allocation_error_mapping(self):
        """Demonstrate how memory allocation errors would be mapped."""
        
        def simulate_cpp_memory_allocation(size):
            """Simulates memory allocation in C++ layer."""
            if size > 1024 * 1024 * 1024:  # Simulate failure for > 1GB
                # In C++: throw GPRMemoryError(message, requested_size, -10)
                raise map_error_code(-10, f"Failed to allocate {size} bytes", 
                                    {"requested_size": size})
            return True
        
        # Test memory error mapping
        large_size = 2 * 1024 * 1024 * 1024  # 2GB
        with self.assertRaises(GPRMemoryError) as context:
            simulate_cpp_memory_allocation(large_size)
        
        exception = context.exception
        self.assertEqual(exception.error_code, -10)
        self.assertEqual(exception.requested_size, large_size)
        self.assertIn("allocate", str(exception).lower())
        self.assertIn(str(large_size), str(exception))
    
    def test_format_error_mapping(self):
        """Demonstrate how format errors would be mapped."""
        
        def simulate_cpp_format_validation(format_name):
            """Simulates format validation in C++ layer."""
            supported_formats = ["gpr", "dng", "raw"]
            if format_name not in supported_formats:
                # In C++: throw GPRFormatError -> GPRUnsupportedFormatError
                raise map_error_code(-31, f"Unsupported format '{format_name}'", 
                                    {"format": format_name, "supported_formats": supported_formats})
            return True
        
        # Test format error mapping
        with self.assertRaises(GPRUnsupportedFormatError) as context:
            simulate_cpp_format_validation("xyz")
        
        exception = context.exception
        self.assertEqual(exception.error_code, -31)
        self.assertEqual(exception.format_name, "xyz")
        self.assertEqual(exception.supported_formats, ["gpr", "dng", "raw"])
        self.assertIn("xyz", str(exception))
        self.assertIn("gpr", str(exception))
    
    def test_conversion_error_context(self):
        """Demonstrate how conversion errors would include context."""
        
        def simulate_cpp_conversion(input_path, output_path):
            """Simulates a conversion operation in C++ layer."""
            # Simulate conversion failure
            context = {
                "operation": "GPR to DNG conversion",
                "input_path": input_path,
                "output_path": output_path,
                "step": "format_validation"
            }
            # In C++: throw GPRConversionError with context
            raise GPRConversionError(f"Conversion failed at {context['step']}", 
                                   context=context)
        
        # Test conversion error with context
        with self.assertRaises(GPRConversionError) as context_mgr:
            simulate_cpp_conversion("/input.gpr", "/output.dng")
        
        exception = context_mgr.exception
        self.assertIn("conversion", str(exception).lower())
        self.assertIn("format_validation", str(exception))
        self.assertIn("/input.gpr", str(exception))
        self.assertIn("/output.dng", str(exception))
    
    def test_error_hierarchy_catching(self):
        """Demonstrate how the error hierarchy enables flexible error handling."""
        
        def simulate_file_operations():
            """Simulate various file operations that can fail."""
            operations = [
                lambda: map_error_code(-2, "Not found", {"filepath": "/missing.gpr"}),
                lambda: map_error_code(-3, "Permission denied", {"filepath": "/protected.gpr", "operation": "write"}),
                lambda: map_error_code(-4, "Corrupted", {"filepath": "/bad.gpr", "reason": "Invalid header"}),
            ]
            
            results = []
            for op in operations:
                try:
                    error = op()  # This creates the exception, but doesn't raise it
                    raise error   # Now raise it so we can catch it
                except GPRFileError as e:  # Catch all file errors
                    results.append(f"File error: {type(e).__name__}")
                except GPRError as e:  # Catch any other GPR errors
                    results.append(f"GPR error: {type(e).__name__}")
            
            return results
        
        results = simulate_file_operations()
        
        # All should be caught as file errors due to hierarchy
        self.assertEqual(len(results), 3)
        self.assertTrue(all("File error:" in result for result in results))
        self.assertIn("GPRFileNotFoundError", results[0])
        self.assertIn("GPRFilePermissionError", results[1])
        self.assertIn("GPRFileCorruptedError", results[2])
    
    def test_error_message_actionability(self):
        """Test that error messages provide actionable information."""
        
        # File not found error should suggest checking file path
        file_error = GPRFileNotFoundError("/missing/file.gpr")
        self.assertIn("/missing/file.gpr", str(file_error))
        self.assertIn("not found", str(file_error).lower())
        
        # Permission error should mention the operation and file
        perm_error = GPRFilePermissionError("/protected/file.gpr", "write")
        self.assertIn("write", str(perm_error))
        self.assertIn("/protected/file.gpr", str(perm_error))
        self.assertIn("permission", str(perm_error).lower())
        
        # Format error should list supported formats
        format_error = GPRUnsupportedFormatError("xyz", ["gpr", "dng", "raw"])
        self.assertIn("xyz", str(format_error))
        self.assertIn("gpr, dng, raw", str(format_error))
        
        # Parameter error should mention the parameter name
        param_error = GPRParameterError("Invalid width", "input_width")
        self.assertTrue(
            "input_width" in str(param_error) or "width" in str(param_error).lower(),
            f"Expected parameter information in: {param_error}"
        )
    
    def test_error_cleanup_pattern(self):
        """Demonstrate proper error handling and cleanup pattern."""
        
        class ResourceManager:
            """Simulates resource management in C++ layer."""
            
            def __init__(self):
                self.resources = []
                self.cleanup_called = False
            
            def allocate_resource(self, name):
                if name == "fail":
                    raise GPRMemoryError(f"Failed to allocate resource: {name}")
                self.resources.append(name)
            
            def cleanup(self):
                self.cleanup_called = True
                self.resources.clear()
        
        def simulate_operation_with_cleanup():
            """Simulates a C++ operation that requires cleanup on error."""
            manager = ResourceManager()
            try:
                manager.allocate_resource("buffer1")
                manager.allocate_resource("buffer2")
                manager.allocate_resource("fail")  # This will throw
                return manager
            except GPRError:
                manager.cleanup()  # Ensure cleanup on error
                raise
        
        # Test that cleanup happens even when error occurs
        with self.assertRaises(GPRMemoryError):
            simulate_operation_with_cleanup()
        
        # In a real implementation, we would verify that C++ destructors
        # and cleanup code are called properly through RAII patterns


if __name__ == '__main__':
    unittest.main()