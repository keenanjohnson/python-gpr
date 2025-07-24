"""
Basic unit tests for python-gpr core functionality.

This test module uses unittest (built into Python) to test basic functionality
that is already implemented without requiring external dependencies or the 
C++ bindings to be fully working.
"""

import unittest
import os
import sys
import tempfile
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import python_gpr
from python_gpr.core import GPRImage, get_gpr_info
from python_gpr.metadata import GPRMetadata, extract_exif, extract_gpr_info


class TestPythonGPRBasic(unittest.TestCase):
    """Test basic python-gpr functionality."""
    
    def test_module_import(self):
        """Test that the python_gpr module can be imported."""
        self.assertIsNotNone(python_gpr)
        
    def test_version_info(self):
        """Test that version information is available."""
        self.assertTrue(hasattr(python_gpr, '__version__'))
        self.assertIsInstance(python_gpr.__version__, str)
        self.assertTrue(len(python_gpr.__version__) > 0)
        
    def test_author_info(self):
        """Test that author information is available."""
        self.assertTrue(hasattr(python_gpr, '__author__'))
        self.assertEqual(python_gpr.__author__, "Keenan Johnson")
        
        self.assertTrue(hasattr(python_gpr, '__email__'))
        self.assertEqual(python_gpr.__email__, "keenan.johnson@gmail.com")
        
    def test_description_info(self):
        """Test that description information is available."""
        self.assertTrue(hasattr(python_gpr, '__description__'))
        self.assertIn("GPR", python_gpr.__description__)


class TestGPRImage(unittest.TestCase):
    """Test GPRImage class basic functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.gpr')
        self.temp_file.write(b'dummy content')
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_gpr_image_init_with_existing_file(self):
        """Test GPRImage initialization with existing file."""
        # Should not raise an exception for existing file
        gpr_img = GPRImage(self.temp_file.name)
        self.assertEqual(gpr_img.filepath, self.temp_file.name)
        
    def test_gpr_image_init_with_nonexistent_file(self):
        """Test GPRImage initialization with non-existent file."""
        non_existent_path = "/path/that/does/not/exist.gpr"
        
        with self.assertRaises(FileNotFoundError) as context:
            GPRImage(non_existent_path)
            
        self.assertIn("GPR file not found", str(context.exception))
        self.assertIn(non_existent_path, str(context.exception))
        
    def test_gpr_image_properties_not_implemented(self):
        """Test that unimplemented properties raise NotImplementedError."""
        gpr_img = GPRImage(self.temp_file.name)
        
        with self.assertRaises(NotImplementedError):
            _ = gpr_img.width
            
        with self.assertRaises(NotImplementedError):
            _ = gpr_img.height
            
        with self.assertRaises(NotImplementedError):
            _ = gpr_img.dimensions
            
    def test_gpr_image_conversion_methods_not_implemented(self):
        """Test that conversion methods raise NotImplementedError."""
        gpr_img = GPRImage(self.temp_file.name)
        
        with self.assertRaises(NotImplementedError):
            gpr_img.to_dng("output.dng")
            
        with self.assertRaises(NotImplementedError):
            gpr_img.to_raw("output.raw")


class TestGPRInfo(unittest.TestCase):
    """Test get_gpr_info function."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.gpr')
        self.temp_file.write(b'dummy content')
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
            
    def test_get_gpr_info_with_existing_file(self):
        """Test get_gpr_info with existing file."""
        # Should raise NotImplementedError but not FileNotFoundError
        with self.assertRaises(NotImplementedError):
            get_gpr_info(self.temp_file.name)
            
    def test_get_gpr_info_with_nonexistent_file(self):
        """Test get_gpr_info with non-existent file."""
        non_existent_path = "/path/that/does/not/exist.gpr"
        
        with self.assertRaises(FileNotFoundError) as context:
            get_gpr_info(non_existent_path)
            
        self.assertIn("File not found", str(context.exception))


class TestGPRMetadata(unittest.TestCase):
    """Test GPRMetadata class basic functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.gpr')
        self.temp_file.write(b'dummy content')
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_gpr_metadata_init_with_existing_file(self):
        """Test GPRMetadata initialization with existing file."""
        # Should not raise an exception for existing file
        metadata = GPRMetadata(self.temp_file.name)
        self.assertEqual(metadata.filepath, self.temp_file.name)
        
    def test_gpr_metadata_init_with_nonexistent_file(self):
        """Test GPRMetadata initialization with non-existent file."""
        non_existent_path = "/path/that/does/not/exist.gpr"
        
        with self.assertRaises(FileNotFoundError) as context:
            GPRMetadata(non_existent_path)
            
        self.assertIn("GPR file not found", str(context.exception))
        
    def test_metadata_properties_implemented(self):
        """Test that metadata properties are now implemented and return values."""
        metadata = GPRMetadata(self.temp_file.name)
        
        # Properties should now return values, not raise NotImplementedError
        camera_model = metadata.camera_model
        self.assertIsInstance(camera_model, str)
        
        iso_speed = metadata.iso_speed
        self.assertIsInstance(iso_speed, int)
        
        exposure_time = metadata.exposure_time
        self.assertIsInstance(exposure_time, float)
        
        f_number = metadata.f_number
        self.assertIsInstance(f_number, float)


class TestMetadataFunctions(unittest.TestCase):
    """Test metadata utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.gpr')
        self.temp_file.write(b'dummy content')
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
            
    def test_extract_exif_with_existing_file(self):
        """Test extract_exif with existing file."""
        # Should now return metadata dictionary, not raise NotImplementedError
        result = extract_exif(self.temp_file.name)
        self.assertIsInstance(result, dict)
        # Check that some expected EXIF fields are present
        self.assertIn("camera_make", result)
        self.assertIn("camera_model", result)
            
    def test_extract_exif_with_nonexistent_file(self):
        """Test extract_exif with non-existent file."""
        non_existent_path = "/path/that/does/not/exist.jpg"
        
        with self.assertRaises(FileNotFoundError) as context:
            extract_exif(non_existent_path)
            
        self.assertIn("File not found", str(context.exception))
        
    def test_extract_gpr_info_with_existing_file(self):
        """Test extract_gpr_info with existing file."""
        # Should now return GPR metadata dictionary, not raise NotImplementedError
        result = extract_gpr_info(self.temp_file.name)
        self.assertIsInstance(result, dict)
        # Check that some expected GPR fields are present
        self.assertIn("input_width", result)
        self.assertIn("input_height", result)
            
    def test_extract_gpr_info_with_nonexistent_file(self):
        """Test extract_gpr_info with non-existent file."""
        non_existent_path = "/path/that/does/not/exist.gpr"
        
        with self.assertRaises(FileNotFoundError) as context:
            extract_gpr_info(non_existent_path)
            
        self.assertIn("GPR file not found", str(context.exception))


if __name__ == '__main__':
    unittest.main()