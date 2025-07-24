#!/usr/bin/env python3
"""
Memory leak detection script for python-gpr.

This script can be run independently to check for memory leaks in the
python-gpr library. It's designed to be used in CI/CD pipelines or
for manual testing.
"""

import argparse
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from python_gpr.memory_profiler import run_memory_stress_test
    from python_gpr.core import GPRImage, get_gpr_info
    from python_gpr.metadata import GPRMetadata, extract_exif, extract_gpr_info
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: Failed to import python_gpr modules: {e}")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Python path: {sys.path}")
    print("\nThis likely means:")
    print("1. The package is not installed properly")
    print("2. You need to install dependencies: pip install -e .[dev]")
    print("3. You need to build the C++ extensions first")
    print("\nExiting with status code 1...")
    sys.exit(1)


def create_test_file():
    """Create a temporary test file for memory testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.gpr')
    temp_file.write(b'Test content for memory leak detection')
    temp_file.close()
    return temp_file.name


def test_gpr_image_operations(iterations=100, threshold_mb=1):
    """Test GPRImage operations for memory leaks."""
    test_file = create_test_file()
    
    try:
        def gpr_image_test():
            img = GPRImage(test_file)
            _ = img.filepath
            try:
                _ = img.width
            except NotImplementedError:
                pass
        
        has_leak, report, _ = run_memory_stress_test(
            gpr_image_test,
            iterations=iterations,
            threshold_bytes=threshold_mb * 1024 * 1024
        )
        
        return has_leak, "GPRImage operations", report
        
    finally:
        import os
        os.unlink(test_file)


def test_gpr_metadata_operations(iterations=100, threshold_mb=1):
    """Test GPRMetadata operations for memory leaks."""
    test_file = create_test_file()
    
    try:
        def gpr_metadata_test():
            metadata = GPRMetadata(test_file)
            _ = metadata.filepath
            try:
                _ = metadata.camera_model
            except NotImplementedError:
                pass
        
        has_leak, report, _ = run_memory_stress_test(
            gpr_metadata_test,
            iterations=iterations,
            threshold_bytes=threshold_mb * 1024 * 1024
        )
        
        return has_leak, "GPRMetadata operations", report
        
    finally:
        import os
        os.unlink(test_file)


def test_function_operations(iterations=100, threshold_mb=1):
    """Test standalone function operations for memory leaks."""
    test_file = create_test_file()
    
    try:
        def function_test():
            try:
                get_gpr_info(test_file)
            except (NotImplementedError, FileNotFoundError):
                pass
            
            try:
                extract_gpr_info(test_file)
            except (NotImplementedError, FileNotFoundError):
                pass
        
        has_leak, report, _ = run_memory_stress_test(
            function_test,
            iterations=iterations,
            threshold_bytes=threshold_mb * 1024 * 1024
        )
        
        return has_leak, "Function operations", report
        
    finally:
        import os
        os.unlink(test_file)


def main():
    """Main function for memory leak detection."""
    parser = argparse.ArgumentParser(
        description="Memory leak detection for python-gpr",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/check_memory_leaks.py --quick
  python scripts/check_memory_leaks.py --iterations 200 --threshold-mb 2
  python scripts/check_memory_leaks.py --verbose
        """
    )
    
    parser.add_argument(
        "--iterations", "-i",
        type=int,
        default=100,
        help="Number of iterations to run for each test (default: 100)"
    )
    
    parser.add_argument(
        "--threshold-mb", "-t",
        type=float,
        default=1.0,
        help="Memory leak threshold in MB (default: 1.0)"
    )
    
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Run quick tests with fewer iterations (50 iterations, 0.5MB threshold)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed memory reports"
    )
    
    args = parser.parse_args()
    
    # Adjust parameters for quick mode
    if args.quick:
        iterations = 50
        threshold_mb = 0.5
        print("Running in quick mode...")
    else:
        iterations = args.iterations
        threshold_mb = args.threshold_mb
    
    print(f"Memory Leak Detection for python-gpr")
    print(f"Iterations per test: {iterations}")
    print(f"Leak threshold: {threshold_mb} MB")
    print("-" * 50)
    
    # List of tests to run
    tests = [
        ("GPRImage operations", test_gpr_image_operations),
        ("GPRMetadata operations", test_gpr_metadata_operations),
        ("Function operations", test_function_operations),
    ]
    
    overall_result = True
    results = []
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        
        try:
            has_leak, operation_name, report = test_func(iterations, threshold_mb)
            results.append((test_name, has_leak, report))
            
            if has_leak:
                print(f"  ❌ LEAK DETECTED in {test_name}")
                overall_result = False
            else:
                print(f"  ✅ No leaks detected in {test_name}")
            
            if args.verbose:
                print(f"  Report: {report.split('Memory Usage Report:')[0].strip()}")
                print()
            
        except Exception as e:
            print(f"  ⚠️  Error running {test_name}: {e}")
            overall_result = False
    
    # Summary
    print("-" * 50)
    print("SUMMARY:")
    
    leak_count = sum(1 for _, has_leak, _ in results if has_leak)
    total_tests = len(results)
    
    if overall_result:
        print(f"✅ All {total_tests} tests passed - No memory leaks detected!")
        exit_code = 0
    else:
        print(f"❌ {leak_count}/{total_tests} tests detected memory leaks")
        exit_code = 1
    
    if args.verbose:
        print("\nDetailed Reports:")
        for test_name, has_leak, report in results:
            print(f"\n{test_name}:")
            print(report)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())