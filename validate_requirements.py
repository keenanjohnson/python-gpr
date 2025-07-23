#!/usr/bin/env python3
"""
Comprehensive validation that all GPR Parameters requirements are satisfied.

This script validates all acceptance criteria from the GitHub issue:
- Parameters can be set using dictionary syntax
- Invalid parameter values raise appropriate exceptions  
- Default parameters work correctly
- All GPR library parameters are accessible
"""

import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent / "src"))

from python_gpr.conversion import GPRParameters


def test_acceptance_criteria():
    """Test all acceptance criteria from the issue."""
    print("🧪 Testing GPR Parameters Implementation against Acceptance Criteria\n")
    
    # ✅ Criterion 1: Parameters can be set using dictionary syntax
    print("1. Parameters can be set using dictionary syntax")
    params = GPRParameters()
    
    # Core GPR parameters
    params['input_width'] = 1920
    params['input_height'] = 1080
    params['input_pitch'] = 7680
    params['fast_encoding'] = True
    params['compute_md5sum'] = False
    params['enable_preview'] = True
    
    # Legacy parameters
    params['quality'] = 10
    params['subband_count'] = 6
    params['progressive'] = False
    
    assert params['input_width'] == 1920
    assert params['fast_encoding'] == True
    assert params['quality'] == 10
    print("   ✅ Dictionary syntax works for all parameter types")
    
    # ✅ Criterion 2: Invalid parameter values raise appropriate exceptions
    print("\n2. Invalid parameter values raise appropriate exceptions")
    
    # Test invalid parameter names
    try:
        params['invalid_parameter'] = 42
        assert False, "Should have raised KeyError"
    except KeyError as e:
        assert "Invalid parameter" in str(e)
        print("   ✅ Invalid parameter names raise KeyError with helpful message")
    
    # Test invalid types
    try:
        params['quality'] = "high"  # String instead of int
        assert False, "Should have raised TypeError"
    except TypeError as e:
        assert "must be of type int" in str(e)
        print("   ✅ Invalid types raise TypeError with helpful message")
    
    # Test invalid values
    try:
        params['quality'] = 15  # Above maximum
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must be between 1 and 12" in str(e)
        print("   ✅ Invalid values raise ValueError with helpful message")
    
    try:
        params['input_width'] = -100  # Negative value
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must be non-negative" in str(e)
        print("   ✅ Negative values for dimension parameters raise ValueError")
    
    # ✅ Criterion 3: Default parameters work correctly
    print("\n3. Default parameters work correctly")
    default_params = GPRParameters()
    
    expected_defaults = {
        'input_width': 0,
        'input_height': 0,
        'input_pitch': 0,
        'fast_encoding': False,
        'compute_md5sum': False,
        'enable_preview': False,
        'quality': 12,
        'subband_count': 4,
        'progressive': False,
    }
    
    for param_name, expected_value in expected_defaults.items():
        actual_value = default_params[param_name]
        assert actual_value == expected_value, f"{param_name}: expected {expected_value}, got {actual_value}"
    
    print(f"   ✅ All {len(expected_defaults)} parameters have correct default values")
    
    # ✅ Criterion 4: All GPR library parameters are accessible
    print("\n4. All GPR library parameters are accessible")
    
    # Core parameters from gpr_parameters struct
    core_gpr_params = [
        'input_width',      # Width of input source in pixels
        'input_height',     # Height of input source in pixels  
        'input_pitch',      # Pitch of input source in pixels
        'fast_encoding',    # Enable fast encoding mode
        'compute_md5sum',   # Compute MD5 checksum
        'enable_preview',   # Enable preview image generation
    ]
    
    # Legacy parameters for backwards compatibility
    legacy_params = [
        'quality',          # Legacy quality parameter
        'subband_count',    # Legacy subband count parameter
        'progressive',      # Legacy progressive encoding parameter
    ]
    
    all_expected_params = core_gpr_params + legacy_params
    
    for param_name in all_expected_params:
        # Test parameter exists
        assert param_name in default_params, f"Parameter {param_name} not accessible"
        
        # Test parameter can be read
        value = default_params[param_name]
        
        # Test parameter can be written
        if param_name == 'quality':
            default_params[param_name] = 8
            assert default_params[param_name] == 8
        elif param_name == 'subband_count':
            default_params[param_name] = 6
            assert default_params[param_name] == 6
        elif param_name.startswith('input'):
            default_params[param_name] = 1920
            assert default_params[param_name] == 1920
        else:
            default_params[param_name] = True
            assert default_params[param_name] == True
    
    print(f"   ✅ All {len(core_gpr_params)} core GPR parameters accessible")
    print(f"   ✅ All {len(legacy_params)} legacy parameters accessible for backwards compatibility")
    
    # Bonus: Test additional dict-like functionality
    print("\n5. Additional dict-like functionality (bonus)")
    
    params = GPRParameters(quality=10, input_width=1920)
    
    # Test iteration
    param_names = list(params)
    assert len(param_names) == len(all_expected_params)
    print("   ✅ Parameter iteration works")
    
    # Test dictionary methods
    assert params.get('quality') == 10
    assert params.get('nonexistent', 'default') == 'default'
    assert len(params) == len(all_expected_params)
    assert 'quality' in params
    assert 'nonexistent' not in params
    print("   ✅ Dictionary methods (get, len, in) work")
    
    # Test copy and update
    params_copy = params.copy()
    params_copy.update({'quality': 8, 'fast_encoding': True})
    assert params['quality'] == 10  # Original unchanged
    assert params_copy['quality'] == 8  # Copy changed
    print("   ✅ Copy and update operations work")
    
    # Test backwards compatibility
    params.quality = 5  # Property access
    assert params['quality'] == 5  # Dict access
    print("   ✅ Backwards compatibility with property access")


def test_parameter_documentation():
    """Test that parameter documentation is comprehensive."""
    print("\n📚 Testing parameter documentation")
    
    all_params = GPRParameters.get_all_parameters()
    
    for param_name, info in all_params.items():
        assert 'type' in info, f"Missing type info for {param_name}"
        assert 'default' in info, f"Missing default info for {param_name}"
        
        # Test individual parameter info
        individual_info = GPRParameters.get_parameter_info(param_name)
        assert individual_info['type'] == info['type']
        assert individual_info['default'] == info['default']
    
    print(f"   ✅ Documentation available for all {len(all_params)} parameters")
    print("   ✅ Type and default information provided for each parameter")


def main():
    """Run all validation tests."""
    try:
        test_acceptance_criteria()
        test_parameter_documentation()
        
        print("\n" + "="*60)
        print("🎉 ALL REQUIREMENTS SATISFIED! 🎉")
        print("="*60)
        print("\nSummary of implemented features:")
        print("✅ Dictionary syntax for parameter access (params['key'] = value)")
        print("✅ Comprehensive parameter validation with clear error messages")
        print("✅ Correct default values for all parameters")
        print("✅ All GPR library parameters accessible")
        print("✅ Full dict-like interface (iteration, copy, update, etc.)")
        print("✅ Backwards compatibility with existing property access")
        print("✅ Parameter documentation and introspection")
        print("✅ Type safety and value range validation")
        print("\nThe GPR parameters binding with Python dict interface is complete!")
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()