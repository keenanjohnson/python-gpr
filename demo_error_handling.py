#!/usr/bin/env python3
"""
Demonstration of the comprehensive error handling and exception mapping system.

This script shows how the enhanced error handling system provides clear,
actionable error messages and proper exception hierarchy for different
error scenarios in the Python GPR library.
"""

import sys
from pathlib import Path

# Add src to path for importing
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from python_gpr.exceptions import *
    print("✅ Successfully imported error handling system")
except ImportError as e:
    print(f"❌ Failed to import error handling system: {e}")
    sys.exit(1)


def demonstrate_exception_hierarchy():
    """Demonstrate the exception hierarchy and inheritance."""
    print("\n🔹 Exception Hierarchy Demonstration")
    print("=" * 50)
    
    # Show inheritance relationships
    exceptions_to_test = [
        GPRError,
        GPRConversionError,
        GPRFileError,
        GPRFileNotFoundError,
        GPRFilePermissionError,
        GPRFileCorruptedError,
        GPRMemoryError,
        GPRParameterError,
        GPRFormatError,
        GPRUnsupportedFormatError,
        GPRCompressionError,
        GPRMetadataError,
        GPRBitstreamError,
        GPRResourceError,
    ]
    
    print("Exception inheritance tree:")
    for exc_class in exceptions_to_test:
        bases = [base.__name__ for base in exc_class.__bases__ if base != Exception]
        inheritance = " -> ".join(bases + [exc_class.__name__])
        print(f"  {inheritance}")


def demonstrate_error_code_mapping():
    """Demonstrate error code to exception mapping."""
    print("\n🔹 Error Code Mapping Demonstration")
    print("=" * 50)
    
    test_cases = [
        (-2, "File not found", {"filepath": "/missing/file.gpr"}),
        (-3, "Permission denied", {"filepath": "/protected/file.gpr", "operation": "write"}),
        (-4, "File corrupted", {"filepath": "/bad/file.gpr", "reason": "Invalid header"}),
        (-10, "Out of memory", {"requested_size": 1024 * 1024 * 1024}),
        (-20, "Invalid parameter", {"parameter": "input_width"}),
        (-31, "Unsupported format", {"format": "xyz", "supported_formats": ["gpr", "dng", "raw"]}),
        (1, "Bitstream underflow", None),
        (2, "Bitstream overflow", None),
        (-999, "Unknown error", None),
    ]
    
    for error_code, message, context in test_cases:
        try:
            error = map_error_code(error_code, message, context)
            print(f"  Error {error_code:4d} -> {type(error).__name__}")
            print(f"              Message: {error}")
            print()
        except Exception as e:
            print(f"  Error {error_code:4d} -> Failed to map: {e}")


def demonstrate_file_error_creation():
    """Demonstrate creating file errors from system exceptions."""
    print("\n🔹 File Error Creation Demonstration")
    print("=" * 50)
    
    system_errors = [
        (FileNotFoundError("No such file"), "read"),
        (PermissionError("Access denied"), "write"),
        (OSError("I/O error"), "read"),
        (ValueError("Invalid value"), "parse"),
        (None, "general"),
    ]
    
    filepath = "/example/file.gpr"
    
    for system_error, operation in system_errors:
        try:
            error = create_file_error(filepath, operation, system_error)
            print(f"  {type(system_error).__name__ if system_error else 'None':15s} -> {type(error).__name__}")
            print(f"                     Message: {error}")
            print()
        except Exception as e:
            print(f"  Failed to create error: {e}")


def demonstrate_error_context_information():
    """Demonstrate rich error context information."""
    print("\n🔹 Error Context Information Demonstration")
    print("=" * 50)
    
    # File errors with context
    file_error = GPRFileNotFoundError("/missing/important_file.gpr")
    print(f"File Error:")
    print(f"  Type: {type(file_error).__name__}")
    print(f"  Message: {file_error}")
    print(f"  Filepath: {file_error.filepath}")
    print(f"  Error Code: {file_error.error_code}")
    print(f"  Context: {file_error.context}")
    print()
    
    # Parameter error with context
    param_error = GPRParameterError("Width must be positive", "input_width", -20)
    print(f"Parameter Error:")
    print(f"  Type: {type(param_error).__name__}")
    print(f"  Message: {param_error}")
    print(f"  Parameter: {param_error.parameter_name}")
    print(f"  Error Code: {param_error.error_code}")
    print()
    
    # Format error with supported formats
    format_error = GPRUnsupportedFormatError("webp", ["gpr", "dng", "raw"])
    print(f"Format Error:")
    print(f"  Type: {type(format_error).__name__}")
    print(f"  Message: {format_error}")
    print(f"  Format: {format_error.format_name}")
    print(f"  Supported: {format_error.supported_formats}")
    print()


