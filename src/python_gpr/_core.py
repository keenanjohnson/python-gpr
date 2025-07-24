"""
Temporary stub implementation for _core module.

This provides basic stub functionality for the C++ bindings that haven't been compiled yet.
This allows the package to be imported and tested without build dependencies.
"""

from typing import Dict, Any, Optional, Tuple
import os
import warnings


# Conversion function stubs
def convert_gpr_to_dng(input_path: str, output_path: str, params: Optional[Dict[str, Any]] = None) -> bool:
    """Convert GPR to DNG format (stub implementation)."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Check if file is empty
    if os.path.getsize(input_path) == 0:
        raise ValueError("Input file is empty or corrupted")
    
    raise NotImplementedError("GPR C++ bindings not available - please build the extension module")


def convert_dng_to_gpr(input_path: str, output_path: str, params: Optional[Dict[str, Any]] = None) -> bool:
    """Convert DNG to GPR format (stub implementation)."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Check if file is empty
    if os.path.getsize(input_path) == 0:
        raise ValueError("Input file is empty or corrupted")
    
    raise NotImplementedError("GPR C++ bindings not available - please build the extension module")


def convert_gpr_to_raw(input_path: str, output_path: str, params: Optional[Dict[str, Any]] = None) -> bool:
    """Convert GPR to RAW format (stub implementation)."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Check if file is empty
    if os.path.getsize(input_path) == 0:
        raise ValueError("Input file is empty or corrupted")
    
    raise NotImplementedError("GPR C++ bindings not available - please build the extension module")


def convert_dng_to_dng(input_path: str, output_path: str, params: Optional[Dict[str, Any]] = None) -> bool:
    """Convert DNG to DNG format with modifications (stub implementation)."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Check if file is empty
    if os.path.getsize(input_path) == 0:
        raise ValueError("Input file is empty or corrupted")
    
    raise NotImplementedError("GPR C++ bindings not available - please build the extension module")


def get_raw_image_data(filepath: str, dtype: str = "uint16") -> Tuple[Any, int, int]:
    """Get raw image data from file (stub implementation)."""
    # Check for invalid dtype first
    valid_dtypes = ["uint8", "uint16", "float32", "float64"]
    if dtype not in valid_dtypes:
        raise ValueError(f"Unsupported dtype '{dtype}'. Valid types are: {valid_dtypes}")
    
    raise NotImplementedError("Raw image data access not yet implemented")


def get_image_info(filepath: str):
    """Get image information from file (stub implementation)."""
    raise NotImplementedError("GPR C++ bindings not available - please build the extension module")


# Exception classes that should be defined in _core
class GPRConversionError(Exception):
    """Exception raised during GPR conversion operations."""
    pass


class GPRError(Exception):
    """Base exception for GPR operations."""
    pass


def extract_exif_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract EXIF metadata from a GPR/DNG file.
    
    Args:
        filepath: Path to the GPR/DNG file
        
    Returns:
        Dictionary containing EXIF metadata
        
    Note:
        This is a stub implementation that returns mock data.
        The real implementation will be in the compiled C++ module.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    warnings.warn(
        "Using stub implementation of _core.extract_exif_metadata. "
        "Install C++ bindings for full functionality.",
        UserWarning
    )
    
    # Return mock EXIF data that matches the expected structure
    return {
        "camera_make": "Mock Camera",
        "camera_model": "Mock Model",
        "camera_serial_number": "12345",
        "lens_model": "Mock Lens",
        "software": "Mock Software v1.0",
        "date_time_original": "2024:01:01 12:00:00",
        "date_time_digitized": "2024:01:01 12:00:00",
        "subsec_time_original": "00",
        "subsec_time_digitized": "00",
        "f_stop_number": 2.8,
        "exposure_time": 0.001,
        "iso_speed_rating": 100,
        "focal_length": 50.0,
        "focal_length_35mm": 75.0,
        "flash": 0,
        "white_balance": 0,
        "exposure_mode": 0,
        "exposure_program": 2,
        "metering_mode": 5,
        "scene_capture_type": 0,
        "contrast": 0,
        "saturation": 0,
        "sharpness": 0,
        "brightness_value": 0.0,
        "exposure_bias_value": 0.0,
        "max_aperture_value": 2.8,
        "subject_distance": 0.0,
        "light_source": 0,
        "color_space": 1,
        "sensing_method": 2,
        "file_source": 3,
        "scene_type": 1,
        "custom_rendered": 0,
        "digital_zoom_ratio": 1.0,
        "gps_latitude": None,
        "gps_longitude": None,
        "gps_altitude": None,
        "gps_timestamp": None,
        "user_comment": "",
        "image_unique_id": "",
        "camera_owner_name": "",
        "body_serial_number": "",
        "lens_serial_number": "",
        "lens_make": "",
        "lens_specification": "",
    }


def extract_gpr_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract GPR-specific metadata from a GPR file.
    
    Args:
        filepath: Path to the GPR file
        
    Returns:
        Dictionary containing GPR-specific metadata
        
    Note:
        This is a stub implementation that returns mock data.
        The real implementation will be in the compiled C++ module.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    warnings.warn(
        "Using stub implementation of _core.extract_gpr_metadata. "
        "Install C++ bindings for full functionality.",
        UserWarning
    )
    
    # Return mock GPR data that matches the expected structure
    return {
        "input_width": 4096,
        "input_height": 3072,
        "input_pitch": 8192,
        "input_format": "RGGB",
        "input_resolution": {"horizontal": 300, "vertical": 300},
        "channels": 4,
        "bits_per_channel": 12,
        "bytes_per_channel": 2,
        "cfaPattern": "RGGB",
        "compression_method": "VC-5",
        "compression_quality": 12,
        "compression_curve": {"enabled": True, "strength": 0.5},
        "rgb_resolution": {"horizontal": 300, "vertical": 300},
        "thumbnail_resolution": {"horizontal": 300, "vertical": 300},
        "preview_image": {
            "has_preview": True,
            "width": 1024,
            "height": 768,
            "format": "JPEG",
            "size_bytes": 102400
        },
        "gpmf_payload": {
            "has_gpmf": False,
            "size_bytes": 0,
            "version": ""
        },
        "fast_decode_parameters": {
            "enabled": True,
            "fast_decode_resolution": {"horizontal": 300, "vertical": 300}
        }
    }


def modify_metadata(input_path: str, output_path: str, metadata_updates: Dict[str, Any]) -> None:
    """
    Modify metadata in a GPR/DNG file and save to a new file.
    
    Args:
        input_path: Path to the input file
        output_path: Path where to save the modified file
        metadata_updates: Dictionary of metadata fields to update
        
    Note:
        This is a stub implementation that just copies the file.
        The real implementation will be in the compiled C++ module.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    warnings.warn(
        "Using stub implementation of _core.modify_metadata. "
        "Install C++ bindings for full functionality. "
        f"File will be copied from {input_path} to {output_path}",
        UserWarning
    )
    
    # For now, just copy the file since we can't actually modify metadata
    import shutil
    shutil.copy2(input_path, output_path)