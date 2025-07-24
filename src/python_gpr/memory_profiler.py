"""
Memory profiling utilities for the Python GPR library.

This module provides tools for memory leak detection and monitoring
memory usage during GPR operations.
"""

import functools
import gc
import resource
import sys
import time
import tracemalloc
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union
import warnings

F = TypeVar('F', bound=Callable[..., Any])


class MemoryProfiler:
    """Memory profiler for tracking memory usage and detecting leaks."""

    def __init__(self):
        """Initialize the memory profiler."""
        self.baseline_memory: Optional[int] = None
        self.snapshots: List[Tuple[str, int, float]] = []
        self._tracemalloc_started = False

    def start_profiling(self) -> None:
        """Start memory profiling."""
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            self._tracemalloc_started = True
        
        # Force garbage collection to get a clean baseline
        gc.collect()
        
        # Record baseline memory usage
        self.baseline_memory = self.get_current_memory()
        self.snapshots = []
        self.take_snapshot("baseline")

    def stop_profiling(self) -> None:
        """Stop memory profiling."""
        if self._tracemalloc_started and tracemalloc.is_tracing():
            tracemalloc.stop()
            self._tracemalloc_started = False

    def get_current_memory(self) -> int:
        """Get current memory usage in bytes."""
        # Force garbage collection before measurement
        gc.collect()
        
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            return current
        else:
            # Fallback to resource module (RSS memory)
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024

    def get_peak_memory(self) -> int:
        """Get peak memory usage in bytes since profiling started."""
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            return peak
        else:
            # Fallback to current memory if peak is not available
            return self.get_current_memory()

    def take_snapshot(self, label: str) -> int:
        """Take a memory snapshot with a label."""
        memory_usage = self.get_current_memory()
        timestamp = time.time()
        self.snapshots.append((label, memory_usage, timestamp))
        return memory_usage

    def get_memory_growth(self) -> int:
        """Get memory growth since baseline in bytes."""
        if self.baseline_memory is None:
            raise RuntimeError("Profiling not started. Call start_profiling() first.")
        
        current_memory = self.get_current_memory()
        return current_memory - self.baseline_memory

    def check_for_leaks(self, threshold_bytes: int = 1024 * 1024) -> Tuple[bool, str]:
        """
        Check for memory leaks.
        
        Args:
            threshold_bytes: Memory growth threshold in bytes (default: 1MB)
            
        Returns:
            Tuple of (has_leak, report_message)
        """
        if self.baseline_memory is None:
            return False, "No baseline memory recorded"
        
        memory_growth = self.get_memory_growth()
        
        if memory_growth > threshold_bytes:
            report = f"Memory leak detected: {memory_growth} bytes growth (threshold: {threshold_bytes} bytes)"
            return True, report
        else:
            report = f"No memory leak detected: {memory_growth} bytes growth (threshold: {threshold_bytes} bytes)"
            return False, report

    def get_memory_report(self) -> str:
        """Generate a detailed memory usage report."""
        if not self.snapshots:
            return "No memory snapshots available"
        
        report_lines = ["Memory Usage Report:", "=" * 40]
        
        for i, (label, memory, timestamp) in enumerate(self.snapshots):
            memory_mb = memory / (1024 * 1024)
            
            if i == 0:
                growth = 0
            else:
                growth = memory - self.snapshots[0][1]
            
            growth_mb = growth / (1024 * 1024)
            
            report_lines.append(
                f"{label}: {memory_mb:.2f} MB (growth: {growth_mb:+.2f} MB)"
            )
        
        # Add final statistics
        if len(self.snapshots) > 1:
            total_growth = self.snapshots[-1][1] - self.snapshots[0][1]
            total_growth_mb = total_growth / (1024 * 1024)
            report_lines.append("-" * 40)
            report_lines.append(f"Total memory growth: {total_growth_mb:+.2f} MB")
        
        return "\n".join(report_lines)


def memory_profile(threshold_bytes: int = 1024 * 1024) -> Callable[[F], F]:
    """
    Decorator to profile memory usage of a function.
    
    Args:
        threshold_bytes: Memory growth threshold in bytes (default: 1MB)
        
    Raises:
        MemoryError: If memory growth exceeds threshold
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler = MemoryProfiler()
            profiler.start_profiling()
            
            try:
                result = func(*args, **kwargs)
                
                # Check for memory leaks
                has_leak, report = profiler.check_for_leaks(threshold_bytes)
                if has_leak:
                    warnings.warn(f"Memory leak in {func.__name__}: {report}")
                
                return result
            finally:
                profiler.stop_profiling()
        
        return wrapper
    return decorator


def measure_memory_usage(func: Callable, *args, **kwargs) -> Tuple[Any, int, str]:
    """
    Measure memory usage of a function call.
    
    Args:
        func: Function to measure
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Tuple of (result, memory_growth_bytes, memory_report)
    """
    profiler = MemoryProfiler()
    profiler.start_profiling()
    
    try:
        result = func(*args, **kwargs)
        profiler.take_snapshot("after_function")
        
        memory_growth = profiler.get_memory_growth()
        memory_report = profiler.get_memory_report()
        
        return result, memory_growth, memory_report
    finally:
        profiler.stop_profiling()


def run_memory_stress_test(
    operation: Callable,
    iterations: int = 100,
    threshold_bytes: int = 1024 * 1024,
    operation_args: Optional[Tuple] = None,
    operation_kwargs: Optional[Dict] = None
) -> Tuple[bool, str, List[int]]:
    """
    Run a stress test to detect memory leaks in repeated operations.
    
    Args:
        operation: Function to test repeatedly
        iterations: Number of iterations to run
        threshold_bytes: Memory growth threshold in bytes
        operation_args: Arguments for the operation
        operation_kwargs: Keyword arguments for the operation
        
    Returns:
        Tuple of (has_leak, report, memory_measurements)
    """
    if operation_args is None:
        operation_args = ()
    if operation_kwargs is None:
        operation_kwargs = {}
    
    profiler = MemoryProfiler()
    profiler.start_profiling()
    
    memory_measurements = []
    
    try:
        # Run the operation multiple times
        for i in range(iterations):
            # Run the operation
            operation(*operation_args, **operation_kwargs)
            
            # Force garbage collection between iterations
            gc.collect()
            
            # Take memory snapshot every 10 iterations
            if i % 10 == 0:
                memory = profiler.take_snapshot(f"iteration_{i}")
                memory_measurements.append(memory)
        
        # Final memory check
        final_memory = profiler.take_snapshot("final")
        memory_measurements.append(final_memory)
        
        # Check for leaks
        has_leak, leak_report = profiler.check_for_leaks(threshold_bytes)
        full_report = f"{leak_report}\n\n{profiler.get_memory_report()}"
        
        return has_leak, full_report, memory_measurements
        
    finally:
        profiler.stop_profiling()


# Global profiler instance for convenience
_global_profiler = MemoryProfiler()


def start_global_profiling() -> None:
    """Start global memory profiling."""
    _global_profiler.start_profiling()


def stop_global_profiling() -> None:
    """Stop global memory profiling."""
    _global_profiler.stop_profiling()


def get_global_memory_report() -> str:
    """Get memory report from global profiler."""
    return _global_profiler.get_memory_report()


def check_global_memory_leaks(threshold_bytes: int = 1024 * 1024) -> Tuple[bool, str]:
    """Check for memory leaks using global profiler."""
    return _global_profiler.check_for_leaks(threshold_bytes)