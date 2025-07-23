#!/usr/bin/env python3
"""
Demonstration of GPR Parameters Dict Interface

This script demonstrates the new dictionary-like interface for GPR parameters,
including validation, error handling, and all the dict-like methods.
"""

import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent / "src"))

from python_gpr.conversion import GPRParameters


def main():
    print("=== GPR Parameters Dict Interface Demo ===\n")
    
    # Basic creation and access
    print("1. Basic creation and dictionary access:")
    params = GPRParameters()
    print(f"Default quality: {params['quality']}")
    print(f"Default input_width: {params['input_width']}")
    
    # Setting parameters
    params['input_width'] = 1920
    params['input_height'] = 1080
    params['fast_encoding'] = True
    print(f"After setting - width: {params['input_width']}, height: {params['input_height']}, fast: {params['fast_encoding']}")
    print()
    
    # Creation with kwargs
    print("2. Creation with keyword arguments:")
    custom_params = GPRParameters(
        quality=10,
        input_width=3840,
        input_height=2160,
        fast_encoding=True,
        enable_preview=True
    )
    print(f"Custom params: {custom_params}")
    print()
    
    # Dictionary-like operations
    print("3. Dictionary-like operations:")
    print(f"'quality' in params: {'quality' in custom_params}")
    print(f"'invalid_param' in params: {'invalid_param' in custom_params}")
    print(f"Number of parameters: {len(custom_params)}")
    print()
    
    # Iteration
    print("4. Parameter iteration:")
    print("All parameter names:")
    for param_name in custom_params:
        print(f"  - {param_name}")
    print()
    
    print("All parameter values:")
    for param_name, value in custom_params.items():
        print(f"  {param_name}: {value}")
    print()
    
    # Dict methods
    print("5. Dictionary methods:")
    quality = custom_params.get('quality', 'not found')
    invalid = custom_params.get('invalid_param', 'default_value')
    print(f"get('quality'): {quality}")
    print(f"get('invalid_param', 'default'): {invalid}")
    print()
    
    # Copy and update
    print("6. Copy and update operations:")
    params_copy = custom_params.copy()
    print(f"Original quality: {custom_params['quality']}")
    
    params_copy['quality'] = 8
    print(f"Copy quality after modification: {params_copy['quality']}")
    print(f"Original quality (unchanged): {custom_params['quality']}")
    
    # Update from dict
    params_copy.update({'subband_count': 6, 'progressive': True})
    print(f"After update - subband_count: {params_copy['subband_count']}, progressive: {params_copy['progressive']}")
    print()
    
    # Backwards compatibility
    print("7. Backwards compatibility (property access):")
    params_copy.quality = 5
    print(f"Set via property: params.quality = 5")
    print(f"Access via dict: params['quality'] = {params_copy['quality']}")
    print()
    
    # Validation examples
    print("8. Parameter validation:")
    try:
        test_params = GPRParameters()
        test_params['quality'] = 15  # Invalid - above max
    except ValueError as e:
        print(f"Value error caught: {e}")
    
    try:
        test_params['quality'] = "high"  # Invalid - wrong type
    except TypeError as e:
        print(f"Type error caught: {e}")
    
    try:
        test_params['invalid_param'] = 42  # Invalid - unknown parameter
    except KeyError as e:
        print(f"Key error caught: {e}")
    print()
    
    # Parameter information
    print("9. Parameter information:")
    print("Available parameters:")
    all_params = GPRParameters.get_all_parameters()
    for name, info in all_params.items():
        type_name = info['type'].__name__
        default = info['default']
        print(f"  {name}: {type_name} (default: {default})")
    print()
    
    # Convert to dict
    print("10. Convert to dictionary:")
    param_dict = custom_params.to_dict()
    print("Parameters as dictionary:")
    for key, value in param_dict.items():
        print(f"  {key}: {value}")
    print()
    
    print("=== Demo complete! ===")


if __name__ == "__main__":
    main()