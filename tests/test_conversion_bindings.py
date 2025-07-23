"""
Test the GPR conversion function bindings.

This test module verifies that the conversion functions are properly bound
and can handle errors correctly.
"""

import unittest
import os
import tempfile
from pathlib import Path

# Try to import the conversion module
try:
    from python_gpr.conversion import (
        convert_gpr_to_dng,
        convert_dng_to_gpr,
        convert_gpr_to_raw,
        convert_dng_to_dng,
        GPRParameters
    )
    CONVERSION_AVAILABLE = True
except ImportError:
    CONVERSION_AVAILABLE = False


class TestConversionBindings(unittest.TestCase):
    """Test the conversion function bindings."""
    
    def setUp(self):
        """Set up test environment."""
        if not CONVERSION_AVAILABLE:
            self.skipTest("Conversion module not available")
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: os.rmdir(self.temp_dir) if os.path.exists(self.temp_dir) else None)
    
    def test_gpr_to_dng_file_not_found(self):
        """Test GPR to DNG conversion with missing input file."""
        input_path = os.path.join(self.temp_dir, "nonexistent.gpr")
        output_path = os.path.join(self.temp_dir, "output.dng")
        
        with self.assertRaises(FileNotFoundError):
            convert_gpr_to_dng(input_path, output_path)
    
    def test_dng_to_gpr_file_not_found(self):
        """Test DNG to GPR conversion with missing input file."""
        input_path = os.path.join(self.temp_dir, "nonexistent.dng")
        output_path = os.path.join(self.temp_dir, "output.gpr")
        
        with self.assertRaises(FileNotFoundError):
            convert_dng_to_gpr(input_path, output_path)
    
    def test_gpr_to_raw_file_not_found(self):
        """Test GPR to RAW conversion with missing input file."""
        input_path = os.path.join(self.temp_dir, "nonexistent.gpr")
        output_path = os.path.join(self.temp_dir, "output.raw")
        
        with self.assertRaises(FileNotFoundError):
            convert_gpr_to_raw(input_path, output_path)
    
    def test_dng_to_dng_file_not_found(self):
        """Test DNG to DNG conversion with missing input file."""
        input_path = os.path.join(self.temp_dir, "nonexistent.dng")
        output_path = os.path.join(self.temp_dir, "output.dng")
        
        with self.assertRaises(FileNotFoundError):
            convert_dng_to_dng(input_path, output_path)
    
    def test_gpr_to_dng_with_dummy_file(self):
        """Test GPR to DNG conversion with a dummy file (should fail conversion)."""
        # Create a dummy input file
        input_path = os.path.join(self.temp_dir, "dummy.gpr")
        output_path = os.path.join(self.temp_dir, "output.dng")
        
        with open(input_path, 'wb') as f:
            f.write(b"dummy data")
        
        # Should raise ValueError due to VC5 encoder not being available
        with self.assertRaises(ValueError) as cm:
            convert_gpr_to_dng(input_path, output_path)
        
        self.assertIn("VC5", str(cm.exception))
    
    def test_dng_to_gpr_with_dummy_file(self):
        """Test DNG to GPR conversion with a dummy file (should fail conversion)."""
        # Create a dummy input file
        input_path = os.path.join(self.temp_dir, "dummy.dng")
        output_path = os.path.join(self.temp_dir, "output.gpr")
        
        with open(input_path, 'wb') as f:
            f.write(b"dummy data")
        
        # Should raise ValueError due to VC5 encoder not being available
        with self.assertRaises(ValueError) as cm:
            convert_dng_to_gpr(input_path, output_path)
        
        self.assertIn("VC5", str(cm.exception))
    
    def test_gpr_to_raw_with_dummy_file(self):
        """Test GPR to RAW conversion with a dummy file (should fail conversion)."""
        # Create a dummy input file
        input_path = os.path.join(self.temp_dir, "dummy.dng")
        output_path = os.path.join(self.temp_dir, "output.raw")
        
        with open(input_path, 'wb') as f:
            f.write(b"dummy data")
        
        # Should raise ValueError due to invalid file format
        with self.assertRaises(ValueError) as cm:
            convert_gpr_to_raw(input_path, output_path)
        
        # The error should indicate conversion failure
        self.assertIn("conversion failed", str(cm.exception).lower())
    
    def test_dng_to_dng_with_dummy_file(self):
        """Test DNG to DNG conversion with a dummy file (should fail conversion)."""
        # Create a dummy input file
        input_path = os.path.join(self.temp_dir, "dummy.dng")
        output_path = os.path.join(self.temp_dir, "output.dng")
        
        with open(input_path, 'wb') as f:
            f.write(b"dummy data")
        
        # Should raise ValueError due to invalid file format
        with self.assertRaises(ValueError) as cm:
            convert_dng_to_dng(input_path, output_path)
        
        # The error should indicate conversion failure
        self.assertIn("conversion failed", str(cm.exception).lower())
    
    def test_parameters_object(self):
        """Test that GPRParameters can be created."""
        params = GPRParameters()
        self.assertIsInstance(params, GPRParameters)
        
        # Test with custom parameters
        params = GPRParameters(quality=10, subband_count=3)
        self.assertEqual(params.quality, 10)
        self.assertEqual(params.subband_count, 3)
        
        # Test to_dict method
        param_dict = params.to_dict()
        self.assertIsInstance(param_dict, dict)
        self.assertEqual(param_dict['quality'], 10)
        self.assertEqual(param_dict['subband_count'], 3)


class TestConversionModuleImport(unittest.TestCase):
    """Test that the conversion module can be imported even without bindings."""
    
    def test_module_import(self):
        """Test that the module can be imported."""
        import python_gpr.conversion
        self.assertTrue(hasattr(python_gpr.conversion, 'convert_gpr_to_dng'))
        self.assertTrue(hasattr(python_gpr.conversion, 'convert_dng_to_gpr'))
        self.assertTrue(hasattr(python_gpr.conversion, 'convert_gpr_to_raw'))
        self.assertTrue(hasattr(python_gpr.conversion, 'GPRParameters'))


if __name__ == '__main__':
    unittest.main()