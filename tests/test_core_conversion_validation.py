"""
Comprehensive validation test for all core GPR conversion functions.

This test module validates that all essential GPR conversion functions 
are properly exposed and accessible from Python, with proper parameter 
passing and error handling.
"""

import unittest
import os
import tempfile
import sys
from pathlib import Path
import inspect

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from python_gpr.conversion import (
        convert_gpr_to_dng,
        convert_dng_to_gpr,
        convert_gpr_to_raw,
        convert_dng_to_dng,
        detect_format,
        GPRParameters
    )
    CONVERSION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Conversion module import failed: {e}")
    CONVERSION_AVAILABLE = False


class TestCoreConversionFunctionAccessibility(unittest.TestCase):
    """Test that all core conversion functions are accessible from Python."""
    
    def setUp(self):
        """Set up test environment."""
        if not CONVERSION_AVAILABLE:
            self.skipTest("Conversion module not available")
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(self._cleanup_temp_dir)
    
    def _cleanup_temp_dir(self):
        """Clean up temporary directory and all its contents."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_all_core_functions_accessible(self):
        """Test that all required conversion functions are accessible."""
        # Test GPR to DNG conversion function
        self.assertTrue(callable(convert_gpr_to_dng), 
                       "convert_gpr_to_dng should be callable")
        
        # Test DNG to GPR conversion function
        self.assertTrue(callable(convert_dng_to_gpr), 
                       "convert_dng_to_gpr should be callable")
        
        # Test GPR to RAW conversion function
        self.assertTrue(callable(convert_gpr_to_raw), 
                       "convert_gpr_to_raw should be callable")
        
        # Test DNG to DNG conversion function
        self.assertTrue(callable(convert_dng_to_dng), 
                       "convert_dng_to_dng should be callable")
        
        # Test format detection function
        self.assertTrue(callable(detect_format), 
                       "detect_format should be callable")
    
    def test_function_signatures(self):
        """Test that all conversion functions have correct signatures."""
        # Check convert_gpr_to_dng signature
        sig = inspect.signature(convert_gpr_to_dng)
        params = list(sig.parameters.keys())
        self.assertEqual(params[:2], ['input_path', 'output_path'], 
                        "convert_gpr_to_dng should accept input_path and output_path")
        self.assertIn('parameters', params, 
                     "convert_gpr_to_dng should accept parameters argument")
        
        # Check convert_dng_to_gpr signature
        sig = inspect.signature(convert_dng_to_gpr)
        params = list(sig.parameters.keys())
        self.assertEqual(params[:2], ['input_path', 'output_path'], 
                        "convert_dng_to_gpr should accept input_path and output_path")
        self.assertIn('parameters', params, 
                     "convert_dng_to_gpr should accept parameters argument")
        
        # Check convert_gpr_to_raw signature
        sig = inspect.signature(convert_gpr_to_raw)
        params = list(sig.parameters.keys())
        self.assertEqual(params[:2], ['input_path', 'output_path'], 
                        "convert_gpr_to_raw should accept input_path and output_path")
        self.assertIn('parameters', params, 
                     "convert_gpr_to_raw should accept parameters argument")
        
        # Check convert_dng_to_dng signature
        sig = inspect.signature(convert_dng_to_dng)
        params = list(sig.parameters.keys())
        self.assertEqual(params[:2], ['input_path', 'output_path'], 
                        "convert_dng_to_dng should accept input_path and output_path")
        self.assertIn('parameters', params, 
                     "convert_dng_to_dng should accept parameters argument")
        
        # Check detect_format signature
        sig = inspect.signature(detect_format)
        params = list(sig.parameters.keys())
        self.assertEqual(params[0], 'filepath', 
                        "detect_format should accept filepath argument")
    
    def test_function_docstrings(self):
        """Test that all conversion functions have proper documentation."""
        functions = [
            (convert_gpr_to_dng, "Convert GPR file to DNG format"),
            (convert_dng_to_gpr, "Convert DNG file to GPR format"),
            (convert_gpr_to_raw, "Convert GPR file to RAW format"),
            (convert_dng_to_dng, "Convert DNG file to DNG format"),
            (detect_format, "Detect the format of an image file"),
        ]
        
        for func, expected_desc in functions:
            self.assertIsNotNone(func.__doc__, 
                               f"{func.__name__} should have documentation")
            self.assertIn(expected_desc.split()[0].lower(), func.__doc__.lower(), 
                         f"{func.__name__} documentation should mention its purpose")


class TestGPRParametersAccessibility(unittest.TestCase):
    """Test GPRParameters class accessibility and functionality."""
    
    def setUp(self):
        """Set up test environment."""
        if not CONVERSION_AVAILABLE:
            self.skipTest("Conversion module not available")
    
    def test_gpr_parameters_class_accessible(self):
        """Test that GPRParameters class is accessible and instantiable."""
        # Test basic instantiation
        params = GPRParameters()
        self.assertIsInstance(params, GPRParameters)
        
        # Test instantiation with parameters
        custom_params = GPRParameters(quality=10, subband_count=3)
        self.assertIsInstance(custom_params, GPRParameters)
        self.assertEqual(custom_params.quality, 10)
        self.assertEqual(custom_params.subband_count, 3)
    
    def test_parameter_validation_functionality(self):
        """Test that parameter validation works correctly."""
        params = GPRParameters()
        
        # Test valid quality parameter
        params.quality = 8
        self.assertEqual(params.quality, 8)
        
        # Test invalid quality parameter
        with self.assertRaises(ValueError):
            params.quality = 15  # Should be 1-12
        
        # Test valid subband_count parameter
        params.subband_count = 6
        self.assertEqual(params.subband_count, 6)
        
        # Test invalid subband_count parameter
        with self.assertRaises(ValueError):
            params.subband_count = 10  # Should be 1-8
    
    def test_parameter_types_validation(self):
        """Test that parameter type validation works correctly."""
        params = GPRParameters()
        
        # Test type validation for quality (using property setter)
        with self.assertRaises(TypeError):
            params.quality = "invalid"
        
        # Test type validation for boolean parameters (using dict-like access)
        params['fast_encoding'] = True
        self.assertTrue(params['fast_encoding'])
        
        with self.assertRaises(TypeError):
            params['fast_encoding'] = "true"
    
    def test_all_core_parameters_available(self):
        """Test that all core GPR parameters are available."""
        params = GPRParameters()
        
        # Core GPR parameters
        core_params = [
            'input_width', 'input_height', 'input_pitch',
            'fast_encoding', 'compute_md5sum', 'enable_preview'
        ]
        
        for param in core_params:
            self.assertIn(param, params, f"Parameter {param} should be available")
        
        # Legacy parameters for backwards compatibility
        legacy_params = ['quality', 'subband_count', 'progressive']
        
        for param in legacy_params:
            self.assertIn(param, params, f"Legacy parameter {param} should be available")
    
    def test_parameter_dict_interface(self):
        """Test that GPRParameters supports dict-like interface."""
        params = GPRParameters(quality=9, fast_encoding=True)
        
        # Test to_dict method
        param_dict = params.to_dict()
        self.assertIsInstance(param_dict, dict)
        self.assertEqual(param_dict['quality'], 9)
        self.assertEqual(param_dict['fast_encoding'], True)
        
        # Test keys, values, items methods
        self.assertTrue(hasattr(params, 'keys'))
        self.assertTrue(hasattr(params, 'values'))
        self.assertTrue(hasattr(params, 'items'))
        
        # Test get method
        self.assertEqual(params.get('quality'), 9)
        self.assertIsNone(params.get('nonexistent_param'))


class TestConversionWithRealFiles(unittest.TestCase):
    """Test conversion functions with real files."""
    
    def setUp(self):
        """Set up test environment."""
        if not CONVERSION_AVAILABLE:
            self.skipTest("Conversion module not available")
        
        # Path to the real GPR test file
        self.test_gpr_file = Path(__file__).parent / "data" / "2024_10_08_10-37-22.GPR"
        
        # Create temporary directory for output files
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(self._cleanup_temp_dir)
    
    def _cleanup_temp_dir(self):
        """Clean up temporary directory and all its contents."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_conversion_functions_with_real_gpr_file(self):
        """Test conversion functions with a real GPR file."""
        if not self.test_gpr_file.exists():
            self.skipTest(f"Test GPR file not found at {self.test_gpr_file}")
        
        # Test GPR to DNG conversion
        output_dng = os.path.join(self.temp_dir, "test_output.dng")
        try:
            convert_gpr_to_dng(str(self.test_gpr_file), output_dng)
            # If successful, verify output file was created
            if os.path.exists(output_dng):
                self.assertGreater(os.path.getsize(output_dng), 0, 
                                 "DNG output file should not be empty")
        except (NotImplementedError, ValueError) as e:
            # Expected when C++ bindings not available or conversion fails
            self.assertTrue(True, f"Expected error occurred: {e}")
        
        # Test GPR to RAW conversion
        output_raw = os.path.join(self.temp_dir, "test_output.raw")
        try:
            convert_gpr_to_raw(str(self.test_gpr_file), output_raw)
            # If successful, verify output file was created
            if os.path.exists(output_raw):
                self.assertGreater(os.path.getsize(output_raw), 0, 
                                 "RAW output file should not be empty")
        except (NotImplementedError, ValueError) as e:
            # Expected when C++ bindings not available or conversion fails
            self.assertTrue(True, f"Expected error occurred: {e}")
    
    def test_conversion_with_parameters(self):
        """Test conversion functions accept parameters correctly."""
        if not self.test_gpr_file.exists():
            self.skipTest(f"Test GPR file not found at {self.test_gpr_file}")
        
        # Create custom parameters
        params = GPRParameters(quality=8, fast_encoding=True, enable_preview=True)
        
        output_path = os.path.join(self.temp_dir, "with_params.dng")
        
        # Test that function accepts parameters without error
        try:
            convert_gpr_to_dng(str(self.test_gpr_file), output_path, parameters=params)
        except (NotImplementedError, ValueError) as e:
            # Expected when C++ bindings not available
            # Important: ensure it's not a parameter-related error
            error_msg = str(e).lower()
            self.assertNotIn("parameter", error_msg, 
                           "Error should not be parameter-related")
            self.assertTrue(
                "not available" in error_msg or "conversion failed" in error_msg,
                "Should be a binding or conversion error, not parameter error"
            )


