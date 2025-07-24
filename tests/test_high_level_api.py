"""
Test the high-level Python wrapper API for python-gpr.

This module tests the enhanced GPRImage class with context manager support
and convenience functions.
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock

# Test imports - handle import errors gracefully
try:
    from python_gpr.core import (
        GPRImage, open_gpr, convert_image, get_info, get_gpr_info,
        load_gpr_as_numpy, get_gpr_image_info
    )
    CORE_AVAILABLE = True
except ImportError as e:
    CORE_AVAILABLE = False
    IMPORT_ERROR = str(e)


class TestHighLevelAPI(unittest.TestCase):
    """Test high-level API functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.gpr")
        # Create a dummy file
        with open(self.test_file, 'w') as f:
            f.write("dummy gpr content")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_gpr_image_context_manager(self):
        """Test GPRImage context manager functionality."""
        # Test that GPRImage can be used as context manager
        with GPRImage(self.test_file) as img:
            self.assertIsInstance(img, GPRImage)
            self.assertEqual(img.filepath, self.test_file)
            self.assertFalse(img.is_closed)
        
        # Image should be closed after context
        self.assertTrue(img.is_closed)
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_gpr_image_close_method(self):
        """Test GPRImage manual close functionality."""
        img = GPRImage(self.test_file)
        self.assertFalse(img.is_closed)
        
        img.close()
        self.assertTrue(img.is_closed)
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_gpr_image_closed_operations(self):
        """Test that operations on closed GPRImage raise ValueError."""
        img = GPRImage(self.test_file)
        img.close()
        
        with self.assertRaises(ValueError) as cm:
            _ = img.width
        self.assertIn("closed", str(cm.exception))
        
        with self.assertRaises(ValueError) as cm:
            _ = img.height
        self.assertIn("closed", str(cm.exception))
        
        with self.assertRaises(ValueError) as cm:
            img.get_image_info()
        self.assertIn("closed", str(cm.exception))
        
        with self.assertRaises(ValueError) as cm:
            img.to_numpy()
        self.assertIn("closed", str(cm.exception))
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_gpr_image_conversion_methods(self):
        """Test enhanced conversion methods."""
        img = GPRImage(self.test_file)
        
        # Test that both old and new method names work
        with self.assertRaises(NotImplementedError):
            img.to_dng("output.dng")
        
        with self.assertRaises(NotImplementedError):
            img.convert_to_dng("output.dng")
        
        with self.assertRaises(NotImplementedError):
            img.to_raw("output.raw")
        
        with self.assertRaises(NotImplementedError):
            img.convert_to_raw("output.raw")
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_gpr_image_repr(self):
        """Test GPRImage string representation."""
        img = GPRImage(self.test_file)
        repr_str = repr(img)
        self.assertIn("GPRImage", repr_str)
        self.assertIn(self.test_file, repr_str)
        
        # Test repr when closed
        img.close()
        repr_str = repr(img)
        self.assertIn("closed=True", repr_str)
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_open_gpr_convenience_function(self):
        """Test open_gpr convenience function."""
        img = open_gpr(self.test_file)
        self.assertIsInstance(img, GPRImage)
        self.assertEqual(img.filepath, self.test_file)
        
        # Test with context manager
        with open_gpr(self.test_file) as img:
            self.assertIsInstance(img, GPRImage)
            self.assertFalse(img.is_closed)
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_open_gpr_nonexistent_file(self):
        """Test open_gpr with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            open_gpr("nonexistent.gpr")
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_convert_image_file_not_found(self):
        """Test convert_image with non-existent input file."""
        with self.assertRaises(FileNotFoundError):
            convert_image("nonexistent.gpr", "output.dng")
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_convert_image_format_detection(self):
        """Test convert_image format detection and validation."""
        # Test with unsupported output format
        with self.assertRaises(ValueError) as cm:
            convert_image(self.test_file, "output.unknown")
        self.assertIn("Cannot determine target format", str(cm.exception))
        
        # Test with explicit target format
        with self.assertRaises(NotImplementedError):
            convert_image(self.test_file, "output.dng", target_format="dng")
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_get_info_convenience_function(self):
        """Test get_info convenience function."""
        with self.assertRaises(NotImplementedError):
            get_info(self.test_file)
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_get_info_nonexistent_file(self):
        """Test get_info with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            get_info("nonexistent.gpr")
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_get_gpr_info_legacy_function(self):
        """Test that get_gpr_info delegates to get_info."""
        # Both should raise the same error type
        with self.assertRaises(NotImplementedError):
            get_gpr_info(self.test_file)
        
        with self.assertRaises(FileNotFoundError):
            get_gpr_info("nonexistent.gpr")


