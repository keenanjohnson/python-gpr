"""
Metadata handling utilities for Python-GPR.

This module provides functionality for extracting and manipulating metadata
from GPR and DNG files, including EXIF data and GPR-specific information.
"""

from typing import Dict, Any, Optional, Union, Tuple
import os
from . import _core


class GPRMetadata:
    """
    Container for GPR image metadata.
    
    This class provides access to metadata stored in GPR files, including
    camera settings, compression parameters, and image properties.
    """
    
    def __init__(self, filepath: str):
        """
        Initialize metadata reader for a GPR file.
        
        Args:
            filepath: Path to the GPR file
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file is not a valid GPR format
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"GPR file not found: {filepath}")
            
        self.filepath = filepath
        self._exif_metadata: Optional[Dict[str, Any]] = None
        self._gpr_metadata: Optional[Dict[str, Any]] = None
        
    def load(self) -> None:
        """Load metadata from the GPR file."""
        try:
            self._exif_metadata = _core.extract_exif_metadata(self.filepath)
            self._gpr_metadata = _core.extract_gpr_metadata(self.filepath)
        except Exception as e:
            raise ValueError(f"Failed to load metadata from {self.filepath}: {e}")
        
    @property
    def camera_model(self) -> str:
        """Get the camera model that captured the image."""
        if self._exif_metadata is None:
            self.load()
        return self._exif_metadata.get("camera_model", "Unknown")
        
    @property
    def camera_make(self) -> str:
        """Get the camera make that captured the image."""
        if self._exif_metadata is None:
            self.load()
        return self._exif_metadata.get("camera_make", "Unknown")
        
    @property
    def camera_serial(self) -> str:
        """Get the camera serial number."""
        if self._exif_metadata is None:
            self.load()
        return self._exif_metadata.get("camera_serial", "Unknown")
        
    @property
    def iso_speed(self) -> int:
        """Get the ISO speed setting."""
        if self._exif_metadata is None:
            self.load()
        return self._exif_metadata.get("iso_speed_rating", 0)
        
    @property
    def exposure_time(self) -> float:
        """Get the exposure time in seconds."""
        if self._exif_metadata is None:
            self.load()
        return self._exif_metadata.get("exposure_time", 0.0)
        
    @property
    def f_number(self) -> float:
        """Get the f-number (aperture)."""
        if self._exif_metadata is None:
            self.load()
        return self._exif_metadata.get("f_stop_number", 0.0)
        
    @property
    def focal_length(self) -> float:
        """Get the focal length in mm."""
        if self._exif_metadata is None:
            self.load()
        return self._exif_metadata.get("focal_length", 0.0)
        
    @property
    def compression_info(self) -> Dict[str, Any]:
        """Get GPR compression information."""
        if self._gpr_metadata is None:
            self.load()
        
        compression_info = {}
        if self._gpr_metadata:
            compression_info["fast_encoding"] = self._gpr_metadata.get("fast_encoding", False)
            compression_info["compute_md5sum"] = self._gpr_metadata.get("compute_md5sum", False)
            compression_info["input_width"] = self._gpr_metadata.get("input_width", 0)
            compression_info["input_height"] = self._gpr_metadata.get("input_height", 0)
            compression_info["input_pitch"] = self._gpr_metadata.get("input_pitch", 0)
            
        return compression_info
        
    @property
    def exif_data(self) -> Dict[str, Any]:
        """Get all EXIF data as a dictionary."""
        if self._exif_metadata is None:
            self.load()
        return self._exif_metadata.copy() if self._exif_metadata else {}
        
    @property
    def gpr_data(self) -> Dict[str, Any]:
        """Get all GPR-specific data as a dictionary."""
        if self._gpr_metadata is None:
            self.load()
        return self._gpr_metadata.copy() if self._gpr_metadata else {}
        
    @property
    def gps_info(self) -> Dict[str, Any]:
        """Get GPS information if available."""
        if self._exif_metadata is None:
            self.load()
        return self._exif_metadata.get("gps_info", {"valid": False})
        
    @property
    def date_time_original(self) -> Dict[str, int]:
        """Get the original date/time when the image was captured."""
        if self._exif_metadata is None:
            self.load()
        return self._exif_metadata.get("date_time_original", {})
        
    @property
    def has_preview(self) -> bool:
        """Check if the file contains a preview image."""
        if self._gpr_metadata is None:
            self.load()
        preview_info = self._gpr_metadata.get("preview_image", {})
        return preview_info.get("has_preview", False)
        
    @property
    def has_gpmf(self) -> bool:
        """Check if the file contains GPMF (GoPro Metadata Format) data."""
        if self._gpr_metadata is None:
            self.load()
        gpmf_info = self._gpr_metadata.get("gpmf_payload", {})
        return gpmf_info.get("has_gpmf", False)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Get all metadata as a dictionary.
        
        Returns:
            Dictionary containing all available metadata
        """
        if self._exif_metadata is None or self._gpr_metadata is None:
            self.load()
            
        result = {}
        if self._exif_metadata:
            result["exif"] = self._exif_metadata.copy()
        if self._gpr_metadata:
            result["gpr"] = self._gpr_metadata.copy()
            
        return result
        
    def update_exif(self, **kwargs) -> 'GPRMetadata':
        """
        Update EXIF metadata values.
        
        Args:
            **kwargs: EXIF fields to update (e.g., camera_make="Canon", iso_speed_rating=800)
            
        Returns:
            Self for method chaining
        """
        if self._exif_metadata is None:
            self.load()
            
        # Update the cached metadata
        for key, value in kwargs.items():
            if key in self._exif_metadata:
                self._exif_metadata[key] = value
                
        return self
        
    def save_with_metadata(self, output_path: str, exif_updates: Optional[Dict[str, Any]] = None) -> None:
        """
        Save the file with modified metadata to a new location.
        
        Args:
            output_path: Path where to save the file with updated metadata
            exif_updates: Optional dictionary of EXIF fields to update
            
        Raises:
            ValueError: If metadata modification fails
        """
        updates = exif_updates or {}
        
        # If we have locally cached updates, apply them
        if self._exif_metadata and hasattr(self, '_local_updates'):
            updates.update(getattr(self, '_local_updates'))
            
        try:
            _core.modify_metadata(self.filepath, output_path, updates)
        except Exception as e:
            raise ValueError(f"Failed to save file with updated metadata: {e}")


