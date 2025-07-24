"""
Long-running memory tests for python-gpr.

This module contains tests that run for extended periods to detect
memory leaks that may only become apparent over time.
"""

import gc
import tempfile
import time
import unittest
import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from python_gpr.memory_profiler import (
        MemoryProfiler,
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


class TestLongRunningMemoryUsage(unittest.TestCase):
    """Test long-running operations for memory leaks."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary files for testing
        self.temp_gpr_file = tempfile.NamedTemporaryFile(delete=False, suffix='.gpr')
        self.temp_gpr_file.write(b'dummy GPR content for long running tests')
        self.temp_gpr_file.close()
        
        self.temp_img_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        self.temp_img_file.write(b'dummy image content for long running tests')
        self.temp_img_file.close()

    def tearDown(self):
        """Clean up test fixtures."""
        import os
        for temp_file in [self.temp_gpr_file, self.temp_img_file]:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_extended_gpr_image_operations(self):
        """Test extended GPRImage operations for memory leaks."""
        
        def extended_gpr_operations():
            # Create multiple GPRImage instances
            images = []
            for _ in range(5):
                img = GPRImage(self.temp_gpr_file.name)
                images.append(img)
                
                # Access properties that exist
                _ = img.filepath
                
                # Try operations that should fail gracefully
                try:
                    _ = img.width
                except NotImplementedError:
                    pass
                
                try:
                    _ = img.height
                except NotImplementedError:
                    pass
                
                try:
                    _ = img.dimensions
                except NotImplementedError:
                    pass
            
            # Clean up references
            del images
            gc.collect()
        
        # Run extended stress test
        has_leak, report, measurements = run_memory_stress_test(
            extended_gpr_operations,
            iterations=200,  # More iterations for long-running test
            threshold_bytes=2 * 1024 * 1024  # 2MB threshold
        )
        
        # Print detailed report
        print(f"\nExtended GPRImage operations memory test report:\n{report}")
        print(f"Memory measurements: {len(measurements)} snapshots")
        
        # Analyze memory growth pattern
        if len(measurements) > 1:
            initial_memory = measurements[0]
            final_memory = measurements[-1]
            total_growth = final_memory - initial_memory
            print(f"Total memory growth: {total_growth / (1024 * 1024):.2f} MB")
        
        # Should not have significant memory leaks
        self.assertFalse(has_leak, f"Memory leak detected in extended GPRImage operations: {report}")

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_continuous_metadata_processing(self):
        """Test continuous metadata processing for memory leaks."""
        
        def continuous_metadata_operations():
            # Create and process metadata continuously
            for _ in range(10):
                metadata = GPRMetadata(self.temp_gpr_file.name)
                
                # Access available properties
                _ = metadata.filepath
                
                # Try operations that should fail gracefully
                try:
                    _ = metadata.camera_model
                except NotImplementedError:
                    pass
                
                try:
                    _ = metadata.iso_speed
                except NotImplementedError:
                    pass
                
                try:
                    _ = metadata.exposure_time
                except NotImplementedError:
                    pass
                
                try:
                    _ = metadata.f_number
                except NotImplementedError:
                    pass
                
                # Try extract functions
                try:
                    extract_gpr_info(self.temp_gpr_file.name)
                except (NotImplementedError, FileNotFoundError):
                    pass
                
                try:
                    extract_exif(self.temp_img_file.name)
                except (NotImplementedError, FileNotFoundError):
                    pass
            
            # Force cleanup
            gc.collect()
        
        # Run continuous processing test
        has_leak, report, measurements = run_memory_stress_test(
            continuous_metadata_operations,
            iterations=100,  # Fewer iterations but more work per iteration
            threshold_bytes=2 * 1024 * 1024  # 2MB threshold
        )
        
        # Print detailed report
        print(f"\nContinuous metadata processing memory test report:\n{report}")
        
        # Should not have significant memory leaks
        self.assertFalse(has_leak, f"Memory leak detected in continuous metadata processing: {report}")

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_mixed_operations_endurance(self):
        """Test mixed operations over extended periods."""
        
        def mixed_operations():
            # Mix of different operations
            operations = [
                lambda: GPRImage(self.temp_gpr_file.name),
                lambda: GPRMetadata(self.temp_gpr_file.name),
            ]
            
            for op in operations:
                try:
                    obj = op()
                    _ = obj.filepath  # Access a property that should work
                    
                    # Try some operations that might fail
                    if hasattr(obj, 'width'):
                        try:
                            _ = obj.width
                        except NotImplementedError:
                            pass
                    
                    if hasattr(obj, 'camera_model'):
                        try:
                            _ = obj.camera_model
                        except NotImplementedError:
                            pass
                            
                except Exception as e:
                    # Log unexpected exceptions but continue
                    print(f"Unexpected exception in mixed operations: {e}")
            
            # Try function calls
            try:
                get_gpr_info(self.temp_gpr_file.name)
            except (NotImplementedError, FileNotFoundError):
                pass
            
            # Force cleanup
            gc.collect()
        
        # Run endurance test
        has_leak, report, measurements = run_memory_stress_test(
            mixed_operations,
            iterations=150,
            threshold_bytes=3 * 1024 * 1024  # 3MB threshold for mixed operations
        )
        
        # Print detailed report
        print(f"\nMixed operations endurance test report:\n{report}")
        
        # Analyze memory pattern over time
        if len(measurements) >= 3:
            print("Memory progression:")
            for i, memory in enumerate(measurements[:5]):  # Show first 5 measurements
                memory_mb = memory / (1024 * 1024)
                print(f"  Measurement {i}: {memory_mb:.2f} MB")
            
            if len(measurements) > 5:
                print("  ...")
                memory_mb = measurements[-1] / (1024 * 1024)
                print(f"  Final: {memory_mb:.2f} MB")
        
        # Should not have significant memory leaks
        self.assertFalse(has_leak, f"Memory leak detected in mixed operations endurance test: {report}")

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_rapid_object_creation_destruction(self):
        """Test rapid object creation and destruction patterns."""
        
        def rapid_create_destroy():
            # Rapidly create and destroy objects
            objects = []
            
            # Create phase
            for i in range(20):
                img = GPRImage(self.temp_gpr_file.name)
                metadata = GPRMetadata(self.temp_gpr_file.name)
                objects.extend([img, metadata])
            
            # Destruction phase
            del objects
            gc.collect()
            
            # Create again to test reuse patterns
            for i in range(10):
                img = GPRImage(self.temp_gpr_file.name)
                _ = img.filepath
                del img
            
            # Final cleanup
            gc.collect()
        
        # Run rapid creation/destruction test
        has_leak, report, measurements = run_memory_stress_test(
            rapid_create_destroy,
            iterations=50,
            threshold_bytes=1024 * 1024  # 1MB threshold
        )
        
        # Print detailed report
        print(f"\nRapid creation/destruction test report:\n{report}")
        
        # Should not have significant memory leaks
        self.assertFalse(has_leak, f"Memory leak detected in rapid create/destroy test: {report}")


class TestMemoryGrowthPatterns(unittest.TestCase):
    """Test specific memory growth patterns that might indicate leaks."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.gpr')
        self.temp_file.write(b'test content for memory growth patterns')
        self.temp_file.close()

    def tearDown(self):
        """Clean up test fixtures."""
        import os
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_linear_memory_growth_detection(self):
        """Test detection of linear memory growth patterns."""
        profiler = MemoryProfiler()
        profiler.start_profiling()
        
        memory_snapshots = []
        
        try:
            # Simulate operations that should not cause linear growth
            for i in range(20):
                # Create object
                obj = GPRImage(self.temp_file.name)
                _ = obj.filepath
                
                # Take memory snapshot every 5 iterations
                if i % 5 == 0:
                    memory = profiler.take_snapshot(f"iteration_{i}")
                    memory_snapshots.append(memory)
                
                # Clean up
                del obj
                gc.collect()
            
            # Analyze growth pattern
            if len(memory_snapshots) >= 3:
                growths = []
                for i in range(1, len(memory_snapshots)):
                    growth = memory_snapshots[i] - memory_snapshots[i-1]
                    growths.append(growth)
                
                # Check if there's consistent positive growth (indicating a leak)
                avg_growth = sum(growths) / len(growths)
                max_growth = max(growths)
                
                print(f"\nMemory growth analysis:")
                print(f"  Average growth per batch: {avg_growth / 1024:.2f} KB")
                print(f"  Maximum growth per batch: {max_growth / 1024:.2f} KB")
                print(f"  Growth values: {[g/1024 for g in growths]} KB")
                
                # Should not have consistent large positive growth
                self.assertLess(avg_growth, 100 * 1024, 
                              f"Suspicious linear memory growth detected: {avg_growth/1024:.2f} KB average per batch")
        
        finally:
            profiler.stop_profiling()

    @unittest.skipUnless(IMPORTS_AVAILABLE, "python_gpr modules not available")
    def test_memory_baseline_stability(self):
        """Test that memory returns to baseline after operations."""
        profiler = MemoryProfiler()
        profiler.start_profiling()
        
        baseline_memory = profiler.baseline_memory
        
        try:
            # Perform operations
            for _ in range(10):
                obj = GPRImage(self.temp_file.name)
                _ = obj.filepath
                del obj
            
            # Force garbage collection
            for _ in range(3):
                gc.collect()
            
            # Check if memory returns close to baseline
            final_memory = profiler.get_current_memory()
            memory_difference = abs(final_memory - baseline_memory)
            
            print(f"\nMemory baseline stability test:")
            print(f"  Baseline memory: {baseline_memory / 1024:.2f} KB")
            print(f"  Final memory: {final_memory / 1024:.2f} KB")
            print(f"  Difference: {memory_difference / 1024:.2f} KB")
            
            # Memory should return reasonably close to baseline
            # Allow for some variance due to Python's memory management
            threshold = 500 * 1024  # 500 KB threshold
            self.assertLess(memory_difference, threshold,
                          f"Memory did not return to baseline: {memory_difference/1024:.2f} KB difference")
        
        finally:
            profiler.stop_profiling()


if __name__ == '__main__':
    # Set higher verbosity for long-running tests
    print("Running long-running memory tests...")
    print("These tests may take several minutes to complete.")
    unittest.main(verbosity=2)