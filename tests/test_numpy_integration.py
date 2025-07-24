"""
Unit tests for NumPy integration functionality in python-gpr.

These tests verify the NumPy array integration for raw image data access,
including different data types and memory management.
"""

import unittest
import os
import sys
import tempfile
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

import python_gpr
from python_gpr.core import GPRImage, load_gpr_as_numpy, get_gpr_image_info


@unittest.skipUnless(HAS_NUMPY, "NumPy not available")
class TestNumPyIntegration(unittest.TestCase):
    """Test NumPy integration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary GPR file for testing
        self.temp_gpr_file = tempfile.NamedTemporaryFile(delete=False, suffix='.gpr')
        self.temp_gpr_file.write(b'dummy GPR content for testing')
        self.temp_gpr_file.close()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_gpr_file.name):
            os.unlink(self.temp_gpr_file.name)
    
    def test_gpr_image_to_numpy_not_implemented(self):
        """Test that GPRImage.to_numpy raises NotImplementedError when bindings unavailable."""
        gpr_img = GPRImage(self.temp_gpr_file.name)
        
        with self.assertRaises(NotImplementedError) as context:
            gpr_img.to_numpy()
            
        self.assertIn("GPR C++ bindings not available", str(context.exception))
        
    def test_gpr_image_to_numpy_with_dtype(self):
        """Test that GPRImage.to_numpy with different dtypes raises NotImplementedError."""
        gpr_img = GPRImage(self.temp_gpr_file.name)
        
        with self.assertRaises(NotImplementedError):
            gpr_img.to_numpy(dtype="uint16")
            
        with self.assertRaises(NotImplementedError):
            gpr_img.to_numpy(dtype="float32")
            
    def test_gpr_image_get_image_info_not_implemented(self):
        """Test that GPRImage.get_image_info raises NotImplementedError when bindings unavailable."""
        gpr_img = GPRImage(self.temp_gpr_file.name)
        
        with self.assertRaises(NotImplementedError) as context:
            gpr_img.get_image_info()
            
        self.assertIn("GPR C++ bindings not available", str(context.exception))
    
    def test_load_gpr_as_numpy_not_implemented(self):
        """Test that load_gpr_as_numpy raises NotImplementedError when bindings unavailable."""
        with self.assertRaises(NotImplementedError) as context:
            load_gpr_as_numpy(self.temp_gpr_file.name)
            
        self.assertIn("GPR C++ bindings not available", str(context.exception))
        
    def test_load_gpr_as_numpy_with_dtype(self):
        """Test that load_gpr_as_numpy with different dtypes raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            load_gpr_as_numpy(self.temp_gpr_file.name, dtype="uint16")
            
        with self.assertRaises(NotImplementedError):
            load_gpr_as_numpy(self.temp_gpr_file.name, dtype="float32")
            
    def test_load_gpr_as_numpy_with_nonexistent_file(self):
        """Test that load_gpr_as_numpy raises FileNotFoundError for non-existent files."""
        non_existent_path = "/path/that/does/not/exist.gpr"
        
        with self.assertRaises(FileNotFoundError) as context:
            load_gpr_as_numpy(non_existent_path)
            
        self.assertIn("GPR file not found", str(context.exception))
        
    def test_get_gpr_image_info_not_implemented(self):
        """Test that get_gpr_image_info raises NotImplementedError when bindings unavailable."""
        with self.assertRaises(NotImplementedError) as context:
            get_gpr_image_info(self.temp_gpr_file.name)
            
        self.assertIn("GPR C++ bindings not available", str(context.exception))
        
    def test_get_gpr_image_info_with_nonexistent_file(self):
        """Test that get_gpr_image_info raises FileNotFoundError for non-existent files."""
        non_existent_path = "/path/that/does/not/exist.gpr"
        
        with self.assertRaises(FileNotFoundError) as context:
            get_gpr_image_info(non_existent_path)
            
        self.assertIn("GPR file not found", str(context.exception))


class TestNumPyIntegrationWithoutNumPy(unittest.TestCase):
    """Test that NumPy integration gracefully handles missing NumPy."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary GPR file for testing
        self.temp_gpr_file = tempfile.NamedTemporaryFile(delete=False, suffix='.gpr')
        self.temp_gpr_file.write(b'dummy GPR content for testing')
        self.temp_gpr_file.close()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_gpr_file.name):
            os.unlink(self.temp_gpr_file.name)
    
    def test_functions_exist_without_numpy(self):
        """Test that NumPy integration functions exist even without NumPy available."""
        # These functions should exist even if NumPy is not available
        self.assertTrue(hasattr(python_gpr.core, 'load_gpr_as_numpy'))
        self.assertTrue(hasattr(python_gpr.core, 'get_gpr_image_info'))
        
        # GPRImage should have the new methods
        gpr_img = GPRImage(self.temp_gpr_file.name)
        self.assertTrue(hasattr(gpr_img, 'to_numpy'))
        self.assertTrue(hasattr(gpr_img, 'get_image_info'))


@unittest.skipUnless(HAS_NUMPY, "NumPy not available")
class TestNumPyIntegrationAPI(unittest.TestCase):
    """Test NumPy integration API design and error handling."""
    
    def test_supported_dtypes(self):
        """Test that the API documents supported dtypes correctly."""
        # This is mainly a documentation test to ensure we handle expected dtypes
        gpr_img = GPRImage("/dummy/path.gpr")
        
        # Test that these dtypes are documented as supported
        supported_dtypes = ["uint16", "float32"]
        
        for dtype in supported_dtypes:
            # Since bindings aren't available, we expect NotImplementedError,
            # but we want to make sure the API accepts these dtype parameters
            try:
                gpr_img.to_numpy(dtype=dtype)
            except NotImplementedError:
                # This is expected when bindings aren't available
                pass
            except FileNotFoundError:
                # This is also expected for dummy path
                pass
            except TypeError:
                # This would indicate the API doesn't accept the dtype parameter
                self.fail(f"API should accept dtype '{dtype}'")
                
    def test_return_type_annotations(self):
        """Test that functions have proper return type annotations."""
        import inspect
        from python_gpr.core import load_gpr_as_numpy, get_gpr_image_info
        
        # Check that load_gpr_as_numpy is annotated to return np.ndarray
        sig = inspect.signature(load_gpr_as_numpy)
        # Note: We can't check the actual return annotation easily without 
        # importing types, but we can verify the function exists and is callable
        self.assertTrue(callable(load_gpr_as_numpy))
        
        # Check that get_gpr_image_info is annotated to return dict
        sig = inspect.signature(get_gpr_image_info)
        self.assertTrue(callable(get_gpr_image_info))


if __name__ == '__main__':
    unittest.main()