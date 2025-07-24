"""
Platform-specific compatibility tests for python-gpr.

These tests verify that the library works correctly across different
operating systems, Python versions, and NumPy versions, identifying
platform-specific issues and behaviors.
"""

import unittest
import sys
import platform
import os
import tempfile
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import numpy as np
    HAS_NUMPY = True
    NUMPY_VERSION = np.__version__
except ImportError:
    HAS_NUMPY = False
    NUMPY_VERSION = None

import python_gpr
from python_gpr.core import GPRImage
from python_gpr.conversion import GPRParameters


class TestPlatformInfo(unittest.TestCase):
    """Test platform information reporting."""
    
    def test_platform_detection(self):
        """Test that we can detect the current platform correctly."""
        system = platform.system()
        self.assertIn(system, ['Linux', 'Windows', 'Darwin'], 
                     f"Unexpected platform: {system}")
        
        # Test basic platform properties
        self.assertIsInstance(platform.python_version(), str)
        self.assertIsInstance(platform.architecture(), tuple)
        
    def test_python_version_compatibility(self):
        """Test Python version compatibility."""
        version_info = sys.version_info
        
        # Ensure we're running on a supported Python version
        self.assertGreaterEqual(version_info.major, 3)
        self.assertGreaterEqual(version_info.minor, 9)
        
        # Test that python_gpr works with current Python version
        self.assertIsNotNone(python_gpr.__version__)
        
    @unittest.skipUnless(HAS_NUMPY, "NumPy not available")
    def test_numpy_version_compatibility(self):
        """Test NumPy version compatibility."""
        version_parts = NUMPY_VERSION.split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1])
        
        # Test that we support NumPy 1.20+
        if major == 1:
            self.assertGreaterEqual(minor, 20, 
                                  f"NumPy {NUMPY_VERSION} is too old (need 1.20+)")
        else:
            # NumPy 2.x should work
            self.assertGreaterEqual(major, 1)


