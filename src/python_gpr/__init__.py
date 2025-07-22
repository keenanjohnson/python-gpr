"""
Python-GPR: Python bindings for the GPR (General Purpose Raw) image format library.

This package provides Python access to the GPR library developed by GoPro,
enabling conversion between GPR, DNG, RAW, PPM, and JPG image formats with
high-performance VC-5 wavelet compression.
"""

from typing import Optional, Dict, Any
import warnings

__version__ = "0.1.0"
__author__ = "Keenan Johnson"
__license__ = "MIT OR Apache-2.0"

# Try to import the native extension
try:
    from ._gpr_binding import *  # noqa: F401, F403
    _NATIVE_AVAILABLE = True
except ImportError as e:
    _NATIVE_AVAILABLE = False
    _import_error = e

def __getattr__(name: str) -> Any:
    """Lazy import fallback for when native extension is not available."""
    if not _NATIVE_AVAILABLE:
        raise ImportError(
            f"python-gpr native extension not available. "
            f"Original error: {_import_error}"
        ) from _import_error
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# High-level API functions that will be implemented
def convert_gpr_to_dng(
    input_path: str, 
    output_path: str, 
    parameters: Optional[Dict[str, Any]] = None
) -> None:
    """
    Convert GPR file to DNG format.
    
    Args:
        input_path: Path to input GPR file
        output_path: Path for output DNG file
        parameters: Optional conversion parameters
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If conversion parameters are invalid
        RuntimeError: If conversion fails
    """
    # Type validation
    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")
    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")
    if parameters is not None and not isinstance(parameters, dict):
        raise TypeError("parameters must be a dictionary or None")
        
    if not _NATIVE_AVAILABLE:
        raise ImportError("Native GPR extension not available")
    # Implementation will be in C++ binding
    raise NotImplementedError("Not yet implemented")

def convert_dng_to_gpr(
    input_path: str, 
    output_path: str, 
    parameters: Optional[Dict[str, Any]] = None
) -> None:
    """
    Convert DNG file to GPR format.
    
    Args:
        input_path: Path to input DNG file
        output_path: Path for output GPR file
        parameters: Optional conversion parameters
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If conversion parameters are invalid
        RuntimeError: If conversion fails
    """
    # Type validation
    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")
    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")
    if parameters is not None and not isinstance(parameters, dict):
        raise TypeError("parameters must be a dictionary or None")
        
    if not _NATIVE_AVAILABLE:
        raise ImportError("Native GPR extension not available")
    # Implementation will be in C++ binding
    raise NotImplementedError("Not yet implemented")

def convert_gpr_to_raw(
    input_path: str, 
    output_path: str
) -> None:
    """
    Convert GPR file to RAW format.
    
    Args:
        input_path: Path to input GPR file
        output_path: Path for output RAW file
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If conversion fails
    """
    # Type validation
    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")
    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string")
        
    if not _NATIVE_AVAILABLE:
        raise ImportError("Native GPR extension not available")
    # Implementation will be in C++ binding
    raise NotImplementedError("Not yet implemented")

def get_image_info(file_path: str) -> Dict[str, Any]:
    """
    Get image information from GPR or DNG file.
    
    Args:
        file_path: Path to image file
        
    Returns:
        Dictionary containing image metadata including:
        - width: Image width in pixels
        - height: Image height in pixels
        - format: File format (GPR, DNG, etc.)
        - metadata: Additional metadata dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported
    """
    # Type validation
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
        
    if not _NATIVE_AVAILABLE:
        raise ImportError("Native GPR extension not available")
    # Implementation will be in C++ binding
    raise NotImplementedError("Not yet implemented")

# Check if native extension is available and issue warning if not
if not _NATIVE_AVAILABLE:
    warnings.warn(
        "python-gpr native extension is not available. "
        "Only stub functions are accessible. "
        "Please ensure the package was installed correctly.",
        ImportWarning,
        stacklevel=2
    )

__all__ = [
    "__version__",
    "__author__", 
    "__license__",
    "convert_gpr_to_dng",
    "convert_dng_to_gpr", 
    "convert_gpr_to_raw",
    "get_image_info",
]