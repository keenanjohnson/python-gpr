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
    
    Supports context manager protocol for automatic resource cleanup:
    
    with GPRImage("image.gpr") as img:
        data = img.to_numpy()
        print(f"Dimensions: {img.width}x{img.height}")
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
        self._info: Optional[dict] = None
        self._closed: bool = False
        
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager with automatic resource cleanup."""
        self.close()
        return False
    
    def close(self) -> None:
        """Close the image and free any associated resources."""
        self._closed = True
        # Any cleanup logic will go here when C++ bindings are integrated
    
    def _ensure_not_closed(self) -> None:
        """Ensure the image is not closed."""
        if self._closed:
            raise ValueError("GPRImage is closed")
    
    def _load_info_if_needed(self) -> None:
        """Load image information if not already loaded."""
        self._ensure_not_closed()
        if self._info is None:
            try:
                self._info = self.get_image_info()
                self._width = self._info['width']
                self._height = self._info['height']
            except NotImplementedError:
                # Fallback when bindings are not available
                pass
    
    @property
    def width(self) -> int:
        """Get the image width in pixels."""
        self._load_info_if_needed()
        if self._width is None:
            raise NotImplementedError("GPR bindings not yet implemented")
        return self._width
        
    @property
    def height(self) -> int:
        """Get the image height in pixels."""
        self._load_info_if_needed()
        if self._height is None:
            raise NotImplementedError("GPR bindings not yet implemented")
        return self._height
        
    @property
    def dimensions(self) -> Tuple[int, int]:
        """Get image dimensions as (width, height) tuple."""
        return (self.width, self.height)
    
    @property
    def is_closed(self) -> bool:
        """Check if the image is closed."""
        return self._closed
        
    def convert_to_dng(self, output_path: str) -> None:
        """
        Convert GPR image to DNG format.
        
        Args:
            output_path: Path where the DNG file will be saved
            
        Raises:
            ValueError: If the image is closed or conversion fails
        """
        self._ensure_not_closed()
        try:
            from .conversion import convert_gpr_to_dng
            convert_gpr_to_dng(self.filepath, output_path)
        except ImportError:
            raise NotImplementedError("GPR bindings not yet implemented")
    
    def convert_to_raw(self, output_path: str) -> None:
        """
        Convert GPR image to RAW format.
        
        Args:
            output_path: Path where the RAW file will be saved
            
        Raises:
            ValueError: If the image is closed or conversion fails
        """
        self._ensure_not_closed()
        try:
            from .conversion import convert_gpr_to_raw
            convert_gpr_to_raw(self.filepath, output_path)
        except ImportError:
            raise NotImplementedError("GPR bindings not yet implemented")
    
    def to_dng(self, output_path: str) -> None:
        """
        Convert GPR image to DNG format (alias for convert_to_dng).
        
        Args:
            output_path: Path where the DNG file will be saved
        """
        self.convert_to_dng(output_path)
        
    def to_raw(self, output_path: str) -> None:
        """
        Convert GPR image to RAW format (alias for convert_to_raw).
        
        Args:
            output_path: Path where the RAW file will be saved
        """
        self.convert_to_raw(output_path)
    
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
            ValueError: If conversion fails, unsupported dtype, or image is closed
        """
        self._ensure_not_closed()
        
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
            ValueError: If information extraction fails or image is closed
        """
        self._ensure_not_closed()
        
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
        except NotImplementedError:
            # Re-raise NotImplementedError as-is
            raise
        except Exception as e:
            raise ValueError(f"Failed to get image information: {str(e)}") from e
    
    def get_metadata(self) -> dict:
        """
        Get image metadata including EXIF and GPR-specific information.
        
        Returns:
            Dictionary containing metadata
            
        Raises:
            NotImplementedError: If GPR bindings are not available
            ValueError: If metadata extraction fails or image is closed
        """
        self._ensure_not_closed()
        
        try:
            from .metadata import GPRMetadata
            metadata_reader = GPRMetadata(self.filepath)
            return metadata_reader.to_dict()
        except Exception as e:
            if "not yet implemented" in str(e).lower():
                raise NotImplementedError("GPR metadata bindings not yet implemented")
            raise ValueError(f"Failed to get metadata: {str(e)}") from e
    
    def __repr__(self) -> str:
        """String representation of the GPRImage."""
        if self._closed:
            return f"GPRImage('{self.filepath}', closed=True)"
        try:
            return f"GPRImage('{self.filepath}', {self.width}x{self.height})"
        except (NotImplementedError, ValueError):
            return f"GPRImage('{self.filepath}')"


def open_gpr(filepath: str) -> GPRImage:
    """
    Open a GPR image file.
    
    Convenience function that creates a GPRImage instance.
    
    Args:
        filepath: Path to the GPR file
        
    Returns:
        GPRImage instance
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file is not a valid GPR format
        
    Example:
        >>> img = open_gpr("sample.gpr")
        >>> print(f"Dimensions: {img.width}x{img.height}")
        >>> img.close()
        
        # Or use as context manager
        >>> with open_gpr("sample.gpr") as img:
        ...     data = img.to_numpy()
    """
    return GPRImage(filepath)


def convert_image(input_path: str, output_path: str, target_format: Optional[str] = None) -> None:
    """
    Convert between supported image formats.
    
    Auto-detects input format and converts to target format based on
    output file extension or explicit target_format parameter.
    
    Args:
        input_path: Path to input file
        output_path: Path for output file
        target_format: Target format ('gpr', 'dng', 'raw'). If None, inferred from output extension.
        
    Raises:
        FileNotFoundError: If input file does not exist
        ValueError: If conversion fails or unsupported format
        NotImplementedError: If conversion bindings are not available
        
    Example:
        >>> convert_image("image.gpr", "image.dng")
        >>> convert_image("image.dng", "image.gpr", target_format="gpr")
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Detect input format
    try:
        from .conversion import detect_format
        input_format = detect_format(input_path)
    except Exception:
        # Fallback to extension-based detection
        input_ext = os.path.splitext(input_path)[1].lower()
        format_map = {'.gpr': 'gpr', '.dng': 'dng', '.raw': 'raw'}
        input_format = format_map.get(input_ext, 'unknown')
    
    # Determine target format
    if target_format is None:
        output_ext = os.path.splitext(output_path)[1].lower()
        format_map = {'.gpr': 'gpr', '.dng': 'dng', '.raw': 'raw'}
        target_format = format_map.get(output_ext)
        if target_format is None:
            raise ValueError(f"Cannot determine target format from extension: {output_ext}")
    
    # Import conversion functions
    try:
        from .conversion import (
            convert_gpr_to_dng, convert_gpr_to_raw,
            convert_dng_to_gpr, convert_dng_to_dng
        )
    except ImportError:
        raise NotImplementedError("GPR conversion bindings not available")
    
    # Perform conversion
    if input_format == 'gpr' and target_format == 'dng':
        convert_gpr_to_dng(input_path, output_path)
    elif input_format == 'gpr' and target_format == 'raw':
        convert_gpr_to_raw(input_path, output_path)
    elif input_format == 'dng' and target_format == 'gpr':
        convert_dng_to_gpr(input_path, output_path)
    elif input_format == 'dng' and target_format == 'dng':
        convert_dng_to_dng(input_path, output_path)
    else:
        raise ValueError(f"Unsupported conversion: {input_format} to {target_format}")