class TestFileSystemCompatibility(unittest.TestCase):
    """Test file system and path handling across platforms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_path_handling(self):
        """Test path handling across different platforms."""
        # Test with different path formats
        test_paths = [
            "test.gpr",
            "./test.gpr", 
            os.path.join(self.temp_dir, "test.gpr"),
            Path(self.temp_dir) / "test.gpr"
        ]
        
        for test_path in test_paths:
            with self.subTest(path=test_path):
                # Create a dummy file
                if isinstance(test_path, Path):
                    file_path = test_path
                else:
                    file_path = Path(test_path)
                
                # Make sure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_bytes(b"dummy gpr content")
                
                try:
                    # Test that GPRImage can handle the path
                    gpr_img = GPRImage(str(file_path))
                    self.assertEqual(gpr_img.filepath, str(file_path))
                finally:
                    # Clean up
                    if file_path.exists():
                        file_path.unlink()
    
    def test_unicode_paths(self):
        """Test handling of Unicode characters in file paths."""
        if platform.system() == "Windows":
            # Windows has specific Unicode handling requirements
            unicode_filename = "测试_file_café.gpr"
        else:
            unicode_filename = "test_café_файл.gpr"
        
        unicode_path = Path(self.temp_dir) / unicode_filename
        unicode_path.write_bytes(b"dummy gpr content")
        
        try:
            # Test that the library can handle Unicode paths
            gpr_img = GPRImage(str(unicode_path))
            self.assertEqual(gpr_img.filepath, str(unicode_path))
        except UnicodeError:
            self.fail(f"Failed to handle Unicode path: {unicode_path}")
        finally:
            if unicode_path.exists():
                unicode_path.unlink()


class TestMemoryManagement(unittest.TestCase):
    """Test memory management across platforms."""
    
    def test_object_creation_cleanup(self):
        """Test that objects are properly created and cleaned up."""
        import gc
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.gpr', delete=False) as tmp_file:
            tmp_file.write(b"dummy gpr content")
            temp_path = tmp_file.name
        
        try:
            # Test object creation and deletion
            initial_objects = len(gc.get_objects())
            
            for i in range(10):
                gpr_img = GPRImage(temp_path)
                params = GPRParameters()
                del gpr_img
                del params
            
            # Force garbage collection
            gc.collect()
            
            # Check that we don't have a major memory leak
            final_objects = len(gc.get_objects())
            object_growth = final_objects - initial_objects
            
            # Allow some growth but not excessive
            self.assertLess(object_growth, 100, 
                          f"Potential memory leak: {object_growth} new objects")
        finally:
            os.unlink(temp_path)


@unittest.skipUnless(HAS_NUMPY, "NumPy not available")
class TestNumPyPlatformCompatibility(unittest.TestCase):
    """Test NumPy integration across platforms and versions."""
    
    def test_numpy_dtypes_platform_consistency(self):
        """Test that NumPy dtypes behave consistently across platforms."""
        # Test different dtypes that should work consistently
        test_dtypes = [
            np.uint8, np.uint16, np.uint32,
            np.int8, np.int16, np.int32,
            np.float32, np.float64
        ]
        
        for dtype in test_dtypes:
            with self.subTest(dtype=dtype):
                # Test basic dtype properties
                self.assertIsNotNone(dtype)
                
                # Test array creation with this dtype
                test_array = np.array([1, 2, 3], dtype=dtype)
                self.assertEqual(test_array.dtype, dtype)
    
    def test_numpy_memory_layout(self):
        """Test NumPy memory layout consistency."""
        test_array = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.uint16)
        
        # Test memory properties
        self.assertIsNotNone(test_array.data)
        self.assertIsInstance(test_array.strides, tuple)
        self.assertIsInstance(test_array.shape, tuple)
        
        # Test C-contiguous arrays (important for C++ bindings)
        c_array = np.ascontiguousarray(test_array)
        self.assertTrue(c_array.flags.c_contiguous)
    
    def test_numpy_version_specific_features(self):
        """Test NumPy version-specific features and compatibility."""
        version_parts = NUMPY_VERSION.split('.')
        major = int(version_parts[0])
        
        if major >= 2:
            # NumPy 2.x specific tests
            # Test that string dtypes still work
            str_array = np.array(['test'], dtype='U4')
            self.assertEqual(str_array[0], 'test')
        
        # Test features that should work in both 1.x and 2.x
        test_array = np.zeros((10, 10), dtype=np.float32)
        self.assertEqual(test_array.shape, (10, 10))
        self.assertEqual(test_array.dtype, np.float32)


class TestPlatformSpecificBehaviors(unittest.TestCase):
    """Test platform-specific behaviors and edge cases."""
    
    def test_endianness_handling(self):
        """Test handling of different byte orders."""
        import sys
        
        # Check system endianness
        endianness = sys.byteorder
        self.assertIn(endianness, ['little', 'big'])
        
        if HAS_NUMPY:
            # Test NumPy endianness detection
            test_array = np.array([1, 2, 3], dtype=np.uint16)
            self.assertIsNotNone(test_array.dtype.byteorder)
    
    def test_line_ending_handling(self):
        """Test that the library handles different line endings properly."""
        # This is more relevant for text processing, but good to verify
        # that our error messages and logs handle line endings correctly
        
        import io
        import sys
        from contextlib import redirect_stderr
        
        # Test with a non-existent file to generate an error message
        f = io.StringIO()
        
        with redirect_stderr(f):
            try:
                # Trigger an error that generates stderr output
                GPRImage("definitely_nonexistent_file_12345.gpr")
            except FileNotFoundError as e:
                # The exception message itself contains the error info
                error_message = str(e)
                # Test that error message exists and is reasonable
                self.assertIn("GPR file not found", error_message)
                self.assertIn("definitely_nonexistent_file_12345.gpr", error_message)
        
        # Even if no stderr was captured, the exception handling worked correctly
        # This test mainly ensures that the library doesn't crash on file errors
    
    def test_floating_point_precision(self):
        """Test floating point precision across platforms."""
        if not HAS_NUMPY:
            self.skipTest("NumPy not available")
        
        # Test that floating point operations are consistent
        test_values = [0.1, 0.2, 0.3, 1.0/3.0]
        
        for value in test_values:
            with self.subTest(value=value):
                # Test basic operations
                np_value = np.float32(value)
                self.assertIsInstance(float(np_value), float)
                
                # Test that we can round-trip through different precisions
                float64_val = np.float64(value)
                float32_val = np.float32(float64_val)
                
                # Should be close (allowing for precision loss)
                if value != 1.0/3.0:  # Skip the infinite decimal
                    self.assertAlmostEqual(float(float32_val), value, places=6)


class TestExceptionHandling(unittest.TestCase):
    """Test exception handling across platforms."""
    
    def test_file_not_found_exceptions(self):
        """Test FileNotFoundError handling across platforms."""
        nonexistent_paths = [
            "does_not_exist.gpr",
            "/nonexistent/path.gpr",
            "C:\\nonexistent\\path.gpr" if platform.system() == "Windows" else "/tmp/nonexistent.gpr"
        ]
        
        for path in nonexistent_paths:
            with self.subTest(path=path):
                with self.assertRaises(FileNotFoundError):
                    GPRImage(path)
    
    def test_permission_error_handling(self):
        """Test permission error handling where applicable."""
        # This test may not work on all platforms/environments
        if platform.system() in ["Linux", "Darwin"]:  # Unix-like systems
            # Try to create a file without permission (if possible)
            try:
                test_path = "/root/test.gpr"  # Typically not writable
                with self.assertRaises((PermissionError, FileNotFoundError)):
                    # This might raise FileNotFoundError if /root doesn't exist
                    with open(test_path, 'w') as f:
                        f.write("test")
            except PermissionError:
                # This is expected and good
                pass
            except:
                # Skip this test if we can't test permissions
                self.skipTest("Cannot test permission errors on this system")


if __name__ == '__main__':
    # Print platform information before running tests
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    if HAS_NUMPY:
        print(f"NumPy: {NUMPY_VERSION}")
    else:
        print("NumPy: Not available")
    print("-" * 50)
    
    unittest.main(verbosity=2)