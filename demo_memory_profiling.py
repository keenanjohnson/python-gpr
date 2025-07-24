#!/usr/bin/env python3
"""
Demo script showing memory leak detection capabilities in python-gpr.

This script demonstrates how to use the memory profiling tools to detect
memory leaks in GPR operations.
"""

import sys
import tempfile
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent / "src"))

import python_gpr
from python_gpr.memory_profiler import (
    MemoryProfiler,
    memory_profile,
    measure_memory_usage,
    run_memory_stress_test
)
from python_gpr.core import GPRImage, get_gpr_info
from python_gpr.metadata import GPRMetadata


def demo_basic_memory_profiling():
    """Demonstrate basic memory profiling capabilities."""
    print("=" * 60)
    print("Basic Memory Profiling Demo")
    print("=" * 60)
    
    # Create a temporary GPR file for testing
    with tempfile.NamedTemporaryFile(suffix='.gpr', delete=False) as temp_file:
        temp_file.write(b'Demo GPR content for memory profiling')
        temp_file_path = temp_file.name
    
    try:
        # Create a memory profiler
        profiler = MemoryProfiler()
        profiler.start_profiling()
        
        print(f"Baseline memory usage recorded")
        
        # Perform some operations
        img = GPRImage(temp_file_path)
        print(f"Created GPRImage: {img.filepath}")
        profiler.take_snapshot("after_image_creation")
        
        metadata = GPRMetadata(temp_file_path)
        print(f"Created GPRMetadata: {metadata.filepath}")
        profiler.take_snapshot("after_metadata_creation")
        
        # Clean up objects
        del img, metadata
        profiler.take_snapshot("after_cleanup")
        
        # Check for memory leaks
        has_leak, report = profiler.check_for_leaks(threshold_bytes=1024 * 1024)  # 1MB
        print(f"\nMemory leak detection: {'LEAK DETECTED' if has_leak else 'NO LEAKS'}")
        print(report)
        
        # Get detailed memory report
        print(f"\nDetailed Memory Report:")
        print(profiler.get_memory_report())
        
        profiler.stop_profiling()
        
    finally:
        # Clean up temporary file
        import os
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def demo_memory_decorator():
    """Demonstrate the memory profiling decorator."""
    print("\n" + "=" * 60)
    print("Memory Profiling Decorator Demo")
    print("=" * 60)
    
    @memory_profile(threshold_bytes=512 * 1024)  # 512KB threshold
    def create_multiple_objects():
        """Function that creates multiple GPR objects."""
        with tempfile.NamedTemporaryFile(suffix='.gpr', delete=False) as temp_file:
            temp_file.write(b'Demo content for decorator test')
            temp_file_path = temp_file.name
        
        try:
            objects = []
            for i in range(5):
                img = GPRImage(temp_file_path)
                metadata = GPRMetadata(temp_file_path)
                objects.extend([img, metadata])
                print(f"Created object pair {i + 1}")
            
            return len(objects)
        finally:
            import os
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    print("Calling function with memory profiling decorator...")
    result = create_multiple_objects()
    print(f"Function completed, created {result} objects")


def demo_memory_measurement():
    """Demonstrate memory usage measurement."""
    print("\n" + "=" * 60)
    print("Memory Usage Measurement Demo")
    print("=" * 60)
    
    def memory_intensive_operation():
        """A function that uses some memory."""
        with tempfile.NamedTemporaryFile(suffix='.gpr', delete=False) as temp_file:
            temp_file.write(b'Content for memory measurement test')
            temp_file_path = temp_file.name
        
        try:
            # Create multiple objects
            objects = []
            for i in range(10):
                img = GPRImage(temp_file_path)
                objects.append(img)
            
            return len(objects)
        finally:
            import os
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    print("Measuring memory usage of operation...")
    result, memory_growth, report = measure_memory_usage(memory_intensive_operation)
    
    print(f"Operation result: {result}")
    print(f"Memory growth: {memory_growth} bytes ({memory_growth / 1024:.2f} KB)")
    print(f"\nDetailed report:\n{report}")


def demo_stress_testing():
    """Demonstrate stress testing for memory leaks."""
    print("\n" + "=" * 60)
    print("Memory Stress Testing Demo")
    print("=" * 60)
    
    # Create a temporary file for stress testing
    with tempfile.NamedTemporaryFile(suffix='.gpr', delete=False) as temp_file:
        temp_file.write(b'Content for stress testing')
        temp_file_path = temp_file.name
    
    try:
        def stress_operation():
            """Operation to stress test."""
            img = GPRImage(temp_file_path)
            metadata = GPRMetadata(temp_file_path)
            
            # Access properties
            _ = img.filepath
            _ = metadata.filepath
            
            # Try operations that raise NotImplementedError
            try:
                _ = img.width
            except NotImplementedError:
                pass
            
            try:
                _ = metadata.camera_model
            except NotImplementedError:
                pass
        
        print("Running stress test with 30 iterations...")
        has_leak, report, measurements = run_memory_stress_test(
            stress_operation,
            iterations=30,
            threshold_bytes=512 * 1024  # 512KB threshold
        )
        
        print(f"Stress test result: {'LEAK DETECTED' if has_leak else 'NO LEAKS'}")
        print(f"Memory measurements taken: {len(measurements)}")
        print(f"\nDetailed report:\n{report}")
        
    finally:
        # Clean up
        import os
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def main():
    """Run all memory profiling demos."""
    print("Python GPR Memory Leak Detection Demo")
    print(f"Python GPR version: {python_gpr.__version__}")
    print()
    
    try:
        demo_basic_memory_profiling()
        demo_memory_decorator()
        demo_memory_measurement()
        demo_stress_testing()
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)
        print("\nMemory profiling features available:")
        print("- MemoryProfiler class for detailed profiling")
        print("- @memory_profile decorator for automatic leak detection")
        print("- measure_memory_usage() for function profiling")
        print("- run_memory_stress_test() for stress testing")
        print("- Global profiling functions for convenience")
        print("\nAll features use Python's built-in tracemalloc module")
        print("for accurate memory tracking without external dependencies.")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())