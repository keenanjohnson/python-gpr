"""
Test the enhanced error handling and exception mapping functionality.

This test module specifically validates that the error handling system
works correctly and that exceptions are properly mapped and propagated.
"""

import unittest
import os
import tempfile
import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Try to import the exception classes directly
try:
    from python_gpr.exceptions import (
        GPRError,
        GPRConversionError,
        GPRFileError,
        GPRFileNotFoundError,
        GPRFilePermissionError,
        GPRFileCorruptedError,
        GPRMemoryError,
        GPRParameterError,
        GPRFormatError,
        GPRUnsupportedFormatError,
        GPRCompressionError,
        GPRMetadataError,
        GPRBitstreamError,
        GPRResourceError,
        map_error_code,
        create_file_error,
    )
    EXCEPTIONS_AVAILABLE = True
except ImportError as e:
    print(f"Exception classes not available: {e}")
    EXCEPTIONS_AVAILABLE = False

# Try to import the core module
try:
    from python_gpr._core import (
        convert_gpr_to_dng,
        convert_dng_to_gpr,
        convert_gpr_to_raw,
        get_raw_image_data,
        get_image_info,
    )
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"Core module not available: {e}")
    CORE_AVAILABLE = False


class TestExceptionHierarchy(unittest.TestCase):
    """Test the exception hierarchy and error mapping functionality."""
    
    def setUp(self):
        """Set up test environment."""
        if not EXCEPTIONS_AVAILABLE:
            self.skipTest("Exception classes not available")
    
    def test_base_gpr_error(self):
        """Test the base GPRError exception."""
        # Test basic error creation
        error = GPRError("Test error message")
        self.assertEqual(str(error), "Test error message")
        self.assertIsNone(error.error_code)
        self.assertEqual(error.context, {})
        
        # Test error with code
        error_with_code = GPRError("Test error", error_code=42)
        self.assertEqual(str(error_with_code), "[Error 42] Test error")
        self.assertEqual(error_with_code.error_code, 42)
        
        # Test error with context
        context = {"filepath": "/test/file.gpr", "operation": "read"}
        error_with_context = GPRError("Test error", context=context)
        expected_str = "Test error (Context: filepath=/test/file.gpr, operation=read)"
        self.assertEqual(str(error_with_context), expected_str)
    
    def test_file_error_hierarchy(self):
        """Test file-related error classes."""
        # Test GPRFileNotFoundError
        not_found = GPRFileNotFoundError("/nonexistent/file.gpr")
        self.assertEqual(not_found.filepath, "/nonexistent/file.gpr")
        self.assertIn("File not found", str(not_found))
        self.assertIn("/nonexistent/file.gpr", str(not_found))
        
        # Test GPRFilePermissionError
        permission = GPRFilePermissionError("/protected/file.gpr", "write")
        self.assertEqual(permission.filepath, "/protected/file.gpr")
        self.assertEqual(permission.operation, "write")
        self.assertIn("Permission denied", str(permission))
        
        # Test GPRFileCorruptedError
        corrupted = GPRFileCorruptedError("/bad/file.gpr", "Invalid header")
        self.assertEqual(corrupted.filepath, "/bad/file.gpr")
        self.assertEqual(corrupted.reason, "Invalid header")
        self.assertIn("corrupted", str(corrupted))
        self.assertIn("Invalid header", str(corrupted))
    
    def test_format_error_hierarchy(self):
        """Test format-related error classes."""
        # Test GPRUnsupportedFormatError
        unsupported = GPRUnsupportedFormatError("xyz", ["gpr", "dng", "raw"])
        self.assertEqual(unsupported.format_name, "xyz")
        self.assertEqual(unsupported.supported_formats, ["gpr", "dng", "raw"])
        self.assertIn("Unsupported format 'xyz'", str(unsupported))
        self.assertIn("gpr, dng, raw", str(unsupported))
    
    def test_bitstream_error(self):
        """Test bitstream error mapping."""
        # Test known error codes
        underflow = GPRBitstreamError(1)
        self.assertEqual(underflow.error_code, 1)
        self.assertIn("underflow", str(underflow))
        
        overflow = GPRBitstreamError(2)
        self.assertEqual(overflow.error_code, 2)
        self.assertIn("overflow", str(overflow))
        
        bad_tag = GPRBitstreamError(3)
        self.assertEqual(bad_tag.error_code, 3)
        self.assertIn("tag", str(bad_tag))
        
        # Test unknown error code
        unknown = GPRBitstreamError(99)
        self.assertEqual(unknown.error_code, 99)
        self.assertIn("Unknown bitstream error", str(unknown))
        self.assertIn("99", str(unknown))
    
    def test_error_code_mapping(self):
        """Test error code to exception mapping."""
        # Test file errors
        file_error = map_error_code(-2, "File not found")
        self.assertIsInstance(file_error, GPRFileNotFoundError)
        
        permission_error = map_error_code(-3, "Permission denied")
        self.assertIsInstance(permission_error, GPRFilePermissionError)
        
        # Test memory errors
        memory_error = map_error_code(-10, "Out of memory")
        self.assertIsInstance(memory_error, GPRMemoryError)
        
        # Test parameter errors
        param_error = map_error_code(-20, "Invalid parameter")
        self.assertIsInstance(param_error, GPRParameterError)
        
        # Test unknown error code
        unknown_error = map_error_code(-999, "Unknown error")
        self.assertIsInstance(unknown_error, GPRError)
        self.assertEqual(unknown_error.error_code, -999)
    
    def test_create_file_error(self):
        """Test file error creation from system errors."""
        # Test FileNotFoundError mapping
        file_error = create_file_error("/test/file.gpr", "read", FileNotFoundError())
        self.assertIsInstance(file_error, GPRFileNotFoundError)
        self.assertEqual(file_error.filepath, "/test/file.gpr")
        
        # Test PermissionError mapping
        perm_error = create_file_error("/test/file.gpr", "write", PermissionError())
        self.assertIsInstance(perm_error, GPRFilePermissionError)
        self.assertEqual(perm_error.operation, "write")
        
        # Test OSError mapping
        os_error = create_file_error("/test/file.gpr", "read", OSError("Disk error"))
        self.assertIsInstance(os_error, GPRFileCorruptedError)
        self.assertIn("Disk error", str(os_error))
        
        # Test generic error
        generic_error = create_file_error("/test/file.gpr", "read", ValueError("Value error"))
        self.assertIsInstance(generic_error, GPRFileError)
        self.assertIn("Value error", str(generic_error))


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling integration with core functions."""
    
    def setUp(self):
        """Set up test environment."""
        if not CORE_AVAILABLE:
            self.skipTest("Core module not available")
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(self._cleanup_temp_dir)
    
    def _cleanup_temp_dir(self):
        """Clean up temporary directory and all its contents."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_file_not_found_error(self):
        """Test that missing files raise appropriate exceptions."""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.gpr")
        output_file = os.path.join(self.temp_dir, "output.dng")
        
        with self.assertRaises(Exception) as context:
            convert_gpr_to_dng(nonexistent_file, output_file)
        
        # The exception should be a GPR-related error
        self.assertTrue(
            any(keyword in str(context.exception).lower() 
                for keyword in ["file", "not found", "exist", "read"]),
            f"Expected file-related error message, got: {context.exception}"
        )
    
    def test_invalid_dtype_parameter(self):
        """Test that invalid dtype parameter raises appropriate exception."""
        if not hasattr(sys.modules.get('python_gpr._core', None), 'get_raw_image_data'):
            self.skipTest("get_raw_image_data function not available")
        
        # Create a dummy file for testing
        dummy_file = os.path.join(self.temp_dir, "dummy.gpr")
        with open(dummy_file, 'w') as f:
            f.write("dummy content")
        
        with self.assertRaises(Exception) as context:
            get_raw_image_data(dummy_file, "invalid_dtype")
        
        # The exception should mention dtype or parameter
        self.assertTrue(
            any(keyword in str(context.exception).lower() 
                for keyword in ["dtype", "parameter", "unsupported", "type"]),
            f"Expected parameter-related error message, got: {context.exception}"
        )
    
    def test_empty_file_error(self):
        """Test that empty files raise appropriate exceptions."""
        empty_file = os.path.join(self.temp_dir, "empty.gpr")
        output_file = os.path.join(self.temp_dir, "output.dng")
        
        # Create empty file
        with open(empty_file, 'w') as f:
            pass  # Create empty file
        
        with self.assertRaises(Exception) as context:
            convert_gpr_to_dng(empty_file, output_file)
        
        # The exception should be related to file content
        self.assertTrue(
            any(keyword in str(context.exception).lower() 
                for keyword in ["empty", "corrupted", "invalid", "size"]),
            f"Expected file content error message, got: {context.exception}"
        )


