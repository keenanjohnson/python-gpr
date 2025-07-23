"""
Format conversion utilities for Python-GPR.

This module provides functions for converting between different image formats
supported by the GPR library, including GPR, DNG, RAW, PPM, and JPG.
"""

from typing import Optional, Dict, Any, Union, Iterator
import os


class GPRParameters:
    """
    Configuration parameters for GPR conversion operations.
    
    This class encapsulates the various parameters that can be used to
    control GPR encoding and decoding operations. It provides a dict-like
    interface for easy parameter access and modification.
    
    Supported parameters:
    - input_width (int): Width of input source in pixels
    - input_height (int): Height of input source in pixels  
    - input_pitch (int): Pitch of input source in pixels
    - fast_encoding (bool): Enable fast encoding mode
    - compute_md5sum (bool): Compute MD5 checksum during processing
    - enable_preview (bool): Enable preview image generation
    - quality (int): Legacy quality parameter (1-12, default: 12)
    - subband_count (int): Legacy subband count parameter (default: 4)
    - progressive (bool): Legacy progressive encoding parameter (default: False)
    """
    
    # Define valid parameters with their types and default values
    _VALID_PARAMS = {
        # Core GPR parameters from gpr_parameters struct
        'input_width': (int, 0),
        'input_height': (int, 0),
        'input_pitch': (int, 0),
        'fast_encoding': (bool, False),
        'compute_md5sum': (bool, False),
        'enable_preview': (bool, False),
        # Legacy parameters for backwards compatibility
        'quality': (int, 12),
        'subband_count': (int, 4),
        'progressive': (bool, False),
    }
    
    def __init__(self, **kwargs):
        """
        Initialize GPR parameters.
        
        Args:
            **kwargs: Parameter values to set. Must be valid parameter names.
            
        Raises:
            ValueError: If an invalid parameter name is provided
            TypeError: If a parameter value has an invalid type
        """
        # Initialize all parameters with defaults
        self._params = {}
        for param_name, (param_type, default_value) in self._VALID_PARAMS.items():
            self._params[param_name] = default_value
        
        # Set any provided parameters
        for key, value in kwargs.items():
            self[key] = value  # Use __setitem__ for validation
    
    def __getitem__(self, key: str) -> Any:
        """Get parameter value using dictionary syntax."""
        if key not in self._VALID_PARAMS:
            raise KeyError(f"Invalid parameter: {key}. Valid parameters: {list(self._VALID_PARAMS.keys())}")
        return self._params[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set parameter value using dictionary syntax with validation."""
        if key not in self._VALID_PARAMS:
            raise KeyError(f"Invalid parameter: {key}. Valid parameters: {list(self._VALID_PARAMS.keys())}")
        
        expected_type, _ = self._VALID_PARAMS[key]
        
        # Type validation
        if not isinstance(value, expected_type):
            raise TypeError(f"Parameter {key} must be of type {expected_type.__name__}, got {type(value).__name__}")
        
        # Value validation for specific parameters
        if key == 'quality' and not (1 <= value <= 12):
            raise ValueError(f"Parameter 'quality' must be between 1 and 12, got {value}")
        elif key == 'subband_count' and not (1 <= value <= 8):
            raise ValueError(f"Parameter 'subband_count' must be between 1 and 8, got {value}")
        elif key in ['input_width', 'input_height', 'input_pitch'] and value < 0:
            raise ValueError(f"Parameter '{key}' must be non-negative, got {value}")
        
        self._params[key] = value
    
    def __contains__(self, key: str) -> bool:
        """Check if parameter exists using 'in' operator."""
        return key in self._VALID_PARAMS
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over parameter names."""
        return iter(self._VALID_PARAMS.keys())
    
    def __len__(self) -> int:
        """Get number of parameters."""
        return len(self._VALID_PARAMS)
    
    def __repr__(self) -> str:
        """String representation of parameters."""
        params_str = ", ".join(f"{k}={v}" for k, v in self._params.items())
        return f"GPRParameters({params_str})"
    
    def keys(self) -> Iterator[str]:
        """Get parameter names (dict-like interface)."""
        return iter(self._VALID_PARAMS.keys())
    
    def values(self) -> Iterator[Any]:
        """Get parameter values (dict-like interface)."""
        for key in self._VALID_PARAMS:
            yield self._params[key]
    
    def items(self) -> Iterator[tuple]:
        """Get parameter (name, value) pairs (dict-like interface)."""
        for key in self._VALID_PARAMS:
            yield (key, self._params[key])
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get parameter value with optional default (dict-like interface)."""
        if key in self._VALID_PARAMS:
            return self._params[key]
        return default
    
    def update(self, other: Union[Dict[str, Any], 'GPRParameters']) -> None:
        """Update parameters from another dict or GPRParameters object."""
        if isinstance(other, GPRParameters):
            for key in self._VALID_PARAMS:
                self._params[key] = other._params[key]
        elif isinstance(other, dict):
            for key, value in other.items():
                self[key] = value  # Use __setitem__ for validation
        else:
            raise TypeError("update() requires a dict or GPRParameters object")
    
    def copy(self) -> 'GPRParameters':
        """Create a copy of these parameters."""
        return GPRParameters(**self._params)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary representation."""
        return self._params.copy()
    
    @classmethod
    def get_parameter_info(cls, param_name: str) -> Dict[str, Any]:
        """
        Get information about a specific parameter.
        
        Args:
            param_name: Name of the parameter
            
        Returns:
            Dictionary with parameter type and default value
            
        Raises:
            KeyError: If parameter name is invalid
        """
        if param_name not in cls._VALID_PARAMS:
            raise KeyError(f"Invalid parameter: {param_name}")
        
        param_type, default_value = cls._VALID_PARAMS[param_name]
        return {
            'type': param_type,
            'default': default_value,
        }
    
    @classmethod
    def get_all_parameters(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about all available parameters."""
        return {
            name: cls.get_parameter_info(name) 
            for name in cls._VALID_PARAMS
        }
    
    # Property access for backwards compatibility
    @property
    def quality(self) -> int:
        """Legacy quality parameter for backwards compatibility."""
        return self._params['quality']
    
    @quality.setter
    def quality(self, value: int) -> None:
        """Legacy quality parameter setter for backwards compatibility."""
        self['quality'] = value
    
    @property
    def subband_count(self) -> int:
        """Legacy subband_count parameter for backwards compatibility."""
        return self._params['subband_count']
    
    @subband_count.setter
    def subband_count(self, value: int) -> None:
        """Legacy subband_count parameter setter for backwards compatibility."""
        self['subband_count'] = value
    
    @property
    def progressive(self) -> bool:
        """Legacy progressive parameter for backwards compatibility."""
        return self._params['progressive']
    
    @progressive.setter
    def progressive(self, value: bool) -> None:
        """Legacy progressive parameter setter for backwards compatibility."""
        self['progressive'] = value


def convert_gpr_to_dng(input_path: str, output_path: str, 
                       parameters: Optional[GPRParameters] = None) -> None:
    """
    Convert GPR file to DNG format.
    
    Args:
        input_path: Path to input GPR file
        output_path: Path for output DNG file  
        parameters: Optional conversion parameters (currently unused)
        
    Raises:
        FileNotFoundError: If input file does not exist
        ValueError: If conversion fails
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    try:
        from ._core import convert_gpr_to_dng as _convert_gpr_to_dng
        from ._core import GPRConversionError
        
        _convert_gpr_to_dng(input_path, output_path)
    except ImportError:
        raise NotImplementedError("GPR C++ bindings not available - please build the extension module")
    except Exception as e:
        # Handle any C++ exceptions that get through
        if "GPRConversionError" in str(type(e)):
            raise ValueError(str(e)) from e
        else:
            raise ValueError(f"Conversion failed: {str(e)}") from e


def convert_dng_to_gpr(input_path: str, output_path: str,
                       parameters: Optional[GPRParameters] = None) -> None:
    """
    Convert DNG file to GPR format.
    
    Args:
        input_path: Path to input DNG file
        output_path: Path for output GPR file
        parameters: Optional conversion parameters (currently unused)
        
    Raises:
        FileNotFoundError: If input file does not exist
        ValueError: If conversion fails
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    try:
        from ._core import convert_dng_to_gpr as _convert_dng_to_gpr
        from ._core import GPRConversionError
        
        _convert_dng_to_gpr(input_path, output_path)
    except ImportError:
        raise NotImplementedError("GPR C++ bindings not available - please build the extension module")
    except Exception as e:
        # Handle any C++ exceptions that get through
        if "GPRConversionError" in str(type(e)):
            raise ValueError(str(e)) from e
        else:
            raise ValueError(f"Conversion failed: {str(e)}") from e


def convert_gpr_to_raw(input_path: str, output_path: str,
                       parameters: Optional[GPRParameters] = None) -> None:
    """
    Convert GPR file to RAW format.
    
    Args:
        input_path: Path to input GPR file (or DNG file)
        output_path: Path for output RAW file
        parameters: Optional conversion parameters (currently unused)
        
    Raises:
        FileNotFoundError: If input file does not exist
        ValueError: If conversion fails
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    try:
        from ._core import convert_gpr_to_raw as _convert_gpr_to_raw
        from ._core import GPRConversionError
        
        _convert_gpr_to_raw(input_path, output_path)
    except ImportError:
        raise NotImplementedError("GPR C++ bindings not available - please build the extension module")
    except Exception as e:
        # Handle any C++ exceptions that get through
        if "GPRConversionError" in str(type(e)):
            raise ValueError(str(e)) from e
        else:
            raise ValueError(f"Conversion failed: {str(e)}") from e


def convert_dng_to_dng(input_path: str, output_path: str,
                       parameters: Optional[GPRParameters] = None) -> None:
    """
    Convert DNG file to DNG format (reprocess).
    
    Args:
        input_path: Path to input DNG file
        output_path: Path for output DNG file
        parameters: Optional conversion parameters (currently unused)
        
    Raises:
        FileNotFoundError: If input file does not exist
        ValueError: If conversion fails
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    try:
        from ._core import convert_dng_to_dng as _convert_dng_to_dng
        from ._core import GPRConversionError
        
        _convert_dng_to_dng(input_path, output_path)
    except ImportError:
        raise NotImplementedError("GPR C++ bindings not available - please build the extension module")
    except Exception as e:
        # Handle any C++ exceptions that get through
        if "GPRConversionError" in str(type(e)):
            raise ValueError(str(e)) from e
        else:
            raise ValueError(f"Conversion failed: {str(e)}") from e


def detect_format(filepath: str) -> str:
    """
    Detect the format of an image file.
    
    Args:
        filepath: Path to the image file
        
    Returns:
        String indicating the detected format ('gpr', 'dng', 'raw', etc.)
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If format cannot be determined
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Simple format detection based on file extension
    # Will be replaced with proper format detection using GPR library
    ext = os.path.splitext(filepath)[1].lower()
    
    format_map = {
        '.gpr': 'gpr',
        '.dng': 'dng', 
        '.raw': 'raw',
        '.ppm': 'ppm',
        '.jpg': 'jpg',
        '.jpeg': 'jpg',
    }
    
    if ext in format_map:
        return format_map[ext]
    
    raise ValueError(f"Unknown format for file: {filepath}")


__all__ = [
    "GPRParameters",
    "convert_gpr_to_dng",
    "convert_dng_to_gpr", 
    "convert_gpr_to_raw",
    "convert_dng_to_dng",
    "detect_format",
]