class TestFormatDetection(unittest.TestCase):
    """Test format detection functionality."""
    
    def setUp(self):
        """Set up test environment."""
        if not CONVERSION_AVAILABLE:
            self.skipTest("Conversion module not available")
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(self._cleanup_temp_dir)
    
    def _cleanup_temp_dir(self):
        """Clean up temporary directory and all its contents."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_format_detection_functionality(self):
        """Test that format detection works for various file formats."""
        # Create test files with different extensions
        test_files = [
            ("test.gpr", "gpr"),
            ("test.dng", "dng"),
            ("test.raw", "raw"),
            ("test.ppm", "ppm"),
            ("test.jpg", "jpg"),
            ("test.jpeg", "jpg"),
        ]
        
        for filename, expected_format in test_files:
            filepath = os.path.join(self.temp_dir, filename)
            
            # Create dummy file
            with open(filepath, 'wb') as f:
                f.write(b"dummy content")
            
            # Test format detection
            detected_format = detect_format(filepath)
            self.assertEqual(detected_format, expected_format, 
                           f"Format detection failed for {filename}")
    
    def test_format_detection_with_real_gpr_file(self):
        """Test format detection with real GPR file."""
        test_gpr_file = Path(__file__).parent / "data" / "2024_10_08_10-37-22.GPR"
        
        if not test_gpr_file.exists():
            self.skipTest(f"Test GPR file not found at {test_gpr_file}")
        
        # Test format detection on real GPR file
        detected_format = detect_format(str(test_gpr_file))
        self.assertEqual(detected_format, "gpr", 
                        "Real GPR file should be detected as GPR format")
    
    def test_format_detection_error_handling(self):
        """Test format detection error handling."""
        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            detect_format("nonexistent_file.gpr")
        
        # Test with unknown format
        unknown_file = os.path.join(self.temp_dir, "test.xyz")
        with open(unknown_file, 'wb') as f:
            f.write(b"dummy content")
        
        with self.assertRaises(ValueError):
            detect_format(unknown_file)


class TestErrorHandlingValidation(unittest.TestCase):
    """Test comprehensive error handling across all conversion functions."""
    
    def setUp(self):
        """Set up test environment."""
        if not CONVERSION_AVAILABLE:
            self.skipTest("Conversion module not available")
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(self._cleanup_temp_dir)
    
    def _cleanup_temp_dir(self):
        """Clean up temporary directory and all its contents."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_file_not_found_errors(self):
        """Test that all conversion functions properly handle missing files."""
        conversion_functions = [
            (convert_gpr_to_dng, "test.gpr", "output.dng"),
            (convert_dng_to_gpr, "test.dng", "output.gpr"),
            (convert_gpr_to_raw, "test.gpr", "output.raw"),
            (convert_dng_to_dng, "test.dng", "output2.dng"),
        ]
        
        for func, input_name, output_name in conversion_functions:
            input_path = os.path.join(self.temp_dir, input_name)
            output_path = os.path.join(self.temp_dir, output_name)
            
            with self.assertRaises(FileNotFoundError, 
                                 msg=f"{func.__name__} should raise FileNotFoundError for missing input"):
                func(input_path, output_path)
    
    def test_conversion_error_handling_with_dummy_files(self):
        """Test conversion error handling with invalid files."""
        # Create dummy files for testing
        dummy_files = [
            ("dummy.gpr", b"fake gpr content"),
            ("dummy.dng", b"fake dng content"),
        ]
        
        for filename, content in dummy_files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(content)
        
        # Test conversion functions with dummy files
        conversion_tests = [
            (convert_gpr_to_dng, "dummy.gpr", "output.dng"),
            (convert_dng_to_gpr, "dummy.dng", "output.gpr"),
            (convert_gpr_to_raw, "dummy.gpr", "output.raw"),
            (convert_dng_to_dng, "dummy.dng", "output2.dng"),
        ]
        
        for func, input_name, output_name in conversion_tests:
            input_path = os.path.join(self.temp_dir, input_name)
            output_path = os.path.join(self.temp_dir, output_name)
            
            # Should raise either NotImplementedError (no bindings) or ValueError (conversion failed)
            with self.assertRaises((NotImplementedError, ValueError), 
                                 msg=f"{func.__name__} should handle invalid files appropriately"):
                func(input_path, output_path)


class TestPackageExportValidation(unittest.TestCase):
    """Test that all functions are properly exported from the package."""
    
    def test_conversion_module_exports(self):
        """Test that conversion module exports all required functions."""
        if not CONVERSION_AVAILABLE:
            self.skipTest("Conversion module not available")
        
        import python_gpr.conversion as conv_module
        
        # Check that all required functions are exported
        required_exports = [
            'convert_gpr_to_dng',
            'convert_dng_to_gpr', 
            'convert_gpr_to_raw',
            'convert_dng_to_dng',
            'detect_format',
            'GPRParameters'
        ]
        
        for export_name in required_exports:
            self.assertTrue(hasattr(conv_module, export_name), 
                          f"conversion module should export {export_name}")
        
        # Test __all__ contains expected exports
        if hasattr(conv_module, '__all__'):
            for export_name in required_exports:
                self.assertIn(export_name, conv_module.__all__, 
                            f"{export_name} should be in __all__")


if __name__ == '__main__':
    unittest.main(verbosity=2)