# Memory Leak Detection for Python GPR

This directory contains automated memory leak detection tools and tests for the Python GPR library.

## Overview

The memory leak detection system provides comprehensive monitoring of memory usage to ensure proper resource management in the Python bindings. It uses Python's built-in `tracemalloc` module for accurate memory tracking without requiring external dependencies.

## Features

### 1. Memory Profiler (`memory_profiler.py`)

A comprehensive memory profiling toolkit that includes:

- **MemoryProfiler class**: Detailed memory profiling with baseline tracking
- **@memory_profile decorator**: Automatic leak detection for functions
- **measure_memory_usage()**: Function-level memory measurement
- **run_memory_stress_test()**: Stress testing for memory leaks
- **Global profiling functions**: Convenience functions for quick profiling

### 2. Memory Leak Tests (`test_memory_leaks.py`)

Unit tests specifically designed to detect memory leaks:

- Basic memory profiler functionality tests
- GPR object creation memory leak tests
- Function operation memory leak tests
- Exception handling memory leak tests

### 3. Long-Running Tests (`test_memory_long_running.py`)

Extended tests that run for longer periods to detect leaks that may only appear over time:

- Extended object operation tests
- Continuous metadata processing tests
- Mixed operation endurance tests
- Memory growth pattern analysis

### 4. Automated Detection Script (`scripts/check_memory_leaks.py`)

Standalone script for automated memory leak detection:

```bash
# Quick test (50 iterations, 0.5MB threshold)
python scripts/check_memory_leaks.py --quick

# Custom parameters
python scripts/check_memory_leaks.py --iterations 200 --threshold-mb 2

# Verbose output
python scripts/check_memory_leaks.py --verbose
```

## Usage Examples

### Basic Memory Profiling

```python
from python_gpr.memory_profiler import MemoryProfiler

profiler = MemoryProfiler()
profiler.start_profiling()

# Your operations here
img = GPRImage("test.gpr")
profiler.take_snapshot("after_image_creation")

# Check for leaks
has_leak, report = profiler.check_for_leaks()
print(report)

profiler.stop_profiling()
```

### Function Decorator

```python
from python_gpr.memory_profiler import memory_profile

@memory_profile(threshold_bytes=1024*1024)  # 1MB threshold
def my_gpr_function():
    # Function implementation
    return GPRImage("test.gpr")
```

### Stress Testing

```python
from python_gpr.memory_profiler import run_memory_stress_test

def test_operation():
    img = GPRImage("test.gpr")
    return img

has_leak, report, measurements = run_memory_stress_test(
    test_operation,
    iterations=100,
    threshold_bytes=512*1024  # 512KB threshold
)
```

### Memory Measurement

```python
from python_gpr.memory_profiler import measure_memory_usage

def memory_intensive_function():
    return [GPRImage("test.gpr") for _ in range(10)]

result, memory_growth, report = measure_memory_usage(memory_intensive_function)
print(f"Memory growth: {memory_growth} bytes")
```

## Running Tests

### Unit Tests

```bash
# Run all memory leak tests
python -m unittest tests.test_memory_leaks -v

# Run specific test class
python -m unittest tests.test_memory_leaks.TestMemoryProfiler -v

# Run with pytest (if available)
python -m pytest tests/test_memory_leaks.py -v
```

### Long-Running Tests

```bash
# Run all long-running tests
python -m unittest tests.test_memory_long_running -v

# Run specific long-running tests
python -m unittest tests.test_memory_long_running.TestMemoryGrowthPatterns -v
```

### Automated Detection

```bash
# Quick automated check
python scripts/check_memory_leaks.py --quick

# Full automated check
python scripts/check_memory_leaks.py

# Custom parameters
python scripts/check_memory_leaks.py --iterations 200 --threshold-mb 2 --verbose
```

## CI Integration

The memory leak detection is integrated into the CI pipeline via `.github/workflows/tests.yml`:

1. **Memory leak detection tests**: Runs unit tests for memory profiling
2. **Automated memory leak detection**: Runs the standalone detection script
3. **Long-running memory tests**: Runs selected long-running tests

All memory tests are set to `continue-on-error: true` to avoid breaking the build during development while still providing visibility into potential issues.

## Thresholds and Configuration

### Default Thresholds

- **Standard tests**: 1MB memory growth threshold
- **Quick tests**: 0.5MB memory growth threshold
- **Stress tests**: 512KB threshold for most operations

### Adjusting Thresholds

Thresholds can be adjusted based on your needs:

```python
# Lower threshold for sensitive operations
profiler.check_for_leaks(threshold_bytes=100*1024)  # 100KB

# Higher threshold for expected growth
profiler.check_for_leaks(threshold_bytes=5*1024*1024)  # 5MB
```

## Memory Measurement Accuracy

The system uses Python's `tracemalloc` module which provides:

- **Accurate tracking**: Tracks all Python memory allocations
- **No external dependencies**: Built into Python 3.4+
- **Low overhead**: Minimal impact on performance
- **Detailed snapshots**: Memory usage at specific points in time

## Troubleshooting

### False Positives

If you're getting false positive memory leak detections:

1. **Check threshold**: Increase the threshold if legitimate memory growth is expected
2. **Garbage collection**: Ensure proper cleanup with `gc.collect()`
3. **Object references**: Check for unintended object references
4. **Test isolation**: Ensure tests don't interfere with each other

### Performance Impact

Memory profiling has minimal performance impact:

- **Tracemalloc overhead**: ~1-3% performance decrease
- **Automatic cleanup**: Tests clean up temporary files and objects
- **Efficient snapshots**: Memory measurements are taken efficiently

## Demo and Examples

Run the memory profiling demo to see all features in action:

```bash
python demo_memory_profiling.py
```

This demo showcases:
- Basic memory profiling
- Decorator usage
- Memory measurement
- Stress testing
- All available features

## Integration with Development Workflow

### Pre-commit Hooks

Add memory leak checks to your pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: memory-leak-check
        name: Check for memory leaks
        entry: python scripts/check_memory_leaks.py --quick
        language: system
        pass_filenames: false
```

### IDE Integration

Use the memory profiler decorator during development:

```python
# Add to functions you want to monitor
@memory_profile()
def new_feature():
    # Your implementation
    pass
```

## Future Enhancements

Potential future improvements:

1. **Memory visualization**: Graphs and charts of memory usage over time
2. **Custom reporters**: Different output formats (JSON, XML, etc.)
3. **Integration with external tools**: Support for memory-profiler, pympler
4. **Performance benchmarking**: Memory usage benchmarks over time
5. **Leak categorization**: Different types of memory leak detection

## Contributing

When adding new features or fixing bugs:

1. **Add memory tests**: Include memory leak tests for new functionality
2. **Update thresholds**: Adjust thresholds if legitimate memory usage changes
3. **Document changes**: Update this README for new features
4. **Test thoroughly**: Run all memory tests before submitting changes

The memory leak detection system helps ensure the Python GPR library maintains excellent memory management and provides a reliable experience for users.