def get_info(filepath: str) -> dict:
    """
    Get comprehensive information about an image file.
    
    Convenience function that returns both basic file info and image metadata.
    
    Args:
        filepath: Path to the image file
        
    Returns:
        Dictionary containing file and image information
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If information extraction fails
        NotImplementedError: If bindings are not available
        
    Example:
        >>> info = get_info("sample.gpr")
        >>> print(f"Dimensions: {info['width']}x{info['height']}")
        >>> print(f"Format: {info['format']}")
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        with GPRImage(filepath) as img:
            return img.get_image_info()
    except NotImplementedError:
        # Re-raise NotImplementedError as-is
        raise
    except Exception as e:
        raise ValueError(f"Failed to get file information: {str(e)}") from e


def get_gpr_info(filepath: str) -> dict:
    """
    Get basic information about a GPR file (legacy function).
    
    Args:
        filepath: Path to the GPR file
        
    Returns:
        Dictionary containing basic file information
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file is not a valid GPR format
        
    Note:
        This function is deprecated. Use get_info() or GPRImage.get_image_info() instead.
    """
    return get_info(filepath)


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
    "open_gpr",
    "convert_image", 
    "get_info",
    "get_gpr_info",
    "load_gpr_as_numpy",
    "get_gpr_image_info",
]