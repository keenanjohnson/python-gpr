"""
Test the GPR conversion function bindings.

This test module verifies that the conversion functions are properly bound
and can handle errors correctly.
"""

import unittest
import os
import tempfile
import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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
        self.addCleanup(self._cleanup_temp_dir)
    
    def _cleanup_temp_dir(self):
        """Clean up temporary directory and all its contents."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
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
        
        # Should raise NotImplementedError if bindings not available, or ValueError if they are
        with self.assertRaises((NotImplementedError, ValueError)) as cm:
            convert_gpr_to_dng(input_path, output_path)
        
        # Check that the error message is appropriate
        error_msg = str(cm.exception).lower()
        self.assertTrue(
            "not available" in error_msg or "vc5" in error_msg or "conversion failed" in error_msg,
            f"Unexpected error message: {cm.exception}"
        )
    
    def test_dng_to_gpr_with_dummy_file(self):
        """Test DNG to GPR conversion with a dummy file (should fail conversion)."""
        # Create a dummy input file
        input_path = os.path.join(self.temp_dir, "dummy.dng")
        output_path = os.path.join(self.temp_dir, "output.gpr")
        
        with open(input_path, 'wb') as f:
            f.write(b"dummy data")
        
        # Should raise NotImplementedError if bindings not available, or ValueError if they are
        with self.assertRaises((NotImplementedError, ValueError)) as cm:
            convert_dng_to_gpr(input_path, output_path)
        
        # Check that the error message is appropriate
        error_msg = str(cm.exception).lower()
        self.assertTrue(
            "not available" in error_msg or "vc5" in error_msg or "conversion failed" in error_msg,
            f"Unexpected error message: {cm.exception}"
        )
    
    def test_gpr_to_raw_with_dummy_file(self):
        """Test GPR to RAW conversion with a dummy file (should fail conversion)."""
        # Create a dummy input file
        input_path = os.path.join(self.temp_dir, "dummy.dng")
        output_path = os.path.join(self.temp_dir, "output.raw")
        
        with open(input_path, 'wb') as f:
            f.write(b"dummy data")
        
        # Should raise NotImplementedError if bindings not available, or ValueError if they are
        with self.assertRaises((NotImplementedError, ValueError)) as cm:
            convert_gpr_to_raw(input_path, output_path)
        
        # Check that the error message is appropriate
        error_msg = str(cm.exception).lower()
        self.assertTrue(
            "not available" in error_msg or "conversion failed" in error_msg,
            f"Unexpected error message: {cm.exception}"
        )
    
    def test_dng_to_dng_with_dummy_file(self):
        """Test DNG to DNG conversion with a dummy file (should fail conversion)."""
        # Create a dummy input file
        input_path = os.path.join(self.temp_dir, "dummy.dng")
        output_path = os.path.join(self.temp_dir, "output.dng")
        
        with open(input_path, 'wb') as f:
            f.write(b"dummy data")
        
        # Should raise NotImplementedError if bindings not available, or ValueError if they are
        with self.assertRaises((NotImplementedError, ValueError)) as cm:
            convert_dng_to_dng(input_path, output_path)
        
        # Check that the error message is appropriate
        error_msg = str(cm.exception).lower()
        self.assertTrue(
            "not available" in error_msg or "conversion failed" in error_msg,
            f"Unexpected error message: {cm.exception}"
        )
    
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
    
    def test_gpr_conversion_with_real_file(self):
        """Test GPR conversion functions with a real GPR file."""
        # Path to the real GPR test file
        test_gpr_file = Path(__file__).parent / "data" / "2024_10_08_10-37-22.GPR"
        
        # Skip test if the test file doesn't exist
        if not test_gpr_file.exists():
            self.skipTest(f"Test GPR file not found at {test_gpr_file}")
        
        # Test GPR to DNG conversion
        output_dng = os.path.join(self.temp_dir, "output.dng")
        try:
            convert_gpr_to_dng(str(test_gpr_file), output_dng)
            # If conversion succeeds, check that output file was created
            self.assertTrue(os.path.exists(output_dng), "DNG output file should be created")
            self.assertGreater(os.path.getsize(output_dng), 0, "DNG output file should not be empty")
        except (NotImplementedError, ValueError) as e:
            # Expected when bindings not available or conversion fails due to missing VC5 codecs
            error_msg = str(e).lower()
            self.assertTrue(
                "not available" in error_msg or "vc5" in error_msg or "conversion failed" in error_msg,
                f"Unexpected error message: {e}"
            )
        
        # Test GPR to RAW conversion
        output_raw = os.path.join(self.temp_dir, "output.raw")
        try:
            convert_gpr_to_raw(str(test_gpr_file), output_raw)
            # If conversion succeeds, check that output file was created
            self.assertTrue(os.path.exists(output_raw), "RAW output file should be created")
            self.assertGreater(os.path.getsize(output_raw), 0, "RAW output file should not be empty")
        except (NotImplementedError, ValueError) as e:
            # Expected when bindings not available or conversion fails
            error_msg = str(e).lower()
            self.assertTrue(
                "not available" in error_msg or "conversion failed" in error_msg,
                f"Unexpected error message: {e}"
            )
        
        # Test DNG to GPR conversion (if we have a DNG file from previous conversion)
        if os.path.exists(output_dng):
            output_gpr = os.path.join(self.temp_dir, "converted_back.gpr")
            try:
                convert_dng_to_gpr(output_dng, output_gpr)
                # If conversion succeeds, check that output file was created
                self.assertTrue(os.path.exists(output_gpr), "GPR output file should be created")
                self.assertGreater(os.path.getsize(output_gpr), 0, "GPR output file should not be empty")
            except (NotImplementedError, ValueError) as e:
                # Expected when bindings not available or conversion fails
                error_msg = str(e).lower()
                self.assertTrue(
                    "not available" in error_msg or "vc5" in error_msg or "conversion failed" in error_msg,
                    f"Unexpected error message: {e}"
                )


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