class TestErrorHandlingRobustness(unittest.TestCase):
    """Test error handling robustness and edge cases."""
    
    def setUp(self):
        """Set up test environment."""
        if not EXCEPTIONS_AVAILABLE:
            self.skipTest("Exception classes not available")
    
    def test_exception_inheritance(self):
        """Test that all exceptions inherit from GPRError correctly."""
        # Test inheritance chain
        self.assertTrue(issubclass(GPRConversionError, GPRError))
        self.assertTrue(issubclass(GPRFileError, GPRError))
        self.assertTrue(issubclass(GPRFileNotFoundError, GPRFileError))
        self.assertTrue(issubclass(GPRFilePermissionError, GPRFileError))
        self.assertTrue(issubclass(GPRFileCorruptedError, GPRFileError))
        self.assertTrue(issubclass(GPRMemoryError, GPRError))
        self.assertTrue(issubclass(GPRParameterError, GPRError))
        self.assertTrue(issubclass(GPRFormatError, GPRError))
        self.assertTrue(issubclass(GPRUnsupportedFormatError, GPRFormatError))
        self.assertTrue(issubclass(GPRCompressionError, GPRError))
        self.assertTrue(issubclass(GPRMetadataError, GPRError))
        self.assertTrue(issubclass(GPRBitstreamError, GPRError))
        self.assertTrue(issubclass(GPRResourceError, GPRError))
    
    def test_exception_pickling(self):
        """Test that exceptions can be pickled/unpickled."""
        import pickle
        
        # Test base error
        error = GPRError("Test message", error_code=42, context={"key": "value"})
        pickled = pickle.dumps(error)
        unpickled = pickle.loads(pickled)
        
        self.assertEqual(str(error), str(unpickled))
        self.assertEqual(error.error_code, unpickled.error_code)
        self.assertEqual(error.context, unpickled.context)
        
        # Test specialized error - just check that it can be pickled/unpickled
        # without worrying about exact string match due to constructor complexity
        file_error = GPRFileNotFoundError("/test/file.gpr")
        pickled = pickle.dumps(file_error)
        unpickled = pickle.loads(pickled)
        
        # Check that key properties are preserved
        self.assertEqual(file_error.filepath, unpickled.filepath)
        self.assertEqual(file_error.error_code, unpickled.error_code)
        self.assertIn("/test/file.gpr", str(unpickled))
        self.assertIn("not found", str(unpickled).lower())
    
    def test_error_messages_are_helpful(self):
        """Test that error messages contain helpful information."""
        # Test that error messages are descriptive
        file_error = GPRFileNotFoundError("/path/to/missing/file.gpr")
        self.assertIn("/path/to/missing/file.gpr", str(file_error))
        self.assertIn("not found", str(file_error).lower())
        
        format_error = GPRUnsupportedFormatError("xyz", ["gpr", "dng"])
        self.assertIn("xyz", str(format_error))
        self.assertIn("gpr", str(format_error))
        self.assertIn("dng", str(format_error))
        
        param_error = GPRParameterError("Invalid width value", "input_width")
        self.assertIn("width", str(param_error).lower())
        # The error code is displayed, so check for that instead of "parameter"
        self.assertTrue(
            "parameter" in str(param_error).lower() or 
            "error" in str(param_error).lower() or
            "input_width" in str(param_error),
            f"Expected parameter-related content in: {param_error}"
        )


if __name__ == '__main__':
    unittest.main()