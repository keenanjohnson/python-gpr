"""
Test the GPR parameters dict-like interface.

This test module verifies that the GPRParameters class provides proper
dict-like functionality with validation and error handling.
"""

import unittest
import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from python_gpr.conversion import GPRParameters


class TestGPRParametersDict(unittest.TestCase):
    """Test the GPRParameters dict-like interface."""
    
    def test_basic_creation(self):
        """Test basic parameter creation."""
        params = GPRParameters()
        self.assertIsInstance(params, GPRParameters)
        
        # Test default values
        self.assertEqual(params['quality'], 12)
        self.assertEqual(params['subband_count'], 4)
        self.assertEqual(params['progressive'], False)
        self.assertEqual(params['input_width'], 0)
        self.assertEqual(params['input_height'], 0)
        self.assertEqual(params['fast_encoding'], False)
    
    def test_creation_with_kwargs(self):
        """Test parameter creation with keyword arguments."""
        params = GPRParameters(quality=10, input_width=1920, fast_encoding=True)
        self.assertEqual(params['quality'], 10)
        self.assertEqual(params['input_width'], 1920)
        self.assertEqual(params['fast_encoding'], True)
        # Defaults should still be set
        self.assertEqual(params['subband_count'], 4)
    
    def test_dict_like_access(self):
        """Test dictionary-like access patterns."""
        params = GPRParameters()
        
        # Test __getitem__ and __setitem__
        params['quality'] = 8
        self.assertEqual(params['quality'], 8)
        
        params['input_width'] = 1920
        self.assertEqual(params['input_width'], 1920)
        
        # Test __contains__
        self.assertIn('quality', params)
        self.assertIn('input_width', params)
        self.assertNotIn('invalid_param', params)
        
        # Test __len__
        self.assertEqual(len(params), len(GPRParameters._VALID_PARAMS))
    
    def test_iteration(self):
        """Test parameter iteration."""
        params = GPRParameters()
        
        # Test __iter__
        param_names = list(params)
        expected_names = list(GPRParameters._VALID_PARAMS.keys())
        self.assertEqual(set(param_names), set(expected_names))
        
        # Test keys(), values(), items()
        self.assertEqual(set(params.keys()), set(expected_names))
        
        values = list(params.values())
        self.assertEqual(len(values), len(expected_names))
        
        items = list(params.items())
        self.assertEqual(len(items), len(expected_names))
        for key, value in items:
            self.assertEqual(params[key], value)
    
    def test_dict_methods(self):
        """Test additional dict-like methods."""
        params = GPRParameters(quality=10)
        
        # Test get()
        self.assertEqual(params.get('quality'), 10)
        self.assertEqual(params.get('invalid_param', 'default'), 'default')
        self.assertIsNone(params.get('invalid_param'))
        
        # Test update()
        updates = {'quality': 8, 'input_width': 1920}
        params.update(updates)
        self.assertEqual(params['quality'], 8)
        self.assertEqual(params['input_width'], 1920)
        
        # Test copy()
        params_copy = params.copy()
        self.assertEqual(params_copy['quality'], 8)
        self.assertEqual(params_copy['input_width'], 1920)
        
        # Modify copy, original should be unchanged
        params_copy['quality'] = 5
        self.assertEqual(params['quality'], 8)  # Original unchanged
        self.assertEqual(params_copy['quality'], 5)  # Copy changed
    
    def test_type_validation(self):
        """Test parameter type validation."""
        params = GPRParameters()
        
        # Valid types should work
        params['quality'] = 10
        params['fast_encoding'] = True
        params['input_width'] = 1920
        
        # Invalid types should raise TypeError
        with self.assertRaises(TypeError):
            params['quality'] = "invalid"  # string instead of int
        
        with self.assertRaises(TypeError):
            params['fast_encoding'] = "true"  # string instead of bool
        
        with self.assertRaises(TypeError):
            params['input_width'] = 3.14  # float instead of int
    
    def test_value_validation(self):
        """Test parameter value validation."""
        params = GPRParameters()
        
        # Valid values should work
        params['quality'] = 1
        params['quality'] = 12
        params['subband_count'] = 4
        params['input_width'] = 0
        params['input_width'] = 1920
        
        # Invalid values should raise ValueError
        with self.assertRaises(ValueError):
            params['quality'] = 0  # Below minimum
        
        with self.assertRaises(ValueError):
            params['quality'] = 13  # Above maximum
        
        with self.assertRaises(ValueError):
            params['subband_count'] = 0  # Below minimum
        
        with self.assertRaises(ValueError):
            params['subband_count'] = 9  # Above maximum
        
        with self.assertRaises(ValueError):
            params['input_width'] = -1  # Negative value
    
    def test_invalid_parameter_names(self):
        """Test handling of invalid parameter names."""
        params = GPRParameters()
        
        # Invalid parameter should raise KeyError
        with self.assertRaises(KeyError):
            _ = params['invalid_param']
        
        with self.assertRaises(KeyError):
            params['invalid_param'] = 42
        
        # Invalid parameter in constructor should raise KeyError
        with self.assertRaises(KeyError):
            GPRParameters(invalid_param=42)
    
    def test_backwards_compatibility(self):
        """Test backwards compatibility with property access."""
        params = GPRParameters(quality=10, subband_count=3, progressive=True)
        
        # Property access should work
        self.assertEqual(params.quality, 10)
        self.assertEqual(params.subband_count, 3)
        self.assertEqual(params.progressive, True)
        
        # Property setting should work
        params.quality = 8
        params.subband_count = 5
        params.progressive = False
        
        self.assertEqual(params['quality'], 8)
        self.assertEqual(params['subband_count'], 5)
        self.assertEqual(params['progressive'], False)
    
    def test_to_dict_compatibility(self):
        """Test that to_dict() method works for backwards compatibility."""
        params = GPRParameters(quality=10, subband_count=3, progressive=True)
        param_dict = params.to_dict()
        
        self.assertIsInstance(param_dict, dict)
        self.assertEqual(param_dict['quality'], 10)
        self.assertEqual(param_dict['subband_count'], 3)
        self.assertEqual(param_dict['progressive'], True)
        
        # All parameters should be included
        self.assertEqual(len(param_dict), len(GPRParameters._VALID_PARAMS))
    
    def test_parameter_info_methods(self):
        """Test parameter information methods."""
        # Test get_parameter_info
        info = GPRParameters.get_parameter_info('quality')
        self.assertEqual(info['type'], int)
        self.assertEqual(info['default'], 12)
        
        # Test get_all_parameters
        all_params = GPRParameters.get_all_parameters()
        self.assertIsInstance(all_params, dict)
        self.assertEqual(len(all_params), len(GPRParameters._VALID_PARAMS))
        
        for param_name in GPRParameters._VALID_PARAMS:
            self.assertIn(param_name, all_params)
            self.assertIn('type', all_params[param_name])
            self.assertIn('default', all_params[param_name])
    
    def test_string_representation(self):
        """Test string representation of parameters."""
        params = GPRParameters(quality=10, input_width=1920)
        repr_str = repr(params)
        
        self.assertIn('GPRParameters', repr_str)
        self.assertIn('quality=10', repr_str)
        self.assertIn('input_width=1920', repr_str)


if __name__ == '__main__':
    unittest.main()