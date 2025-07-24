"""
Memory leak detection tests for python-gpr.

This module contains tests specifically designed to detect memory leaks
in the Python GPR library.
"""

import gc
import tempfile
import unittest
import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from python_gpr.memory_profiler import (
        MemoryProfiler,
        memory_profile,
        measure_memory_usage,
        run_memory_stress_test
    )
    from python_gpr.core import GPRImage, get_gpr_info
    from python_gpr.metadata import GPRMetadata, extract_exif, extract_gpr_info
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Failed to import python_gpr modules: {e}")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Python path: {sys.path}")
    IMPORTS_AVAILABLE = False


class TestMemoryProfiler(unittest.TestCase):
    """Test the memory profiler functionality."""

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_memory_profiler_basic(self):
        """Test basic memory profiler functionality."""
        profiler = MemoryProfiler()
        
        # Test that we can start and stop profiling
        profiler.start_profiling()
        self.assertIsNotNone(profiler.baseline_memory)
        self.assertEqual(len(profiler.snapshots), 1)
        
        # Take a snapshot
        memory = profiler.take_snapshot("test")
        self.assertEqual(len(profiler.snapshots), 2)
        
        # Check for leaks (should be none with minimal operations)
        has_leak, report = profiler.check_for_leaks()
        self.assertFalse(has_leak)
        self.assertIn("No memory leak detected", report)
        
        # Get memory report
        memory_report = profiler.get_memory_report()
        self.assertIn("Memory Usage Report", memory_report)
        self.assertIn("baseline", memory_report)
        self.assertIn("test", memory_report)
        
        profiler.stop_profiling()

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_memory_profiler_growth_detection(self):
        """Test memory growth detection."""
        profiler = MemoryProfiler()
        profiler.start_profiling()
        
        # Create some objects to increase memory usage
        large_list = [i for i in range(1000)]  # Small increase
        profiler.take_snapshot("after_small_allocation")
        
        # Check growth
        growth = profiler.get_memory_growth()
        self.assertGreater(growth, 0)  # Should have some growth
        
        # Check for leaks with very low threshold
        has_leak, report = profiler.check_for_leaks(threshold_bytes=1)
        self.assertTrue(has_leak)  # Should detect the allocation as a "leak"
        self.assertIn("Memory leak detected", report)
        
        # Clean up
        del large_list
        gc.collect()
        
        profiler.stop_profiling()

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_memory_profile_decorator(self):
        """Test the memory profile decorator."""
        
        @memory_profile(threshold_bytes=1024 * 1024)  # 1MB threshold
        def test_function():
            # Create a small list that shouldn't trigger leak detection
            return [i for i in range(100)]
        
        # This should not raise any warnings or exceptions
        result = test_function()
        self.assertEqual(len(result), 100)

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_measure_memory_usage(self):
        """Test the measure_memory_usage function."""
        
        def test_operation():
            return [i for i in range(1000)]
        
        result, memory_growth, report = measure_memory_usage(test_operation)
        
        self.assertEqual(len(result), 1000)
        self.assertIsInstance(memory_growth, int)
        self.assertIn("Memory Usage Report", report)


