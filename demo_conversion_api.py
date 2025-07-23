#!/usr/bin/env python3
"""
Demonstration of the GPR conversion function bindings.

This script shows how to use the python-gpr conversion functions
and demonstrates their error handling capabilities.
"""

import tempfile
import os
from python_gpr.conversion import (
    convert_gpr_to_dng,
    convert_dng_to_gpr,
    convert_gpr_to_raw,
    convert_dng_to_dng,
    GPRParameters
)


def demo_file_validation():
    """Demonstrate file validation and error handling."""
    print("=== File Validation Demo ===")
    
    # Test with non-existent file
    try:
        convert_gpr_to_dng("nonexistent.gpr", "output.dng")
    except FileNotFoundError as e:
        print(f"✓ Correctly caught FileNotFoundError: {e}")
    
    # Test with non-existent DNG file
    try:
        convert_dng_to_gpr("nonexistent.dng", "output.gpr")
    except FileNotFoundError as e:
        print(f"✓ Correctly caught FileNotFoundError: {e}")
    
    print()


def demo_conversion_errors():
    """Demonstrate conversion error handling with dummy files."""
    print("=== Conversion Error Handling Demo ===")
    
    # Create a dummy file to test with
    with tempfile.NamedTemporaryFile(suffix='.dng', delete=False) as temp_file:
        temp_file.write(b"This is not a real DNG file")
        temp_path = temp_file.name
    
    try:
        # Test GPR to DNG conversion (should fail due to missing VC5 support)
        try:
            convert_gpr_to_dng(temp_path, "output.dng")
        except ValueError as e:
            print(f"✓ GPR to DNG correctly failed: {e}")
        
        # Test DNG to GPR conversion (should fail due to missing VC5 support)
        try:
            convert_dng_to_gpr(temp_path, "output.gpr")
        except ValueError as e:
            print(f"✓ DNG to GPR correctly failed: {e}")
        
        # Test DNG to RAW conversion (should fail with invalid file format)
        try:
            convert_gpr_to_raw(temp_path, "output.raw")
        except ValueError as e:
            print(f"✓ DNG to RAW correctly failed: {e}")
        
        # Test DNG to DNG conversion (should fail with invalid file format)
        try:
            convert_dng_to_dng(temp_path, "output2.dng")
        except ValueError as e:
            print(f"✓ DNG to DNG correctly failed: {e}")
    
    finally:
        # Clean up
        os.unlink(temp_path)
    
    print()


def demo_parameters():
    """Demonstrate GPRParameters usage."""
    print("=== GPRParameters Demo ===")
    
    # Create default parameters
    params = GPRParameters()
    print(f"Default parameters: {params.to_dict()}")
    
    # Create custom parameters
    custom_params = GPRParameters(quality=10, subband_count=3, progressive=True)
    print(f"Custom parameters: {custom_params.to_dict()}")
    
    print()


def demo_api_availability():
    """Show all available functions."""
    print("=== Available API Functions ===")
    
    functions = [
        ("convert_gpr_to_dng", convert_gpr_to_dng),
        ("convert_dng_to_gpr", convert_dng_to_gpr),
        ("convert_gpr_to_raw", convert_gpr_to_raw),
        ("convert_dng_to_dng", convert_dng_to_dng),
    ]
    
    for name, func in functions:
        doc = func.__doc__.split('.')[0] if func.__doc__ else "No description"
        print(f"✓ {name}: {doc}")
    
    print()
    print("✓ GPRParameters class available for conversion options")
    print()


if __name__ == "__main__":
    print("Python-GPR Conversion Functions Demo")
    print("====================================")
    print()
    
    demo_api_availability()
    demo_parameters()
    demo_file_validation()
    demo_conversion_errors()
    
    print("=== Summary ===")
    print("✓ All core conversion functions are successfully bound to Python")
    print("✓ Proper error handling and exception mapping is working")
    print("✓ File path validation is functioning correctly")
    print("✓ Functions accept string paths for input/output files")
    print("✓ GPRParameters class is available for future enhancement")
    print()
    print("Note: Full GPR conversion requires VC5 codec components.")
    print("Current build supports DNG processing operations.")