def demonstrate_flexible_error_handling():
    """Demonstrate flexible error handling using the hierarchy."""
    print("\n🔹 Flexible Error Handling Demonstration")
    print("=" * 50)
    
    # Simulate different types of errors
    errors_to_handle = [
        GPRFileNotFoundError("/missing.gpr"),
        GPRFilePermissionError("/protected.gpr", "write"),
        GPRMemoryError("Allocation failed", 1024*1024*1024),
        GPRParameterError("Invalid width", "input_width"),
        GPRConversionError("Conversion failed"),
        GPRBitstreamError(1, "Underflow"),
    ]
    
    # Handle them with different levels of specificity
    print("Handling errors with different catch levels:")
    print()
    
    for error in errors_to_handle:
        print(f"Error: {type(error).__name__} - {error}")
        
        # Specific error type handling
        if isinstance(error, GPRFileError):
            print("  → Handled as file error: Check file path and permissions")
        elif isinstance(error, GPRMemoryError):
            print("  → Handled as memory error: Reduce memory usage or increase available memory")
        elif isinstance(error, GPRParameterError):
            print("  → Handled as parameter error: Check input parameter values")
        elif isinstance(error, GPRBitstreamError):
            print("  → Handled as bitstream error: Check input data format")
        elif isinstance(error, GPRError):
            print("  → Handled as general GPR error: Check GPR operation")
        else:
            print("  → Unhandled error type")
        
        print()


def demonstrate_error_message_quality():
    """Demonstrate that error messages are clear and actionable."""
    print("\n🔹 Error Message Quality Demonstration")
    print("=" * 50)
    
    test_scenarios = [
        {
            "scenario": "Missing input file",
            "error": GPRFileNotFoundError("/path/to/input.gpr"),
            "actionable_advice": "Verify the file path exists and is accessible"
        },
        {
            "scenario": "Invalid parameter type",
            "error": GPRParameterError("dtype must be 'uint16' or 'float32', got 'int8'", "dtype"),
            "actionable_advice": "Use supported dtype values"
        },
        {
            "scenario": "Unsupported output format",
            "error": GPRUnsupportedFormatError("webp", ["gpr", "dng", "raw"]),
            "actionable_advice": "Choose a supported output format"
        },
        {
            "scenario": "Memory allocation failure",
            "error": GPRMemoryError("Failed to allocate 2GB buffer", 2*1024*1024*1024),
            "actionable_advice": "Reduce image size or increase available memory"
        },
    ]
    
    for scenario in test_scenarios:
        print(f"Scenario: {scenario['scenario']}")
        print(f"  Error: {scenario['error']}")
        print(f"  Advice: {scenario['actionable_advice']}")
        print()


def main():
    """Run all demonstrations."""
    print("Python GPR Error Handling System Demonstration")
    print("=" * 60)
    print()
    print("This demonstration shows the comprehensive error handling")
    print("and exception mapping system implemented for the Python GPR library.")
    
    try:
        demonstrate_exception_hierarchy()
        demonstrate_error_code_mapping()
        demonstrate_file_error_creation()
        demonstrate_error_context_information()
        demonstrate_flexible_error_handling()
        demonstrate_error_message_quality()
        
        print("\n🎉 Error Handling System Demonstration Complete!")
        print()
        print("Key Features Demonstrated:")
        print("✅ Comprehensive exception hierarchy")
        print("✅ Automatic error code mapping")
        print("✅ Rich error context information")
        print("✅ Flexible error handling patterns")
        print("✅ Clear and actionable error messages")
        print("✅ Proper inheritance for selective error handling")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())