def extract_exif(filepath: str) -> Dict[str, Any]:
    """
    Extract EXIF data from a GPR or DNG file.
    
    Args:
        filepath: Path to the image file
        
    Returns:
        Dictionary containing EXIF data
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If EXIF data cannot be extracted
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        return _core.extract_exif_metadata(filepath)
    except Exception as e:
        raise ValueError(f"Failed to extract EXIF data from {filepath}: {e}")


def extract_gpr_info(filepath: str) -> Dict[str, Any]:
    """
    Extract GPR-specific information from a GPR file.
    
    Args:
        filepath: Path to the GPR file
        
    Returns:
        Dictionary containing GPR-specific information like compression
        parameters, wavelet settings, etc.
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If GPR information cannot be extracted
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"GPR file not found: {filepath}")
    
    try:
        return _core.extract_gpr_metadata(filepath)
    except Exception as e:
        raise ValueError(f"Failed to extract GPR information from {filepath}: {e}")


def modify_exif(input_path: str, output_path: str, **exif_updates) -> None:
    """
    Modify EXIF data in a file and save to a new location.
    
    Args:
        input_path: Path to the input file
        output_path: Path where to save the modified file
        **exif_updates: EXIF fields to update (e.g., camera_make="Canon")
        
    Raises:
        FileNotFoundError: If input file does not exist
        ValueError: If metadata modification fails
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    try:
        _core.modify_metadata(input_path, output_path, exif_updates)
    except Exception as e:
        raise ValueError(f"Failed to modify EXIF data: {e}")


def copy_metadata(source_path: str, target_path: str) -> None:
    """
    Copy metadata from one file to another.
    
    Args:
        source_path: Path to source file with metadata
        target_path: Path to target file to copy metadata to
        
    Raises:
        FileNotFoundError: If source file does not exist
        ValueError: If metadata cannot be copied
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Target file not found: {target_path}")
    
    try:
        # Extract metadata from source
        exif_data = extract_exif(source_path)
        gpr_data = extract_gpr_info(source_path)
        
        # Create a temporary output file with the target file content but source metadata
        import tempfile
        import shutil
        
        with tempfile.NamedTemporaryFile(suffix=".dng", delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            # Copy target file to temp location
            shutil.copy2(target_path, temp_path)
            
            # Apply source metadata to temp file, overwriting target
            _core.modify_metadata(temp_path, target_path, exif_data)
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        raise ValueError(f"Failed to copy metadata from {source_path} to {target_path}: {e}")


def get_metadata_summary(filepath: str) -> Dict[str, Any]:
    """
    Get a summary of key metadata fields from a file.
    
    Args:
        filepath: Path to the image file
        
    Returns:
        Dictionary with summary of key metadata fields
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    try:
        exif_data = extract_exif(filepath)
        gpr_data = extract_gpr_info(filepath)
        
        summary = {
            "filepath": filepath,
            "camera_make": exif_data.get("camera_make", "Unknown"),
            "camera_model": exif_data.get("camera_model", "Unknown"),
            "iso_speed": exif_data.get("iso_speed_rating", 0),
            "exposure_time": exif_data.get("exposure_time", 0.0),
            "f_stop": exif_data.get("f_stop_number", 0.0),
            "focal_length": exif_data.get("focal_length", 0.0),
            "image_width": gpr_data.get("input_width", 0),
            "image_height": gpr_data.get("input_height", 0),
            "has_gps": exif_data.get("gps_info", {}).get("valid", False),
            "has_preview": gpr_data.get("preview_image", {}).get("has_preview", False),
            "has_gpmf": gpr_data.get("gpmf_payload", {}).get("has_gpmf", False),
        }
        
        date_info = exif_data.get("date_time_original", {})
        if date_info:
            summary["capture_date"] = f"{date_info.get('year', 0)}-{date_info.get('month', 0):02d}-{date_info.get('day', 0):02d}"
            summary["capture_time"] = f"{date_info.get('hour', 0):02d}:{date_info.get('minute', 0):02d}:{date_info.get('second', 0):02d}"
        
        return summary
        
    except Exception as e:
        raise ValueError(f"Failed to get metadata summary for {filepath}: {e}")


# Convenience functions for common EXIF fields
def get_camera_info(filepath: str) -> Dict[str, str]:
    """Get camera make, model, and serial number."""
    exif_data = extract_exif(filepath)
    return {
        "make": exif_data.get("camera_make", "Unknown"),
        "model": exif_data.get("camera_model", "Unknown"),
        "serial": exif_data.get("camera_serial", "Unknown"),
    }


def get_exposure_settings(filepath: str) -> Dict[str, Union[float, int]]:
    """Get exposure-related settings."""
    exif_data = extract_exif(filepath)
    return {
        "exposure_time": exif_data.get("exposure_time", 0.0),
        "f_stop": exif_data.get("f_stop_number", 0.0),
        "iso_speed": exif_data.get("iso_speed_rating", 0),
        "focal_length": exif_data.get("focal_length", 0.0),
        "exposure_bias": exif_data.get("exposure_bias", 0.0),
    }


def get_image_dimensions(filepath: str) -> Tuple[int, int]:
    """Get image width and height."""
    gpr_data = extract_gpr_info(filepath)
    return (gpr_data.get("input_width", 0), gpr_data.get("input_height", 0))


__all__ = [
    "GPRMetadata",
    "extract_exif",
    "extract_gpr_info", 
    "modify_exif",
    "copy_metadata",
    "get_metadata_summary",
    "get_camera_info",
    "get_exposure_settings", 
    "get_image_dimensions",
]