class TestGPRMemoryLeaks(unittest.TestCase):
    """Test for memory leaks in GPR operations."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary GPR file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.gpr')
        self.temp_file.write(b'dummy GPR content')
        self.temp_file.close()

    def tearDown(self):
        """Clean up test fixtures."""
        import os
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_gpr_image_creation_memory_leak(self):
        """Test for memory leaks in GPRImage creation."""
        
        def create_gpr_image():
            img = GPRImage(self.temp_file.name)
            return img
        
        # Run stress test with multiple GPRImage creations
        has_leak, report, measurements = run_memory_stress_test(
            create_gpr_image,
            iterations=50,
            threshold_bytes=512 * 1024  # 512KB threshold
        )
        
        # Print report for debugging
        print(f"\nGPRImage creation memory test report:\n{report}")
        
        # Should not have significant memory leaks for simple object creation
        self.assertFalse(has_leak, f"Memory leak detected in GPRImage creation: {report}")

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_gpr_metadata_creation_memory_leak(self):
        """Test for memory leaks in GPRMetadata creation."""
        
        def create_gpr_metadata():
            metadata = GPRMetadata(self.temp_file.name)
            return metadata
        
        # Run stress test with multiple GPRMetadata creations
        has_leak, report, measurements = run_memory_stress_test(
            create_gpr_metadata,
            iterations=50,
            threshold_bytes=512 * 1024  # 512KB threshold
        )
        
        # Print report for debugging
        print(f"\nGPRMetadata creation memory test report:\n{report}")
        
        # Should not have significant memory leaks for simple object creation
        self.assertFalse(has_leak, f"Memory leak detected in GPRMetadata creation: {report}")

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_repeated_file_operations_memory_leak(self):
        """Test for memory leaks in repeated file operations."""
        
        def file_operations():
            # Create both image and metadata objects
            img = GPRImage(self.temp_file.name)
            metadata = GPRMetadata(self.temp_file.name)
            
            # Access file paths (should not cause leaks)
            _ = img.filepath
            _ = metadata.filepath
            
            return img, metadata
        
        # Run stress test with repeated operations
        has_leak, report, measurements = run_memory_stress_test(
            file_operations,
            iterations=30,
            threshold_bytes=1024 * 1024  # 1MB threshold
        )
        
        # Print report for debugging
        print(f"\nRepeated file operations memory test report:\n{report}")
        
        # Should not have significant memory leaks
        self.assertFalse(has_leak, f"Memory leak detected in repeated file operations: {report}")

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_exception_handling_memory_leak(self):
        """Test for memory leaks when exceptions are raised."""
        
        def operation_with_exceptions():
            try:
                # This should raise NotImplementedError
                img = GPRImage(self.temp_file.name)
                _ = img.width  # This will raise NotImplementedError
            except NotImplementedError:
                pass  # Expected exception
            
            try:
                # This should also raise NotImplementedError
                metadata = GPRMetadata(self.temp_file.name)
                _ = metadata.camera_model  # This will raise NotImplementedError
            except NotImplementedError:
                pass  # Expected exception
        
        # Run stress test with exception handling
        has_leak, report, measurements = run_memory_stress_test(
            operation_with_exceptions,
            iterations=40,
            threshold_bytes=512 * 1024  # 512KB threshold
        )
        
        # Print report for debugging
        print(f"\nException handling memory test report:\n{report}")
        
        # Should not have significant memory leaks even with exceptions
        self.assertFalse(has_leak, f"Memory leak detected in exception handling: {report}")


class TestFunctionMemoryLeaks(unittest.TestCase):
    """Test for memory leaks in standalone functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary files for testing
        self.temp_gpr_file = tempfile.NamedTemporaryFile(delete=False, suffix='.gpr')
        self.temp_gpr_file.write(b'dummy GPR content')
        self.temp_gpr_file.close()
        
        self.temp_img_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        self.temp_img_file.write(b'dummy image content')
        self.temp_img_file.close()

    def tearDown(self):
        """Clean up test fixtures."""
        import os
        for temp_file in [self.temp_gpr_file, self.temp_img_file]:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_get_gpr_info_memory_leak(self):
        """Test for memory leaks in get_gpr_info function."""
        
        def call_get_gpr_info():
            try:
                return get_gpr_info(self.temp_gpr_file.name)
            except (NotImplementedError, FileNotFoundError):
                return None  # Expected for current implementation
        
        # Run stress test
        has_leak, report, measurements = run_memory_stress_test(
            call_get_gpr_info,
            iterations=40,
            threshold_bytes=512 * 1024  # 512KB threshold
        )
        
        # Print report for debugging
        print(f"\nget_gpr_info memory test report:\n{report}")
        
        # Should not have significant memory leaks
        self.assertFalse(has_leak, f"Memory leak detected in get_gpr_info: {report}")

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_extract_functions_memory_leak(self):
        """Test for memory leaks in extract functions."""
        
        def call_extract_functions():
            try:
                extract_exif(self.temp_img_file.name)
            except (NotImplementedError, FileNotFoundError):
                pass  # Expected for current implementation
            
            try:
                extract_gpr_info(self.temp_gpr_file.name)
            except (NotImplementedError, FileNotFoundError):
                pass  # Expected for current implementation
        
        # Run stress test
        has_leak, report, measurements = run_memory_stress_test(
            call_extract_functions,
            iterations=30,
            threshold_bytes=512 * 1024  # 512KB threshold
        )
        
        # Print report for debugging
        print(f"\nExtract functions memory test report:\n{report}")
        
        # Should not have significant memory leaks
        self.assertFalse(has_leak, f"Memory leak detected in extract functions: {report}")


if __name__ == '__main__':
    # Enable more verbose output for memory tests
    unittest.main(verbosity=2)