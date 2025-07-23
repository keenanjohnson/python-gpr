"""
Comprehensive validation that all GPR Parameters requirements are satisfied.

This test module validates all acceptance criteria from the GitHub issue:
- Parameters can be set using dictionary syntax
- Invalid parameter values raise appropriate exceptions  
- Default parameters work correctly
- All GPR library parameters are accessible
"""

import unittest
import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from python_gpr.conversion import GPRParameters


class TestAcceptanceCriteria(unittest.TestCase):
    """Test all acceptance criteria from the GitHub issue."""

    def test_criterion_1_dictionary_syntax(self):
        """Test that parameters can be set using dictionary syntax."""
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
        
        # Verify values are set correctly
        self.assertEqual(params['input_width'], 1920)
        self.assertEqual(params['input_height'], 1080)
        self.assertEqual(params['input_pitch'], 7680)
        self.assertTrue(params['fast_encoding'])
        self.assertFalse(params['compute_md5sum'])
        self.assertTrue(params['enable_preview'])
        self.assertEqual(params['quality'], 10)
        self.assertEqual(params['subband_count'], 6)
        self.assertFalse(params['progressive'])

    def test_criterion_2_invalid_parameter_exceptions(self):
        """Test that invalid parameter values raise appropriate exceptions."""
        params = GPRParameters()
        
        # Test invalid parameter names
        with self.assertRaises(KeyError) as cm:
            params['invalid_parameter'] = 42
        self.assertIn("Invalid parameter", str(cm.exception))
        
        # Test invalid types
        with self.assertRaises(TypeError) as cm:
            params['quality'] = "high"  # String instead of int
        self.assertIn("must be of type int", str(cm.exception))
        
        # Test invalid values - quality out of range
        with self.assertRaises(ValueError) as cm:
            params['quality'] = 15  # Above maximum
        self.assertIn("must be between 1 and 12", str(cm.exception))
        
        # Test invalid values - negative dimensions
        with self.assertRaises(ValueError) as cm:
            params['input_width'] = -100  # Negative value
        self.assertIn("must be non-negative", str(cm.exception))

    def test_criterion_3_default_parameters(self):
        """Test that default parameters work correctly."""
        params = GPRParameters()
        
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
            with self.subTest(param=param_name):
                actual_value = params[param_name]
                self.assertEqual(
                    actual_value, expected_value,
                    f"{param_name}: expected {expected_value}, got {actual_value}"
                )

    def test_criterion_4_all_gpr_parameters_accessible(self):
        """Test that all GPR library parameters are accessible."""
        params = GPRParameters()
        
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
        
        # Test each parameter
        for param_name in all_expected_params:
            with self.subTest(param=param_name):
                # Test parameter exists
                self.assertIn(param_name, params, f"Parameter {param_name} not accessible")
                
                # Test parameter can be read
                value = params[param_name]
                self.assertIsNotNone(value if value else True)  # Handle 0 and False values
                
                # Test parameter can be written with valid values
                if param_name == 'quality':
                    params[param_name] = 8
                    self.assertEqual(params[param_name], 8)
                elif param_name == 'subband_count':
                    params[param_name] = 6
                    self.assertEqual(params[param_name], 6)
                elif param_name.startswith('input'):
                    params[param_name] = 1920
                    self.assertEqual(params[param_name], 1920)
                else:  # Boolean parameters
                    params[param_name] = True
                    self.assertTrue(params[param_name])


