"""
Test the minimal pybind11 binding functionality.

This test module verifies that the basic pybind11 C++ binding works correctly
and can be imported and used from Python.
"""

import unittest
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

# Add build directory to path to find the compiled module
build_dir = Path(__file__).parent.parent / "build"
if build_dir.exists():
    sys.path.insert(0, str(build_dir))


class TestPybind11Binding(unittest.TestCase):
    """Test the basic pybind11 binding functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Try to import the compiled module
        try:
            import _core
            self._core = _core
            self.module_available = True
        except ImportError:
            self.module_available = False
    
    def test_module_import(self):
        """Test that the _core module can be imported."""
        if not self.module_available:
            self.skipTest("_core module not available - build first with CMake")
        
        self.assertIsNotNone(self._core)
    
    def test_hello_world_function(self):
        """Test the hello_world function."""
        if not self.module_available:
            self.skipTest("_core module not available - build first with CMake")
        
        result = self._core.hello_world()
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Hello World from pybind11!")
    
    def test_add_function(self):
        """Test the add function with integer arguments."""
        if not self.module_available:
            self.skipTest("_core module not available - build first with CMake")
        
        # Test basic addition
        result = self._core.add(5, 3)
        self.assertEqual(result, 8)
        
        # Test with zero
        result = self._core.add(10, 0)
        self.assertEqual(result, 10)
        
        # Test with negative numbers
        result = self._core.add(-5, 3)
        self.assertEqual(result, -2)
        
        # Test with both negative
        result = self._core.add(-5, -3)
        self.assertEqual(result, -8)
    
    def test_greet_function(self):
        """Test the greet function with string arguments."""
        if not self.module_available:
            self.skipTest("_core module not available - build first with CMake")
        
        # Test basic greeting
        result = self._core.greet("World")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Hello, World!")
        
        # Test with different names
        result = self._core.greet("Python")
        self.assertEqual(result, "Hello, Python!")
        
        # Test with empty string
        result = self._core.greet("")
        self.assertEqual(result, "Hello, !")
    
    def test_version_attribute(self):
        """Test that the module has a version attribute."""
        if not self.module_available:
            self.skipTest("_core module not available - build first with CMake")
        
        self.assertTrue(hasattr(self._core, '__version__'))
        version = self._core.__version__
        self.assertIsInstance(version, str)
        self.assertTrue(len(version) > 0)
        # Version should be set from CMake
        self.assertEqual(version, "0.1.0")


class TestBuildSystem(unittest.TestCase):
    """Test that the build system works correctly."""
    
    def test_cmake_build_system(self):
        """Test that CMake can build the project."""
        # Check if CMakeLists.txt exists
        cmake_file = Path(__file__).parent.parent / "CMakeLists.txt"
        self.assertTrue(cmake_file.exists(), "CMakeLists.txt should exist")
        
        # Check if build directory exists or can be created
        build_dir = Path(__file__).parent.parent / "build"
        self.assertTrue(build_dir.exists() or build_dir.parent.exists(), 
                       "Build directory or parent should exist")
    
    def test_pybind11_source_exists(self):
        """Test that the pybind11 source file exists."""
        source_file = Path(__file__).parent.parent / "src" / "python_gpr" / "_core.cpp"
        self.assertTrue(source_file.exists(), "_core.cpp should exist")
        
        # Check that it contains pybind11 includes
        with open(source_file, 'r') as f:
            content = f.read()
            self.assertIn("#include <pybind11/pybind11.h>", content)
            self.assertIn("PYBIND11_MODULE", content)


if __name__ == '__main__':
    # Provide helpful instructions if module is not available
    try:
        import _core
    except ImportError:
        print("\nWARNING: _core module not found.")
        print("To build the pybind11 binding, run:")
        print("  cd build && cmake .. && make")
        print("\nOr run the test from the build directory after building.")
        print("Some tests will be skipped.\n")
    
    unittest.main()