class TestAPIConsistency(unittest.TestCase):
    """Test that the API follows Python naming conventions."""
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_function_names_are_pythonic(self):
        """Test that function names follow Python conventions."""
        # Function names should be lowercase with underscores
        self.assertTrue(open_gpr.__name__.islower())
        self.assertTrue(convert_image.__name__.islower())
        self.assertTrue(get_info.__name__.islower())
        self.assertTrue(load_gpr_as_numpy.__name__.islower())
        
        # Should use underscores not camelCase
        self.assertIn('_', open_gpr.__name__)
        self.assertIn('_', convert_image.__name__)
        self.assertIn('_', get_info.__name__)
        self.assertIn('_', load_gpr_as_numpy.__name__)
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_class_name_is_pythonic(self):
        """Test that class name follows Python conventions."""
        # Class names should be CamelCase
        self.assertEqual(GPRImage.__name__, "GPRImage")
        self.assertTrue(GPRImage.__name__[0].isupper())
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_method_names_are_pythonic(self):
        """Test that method names follow Python conventions."""
        # Create a dummy file for testing
        with tempfile.NamedTemporaryFile(suffix='.gpr', delete=False) as f:
            test_file = f.name
        
        try:
            img = GPRImage(test_file)
            
            # Method names should be lowercase with underscores
            self.assertTrue(hasattr(img, 'to_numpy'))
            self.assertTrue(hasattr(img, 'to_dng'))
            self.assertTrue(hasattr(img, 'to_raw'))
            self.assertTrue(hasattr(img, 'convert_to_dng'))
            self.assertTrue(hasattr(img, 'convert_to_raw'))
            self.assertTrue(hasattr(img, 'get_image_info'))
            self.assertTrue(hasattr(img, 'get_metadata'))
            self.assertTrue(hasattr(img, 'is_closed'))
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)


class TestContextManagerBehavior(unittest.TestCase):
    """Test context manager behavior in detail."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.gpr")
        # Create a dummy file
        with open(self.test_file, 'w') as f:
            f.write("dummy gpr content")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_context_manager_enter(self):
        """Test context manager __enter__ method."""
        img = GPRImage(self.test_file)
        
        # __enter__ should return the instance itself
        result = img.__enter__()
        self.assertIs(result, img)
        self.assertFalse(img.is_closed)
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_context_manager_exit_normal(self):
        """Test context manager __exit__ method with normal exit."""
        img = GPRImage(self.test_file)
        
        # __exit__ should close the image and return False
        result = img.__exit__(None, None, None)
        self.assertFalse(result)  # Should not suppress exceptions
        self.assertTrue(img.is_closed)
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_context_manager_exit_with_exception(self):
        """Test context manager __exit__ method when exception occurs."""
        img = GPRImage(self.test_file)
        
        # __exit__ should still close the image when exception occurs
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            result = img.__exit__(type(e), e, e.__traceback__)
            self.assertFalse(result)  # Should not suppress the exception
            self.assertTrue(img.is_closed)
    
    @unittest.skipIf(not CORE_AVAILABLE, f"Core module not available: {IMPORT_ERROR if not CORE_AVAILABLE else ''}")
    def test_context_manager_exception_propagation(self):
        """Test that exceptions inside context manager are properly propagated."""
        with self.assertRaises(ValueError):
            with GPRImage(self.test_file) as img:
                raise ValueError("Test exception")
        
        # Image should still be closed despite the exception
        self.assertTrue(img.is_closed)


if __name__ == '__main__':
    unittest.main()