class TestAdditionalDictFunctionality(unittest.TestCase):
    """Test additional dict-like functionality (bonus features)."""

    def test_iteration(self):
        """Test parameter iteration."""
        params = GPRParameters(quality=10, input_width=1920)
        
        # Test iteration returns all parameter names
        param_names = list(params)
        expected_count = 9  # All parameters should be present
        self.assertEqual(len(param_names), expected_count)
        
        # Test specific parameters are in iteration
        self.assertIn('quality', param_names)
        self.assertIn('input_width', param_names)
        self.assertIn('fast_encoding', param_names)

    def test_dictionary_methods(self):
        """Test dictionary methods (get, len, in)."""
        params = GPRParameters(quality=10)
        
        # Test get method
        self.assertEqual(params.get('quality'), 10)
        self.assertEqual(params.get('nonexistent', 'default'), 'default')
        
        # Test len
        expected_count = 9  # All parameters should be counted
        self.assertEqual(len(params), expected_count)
        
        # Test 'in' operator
        self.assertIn('quality', params)
        self.assertNotIn('nonexistent', params)

    def test_copy_and_update(self):
        """Test copy and update operations."""
        params = GPRParameters(quality=10, input_width=1920)
        
        # Test copy
        params_copy = params.copy()
        self.assertEqual(params_copy['quality'], 10)
        self.assertEqual(params_copy['input_width'], 1920)
        
        # Test update
        params_copy.update({'quality': 8, 'fast_encoding': True})
        
        # Original should be unchanged
        self.assertEqual(params['quality'], 10)
        self.assertFalse(params['fast_encoding'])
        
        # Copy should be changed
        self.assertEqual(params_copy['quality'], 8)
        self.assertTrue(params_copy['fast_encoding'])

    def test_backwards_compatibility(self):
        """Test backwards compatibility with property access."""
        params = GPRParameters()
        
        # Test property access works
        params.quality = 5
        self.assertEqual(params.quality, 5)
        
        # Test dict access sees property changes
        self.assertEqual(params['quality'], 5)
        
        # Test property access sees dict changes
        params['quality'] = 8
        self.assertEqual(params.quality, 8)


class TestParameterDocumentation(unittest.TestCase):
    """Test parameter documentation and introspection."""

    def test_parameter_documentation_comprehensive(self):
        """Test that parameter documentation is comprehensive."""
        all_params = GPRParameters.get_all_parameters()
        
        # Should have documentation for all parameters
        expected_params = [
            'input_width', 'input_height', 'input_pitch',
            'fast_encoding', 'compute_md5sum', 'enable_preview',
            'quality', 'subband_count', 'progressive'
        ]
        
        for param_name in expected_params:
            with self.subTest(param=param_name):
                self.assertIn(param_name, all_params, f"Missing documentation for {param_name}")
                
                info = all_params[param_name]
                self.assertIn('type', info, f"Missing type info for {param_name}")
                self.assertIn('default', info, f"Missing default info for {param_name}")

    def test_individual_parameter_info(self):
        """Test getting individual parameter information."""
        all_params = GPRParameters.get_all_parameters()
        
        for param_name in all_params.keys():
            with self.subTest(param=param_name):
                # Test individual parameter info matches bulk info
                individual_info = GPRParameters.get_parameter_info(param_name)
                bulk_info = all_params[param_name]
                
                self.assertEqual(individual_info['type'], bulk_info['type'])
                self.assertEqual(individual_info['default'], bulk_info['default'])


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios that combine multiple features."""

    def test_full_workflow_scenario(self):
        """Test a complete workflow using the parameters."""
        # Create parameters with some initial values
        params = GPRParameters(quality=10, input_width=1920, input_height=1080)
        
        # Modify using dict syntax
        params['fast_encoding'] = True
        params['compute_md5sum'] = True
        
        # Verify all values
        self.assertEqual(params['quality'], 10)
        self.assertEqual(params['input_width'], 1920)
        self.assertEqual(params['input_height'], 1080)
        self.assertTrue(params['fast_encoding'])
        self.assertTrue(params['compute_md5sum'])
        
        # Test iteration and verification
        param_dict = dict(params.items())
        self.assertEqual(param_dict['quality'], 10)
        self.assertEqual(param_dict['input_width'], 1920)
        
        # Test copy for backup
        backup_params = params.copy()
        
        # Modify original
        params['quality'] = 8
        
        # Verify backup is unchanged
        self.assertEqual(backup_params['quality'], 10)
        self.assertEqual(params['quality'], 8)

    def test_error_handling_scenarios(self):
        """Test various error conditions."""
        params = GPRParameters()
        
        # Test multiple validation errors
        error_cases = [
            ('invalid_param', 42, KeyError),
            ('quality', 'high', TypeError), 
            ('quality', 15, ValueError),
            ('input_width', -100, ValueError),
            ('subband_count', 10, ValueError),  # Out of range
        ]
        
        for param_name, value, expected_error in error_cases:
            with self.subTest(param=param_name, value=value):
                with self.assertRaises(expected_error):
                    params[param_name] = value


if __name__ == '__main__':
    unittest.main(verbosity=2)