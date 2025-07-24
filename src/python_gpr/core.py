"""
Core functionality for Python-GPR.

This module will contain the main high-level API for working with GPR images,
including image loading, manipulation, and basic operations.
"""

from typing import Optional, Union, Tuple
import os

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    # Create a dummy np for type hints
    class DummyNumPy:
        class ndarray:
            pass
    np = DummyNumPy()


class GPRImage:
    """
    Represents a GPR image file.
    
    This class provides a high-level interface for working with GPR image files,
    including loading, format conversion, and metadata access.
    """
    
    def __init__(self, filepath: str):
        """
        Initialize a GPR image from a file path.
        
        Args:
            filepath: Path to the GPR image file
            
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a valid GPR format
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"GPR file not found: {filepath}")
        
        self.filepath = filepath
        self._width: Optional[int] = None
        self._height: Optional[int] = None
        
    @property
    def width(self) -> int:
        """Get the image width in pixels."""
        # Placeholder - will be implemented with actual GPR bindings
        if self._width is None:
            raise NotImplementedError("GPR bindings not yet implemented")
        return self._width
        
    @property
    def height(self) -> int:
        """Get the image height in pixels."""
        # Placeholder - will be implemented with actual GPR bindings
        if self._height is None:
            raise NotImplementedError("GPR bindings not yet implemented")
        return self._height
        
    @property
    def dimensions(self) -> Tuple[int, int]:
        """Get image dimensions as (width, height) tuple."""
        return (self.width, self.height)
        
    def to_dng(self, output_path: str) -> None:
        """
        Convert GPR image to DNG format.
        
        Args:
            output_path: Path where the DNG file will be saved
        """
        raise NotImplementedError("GPR bindings not yet implemented")
        
    def to_raw(self, output_path: str) -> None:
        """
        Convert GPR image to RAW format.
        
        Args:
            output_path: Path where the RAW file will be saved
        """
        raise NotImplementedError("GPR bindings not yet implemented")
    
    def to_numpy(self, dtype: str = "uint16") -> np.ndarray:
        """
        Extract raw image data as a NumPy array.
        
        Args:
            dtype: Data type for the returned array. Supported: 'uint16', 'float32'
            
        Returns:
            NumPy array containing the raw image data with shape (height, width)
            
        Raises:
            ImportError: If NumPy is not available
            NotImplementedError: If GPR bindings are not available
            ValueError: If conversion fails or unsupported dtype
        """
        if not HAS_NUMPY:
            raise ImportError("NumPy is required for this functionality. Please install numpy: pip install numpy")
        
        try:
            from ._core import get_raw_image_data
            return get_raw_image_data(self.filepath, dtype)
        except ImportError:
            raise NotImplementedError("GPR C++ bindings not available - please build the extension module")
        except Exception as e:
            raise ValueError(f"Failed to extract raw image data: {str(e)}") from e
    
    def get_image_info(self) -> dict:
        """
        Get detailed image information including dimensions and metadata.
        
        Returns:
            Dictionary containing image information (width, height, channels, format, data_size)
            
        Raises:
            NotImplementedError: If GPR bindings are not available
            ValueError: If information extraction fails
        """
        try:
            from ._core import get_image_info
            info = get_image_info(self.filepath)
            return {
                'width': info.width,
                'height': info.height,
                'channels': info.channels,
                'format': info.format,
                'data_size': info.data_size
            }
        except ImportError:
            raise NotImplementedError("GPR C++ bindings not available - please build the extension module")
        except Exception as e:
            raise ValueError(f"Failed to get image information: {str(e)}") from e


def get_gpr_info(filepath: str) -> dict:
    """
    Get basic information about a GPR file.
    
    Args:
        filepath: Path to the GPR file
        
    Returns:
        Dictionary containing basic file information
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file is not a valid GPR format
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"GPR file not found: {filepath}")
    
    # Placeholder - will be implemented with actual GPR bindings
    raise NotImplementedError("GPR bindings not yet implemented")


def load_gpr_as_numpy(filepath: str, dtype: str = "uint16") -> np.ndarray:
    """
    Load a GPR file directly as a NumPy array.
    
    Args:
        filepath: Path to the GPR file
        dtype: Data type for the returned array. Supported: 'uint16', 'float32'
        
    Returns:
        NumPy array containing the raw image data with shape (height, width)
        
    Raises:
        FileNotFoundError: If the file does not exist
        ImportError: If NumPy is not available
        ValueError: If conversion fails or unsupported dtype
        NotImplementedError: If GPR bindings are not available
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"GPR file not found: {filepath}")
    
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for this functionality. Please install numpy: pip install numpy")
    
    try:
        from ._core import get_raw_image_data
        return get_raw_image_data(filepath, dtype)
    except ImportError:
        raise NotImplementedError("GPR C++ bindings not available - please build the extension module")
    except Exception as e:
        raise ValueError(f"Failed to load GPR file as NumPy array: {str(e)}") from e


def get_gpr_image_info(filepath: str) -> dict:
    """
    Get detailed information about a GPR image file.
    
    Args:
        filepath: Path to the GPR file
        
    Returns:
        Dictionary containing image information (width, height, channels, format, data_size)
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If information extraction fails  
        NotImplementedError: If GPR bindings are not available
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"GPR file not found: {filepath}")
    
    try:
        from ._core import get_image_info
        info = get_image_info(filepath)
        return {
            'width': info.width,
            'height': info.height,
            'channels': info.channels,
            'format': info.format,
            'data_size': info.data_size
        }
    except ImportError:
        raise NotImplementedError("GPR C++ bindings not available - please build the extension module")
    except Exception as e:
        raise ValueError(f"Failed to get GPR image information: {str(e)}") from e


__all__ = [
    "GPRImage",
    "get_gpr_info",
    "load_gpr_as_numpy",
    "get_gpr_image_info",
]