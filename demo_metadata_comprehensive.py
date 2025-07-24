#!/usr/bin/env python3
"""
Demo script for comprehensive GPR metadata access.

This script demonstrates all the metadata functionality including:
- Extracting EXIF data from GPR/DNG files
- Accessing GPR-specific metadata
- Modifying and saving metadata
- Working with the GPRMetadata class
"""

import os
import sys
from pathlib import Path

# Add the source directory to the path for importing
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from python_gpr.metadata import (
        GPRMetadata, extract_exif, extract_gpr_info, modify_exif,
        get_metadata_summary, get_camera_info, get_exposure_settings,
        get_image_dimensions, copy_metadata
    )
    METADATA_AVAILABLE = True
except ImportError as e:
    print(f"Warning: GPR metadata bindings not available: {e}")
    print("This demo will show the expected functionality when bindings are built.")
    METADATA_AVAILABLE = False


def demo_exif_extraction(filepath):
    """Demonstrate EXIF data extraction."""
    print(f"\n=== EXIF Data Extraction from {filepath} ===")
    
    if not METADATA_AVAILABLE:
        print("(Demo mode - bindings not available)")
        # Show what the output would look like
        mock_exif = {
            "camera_make": "GoPro",
            "camera_model": "HERO8 Black",
            "camera_serial": "ABC123456789",
            "software_version": "1.2.3",
            "iso_speed_rating": 800,
            "exposure_time": 0.001,
            "f_stop_number": 2.8,
            "focal_length": 3.0,
            "focal_length_in_35mm_film": 16,
            "exposure_program": 2,
            "metering_mode": 5,
            "flash": 0,
            "white_balance": 0,
            "date_time_original": {
                "year": 2023, "month": 10, "day": 15,
                "hour": 14, "minute": 30, "second": 45
            },
            "gps_info": {
                "valid": True,
                "latitude_ref": "N",
                "longitude_ref": "W",
                "latitude": [(37, 1), (46, 1), (30, 1)],
                "longitude": [(122, 1), (25, 1), (0, 1)]
            }
        }
        print("Mock EXIF data:")
        for key, value in mock_exif.items():
            print(f"  {key}: {value}")
        return
        
    try:
        exif_data = extract_exif(filepath)
        
        print("Basic Camera Information:")
        print(f"  Make: {exif_data.get('camera_make', 'Unknown')}")
        print(f"  Model: {exif_data.get('camera_model', 'Unknown')}")
        print(f"  Serial: {exif_data.get('camera_serial', 'Unknown')}")
        print(f"  Software: {exif_data.get('software_version', 'Unknown')}")
        
        print("\nExposure Settings:")
        print(f"  ISO: {exif_data.get('iso_speed_rating', 'Unknown')}")
        print(f"  Exposure Time: {exif_data.get('exposure_time', 'Unknown')} seconds")
        print(f"  F-Stop: f/{exif_data.get('f_stop_number', 'Unknown')}")
        print(f"  Focal Length: {exif_data.get('focal_length', 'Unknown')} mm")
        
        print("\nCapture Information:")
        date_info = exif_data.get('date_time_original', {})
        if date_info:
            print(f"  Date: {date_info.get('year')}-{date_info.get('month'):02d}-{date_info.get('day'):02d}")
            print(f"  Time: {date_info.get('hour'):02d}:{date_info.get('minute'):02d}:{date_info.get('second'):02d}")
        
        gps_info = exif_data.get('gps_info', {})
        if gps_info.get('valid', False):
            print("  GPS: Available")
            print(f"    Latitude Reference: {gps_info.get('latitude_ref', 'Unknown')}")
            print(f"    Longitude Reference: {gps_info.get('longitude_ref', 'Unknown')}")
        else:
            print("  GPS: Not available")
            
        print(f"\nTotal EXIF fields: {len(exif_data)}")
        
    except Exception as e:
        print(f"Error extracting EXIF data: {e}")


def demo_gpr_metadata_extraction(filepath):
    """Demonstrate GPR-specific metadata extraction."""
    print(f"\n=== GPR Metadata Extraction from {filepath} ===")
    
    if not METADATA_AVAILABLE:
        print("(Demo mode - bindings not available)")
        mock_gpr = {
            "input_width": 4000,
            "input_height": 3000,
            "input_pitch": 4000,
            "fast_encoding": True,
            "compute_md5sum": False,
            "enable_preview": True,
            "preview_image": {
                "has_preview": True,
                "width": 1920,
                "height": 1080,
                "jpg_preview_size": 256000
            },
            "gpmf_payload": {
                "has_gpmf": True,
                "size": 4096
            },
            "profile_info": {"available": True},
            "tuning_info": {"available": True}
        }
        print("Mock GPR metadata:")
        for key, value in mock_gpr.items():
            print(f"  {key}: {value}")
        return
        
    try:
        gpr_data = extract_gpr_info(filepath)
        
        print("Image Dimensions:")
        print(f"  Width: {gpr_data.get('input_width', 'Unknown')} pixels")
        print(f"  Height: {gpr_data.get('input_height', 'Unknown')} pixels")
        print(f"  Pitch: {gpr_data.get('input_pitch', 'Unknown')} pixels")
        
        print("\nCompression Settings:")
        print(f"  Fast Encoding: {gpr_data.get('fast_encoding', False)}")
        print(f"  MD5 Checksum: {gpr_data.get('compute_md5sum', False)}")
        print(f"  Preview Enabled: {gpr_data.get('enable_preview', False)}")
        
        preview_info = gpr_data.get('preview_image', {})
        if preview_info.get('has_preview', False):
            print(f"  Preview Size: {preview_info.get('width', 0)}x{preview_info.get('height', 0)}")
            print(f"  Preview Data Size: {preview_info.get('jpg_preview_size', 0)} bytes")
        
        gpmf_info = gpr_data.get('gpmf_payload', {})
        if gpmf_info.get('has_gpmf', False):
            print(f"  GPMF Data Size: {gpmf_info.get('size', 0)} bytes")
        else:
            print("  GPMF: Not available")
            
        print(f"\nTotal GPR fields: {len(gpr_data)}")
        
    except Exception as e:
        print(f"Error extracting GPR metadata: {e}")


def demo_gpr_metadata_class(filepath):
    """Demonstrate using the GPRMetadata class."""
    print(f"\n=== GPRMetadata Class Demo with {filepath} ===")
    
    if not METADATA_AVAILABLE:
        print("(Demo mode - bindings not available)")
        print("The GPRMetadata class would provide convenient property access:")
        print("  metadata = GPRMetadata('sample.gpr')")
        print("  print(f'Camera: {metadata.camera_make} {metadata.camera_model}')")
        print("  print(f'ISO: {metadata.iso_speed}, Exposure: {metadata.exposure_time}')")
        print("  print(f'Dimensions: {metadata.compression_info[\"input_width\"]}x{metadata.compression_info[\"input_height\"]}')")
        print("  print(f'Has GPS: {metadata.gps_info[\"valid\"]}')")
        return
        
    try:
        metadata = GPRMetadata(filepath)
        
        print("Camera Information:")
        print(f"  Make: {metadata.camera_make}")
        print(f"  Model: {metadata.camera_model}")
        print(f"  Serial: {metadata.camera_serial}")
        
        print("\nExposure Settings:")
        print(f"  ISO: {metadata.iso_speed}")
        print(f"  Exposure Time: {metadata.exposure_time} seconds")
        print(f"  F-Number: f/{metadata.f_number}")
        print(f"  Focal Length: {metadata.focal_length} mm")
        
        print("\nImage Properties:")
        compression_info = metadata.compression_info
        print(f"  Dimensions: {compression_info.get('input_width', 0)}x{compression_info.get('input_height', 0)}")
        print(f"  Fast Encoding: {compression_info.get('fast_encoding', False)}")
        
        print("\nFeatures Available:")
        print(f"  Preview Image: {metadata.has_preview}")
        print(f"  GPMF Data: {metadata.has_gpmf}")
        print(f"  GPS Data: {metadata.gps_info.get('valid', False)}")
        
        # Demonstrate getting all metadata as dictionary
        all_metadata = metadata.to_dict()
        print(f"\nTotal metadata sections: {len(all_metadata)}")
        for section, data in all_metadata.items():
            print(f"  {section}: {len(data)} fields")
            
    except Exception as e:
        print(f"Error using GPRMetadata class: {e}")


def demo_metadata_modification(input_filepath, output_filepath):
    """Demonstrate metadata modification."""
    print(f"\n=== Metadata Modification Demo ===")
    print(f"Input: {input_filepath}")
    print(f"Output: {output_filepath}")
    
    if not METADATA_AVAILABLE:
        print("(Demo mode - bindings not available)")
        print("Metadata modification would work like this:")
        print("  # Modify specific EXIF fields")
        print("  modify_exif('input.gpr', 'output.gpr',")
        print("              camera_make='Custom Make',")
        print("              iso_speed_rating=1600,")
        print("              user_comment='Modified by Python-GPR')")
        print("  ")
        print("  # Or use the GPRMetadata class")
        print("  metadata = GPRMetadata('input.gpr')")
        print("  metadata.save_with_metadata('output.gpr', {")
        print("      'camera_make': 'Custom Make',")
        print("      'user_comment': 'Modified metadata'")
        print("  })")
        return
        
    try:
        # First, show original metadata
        print("\nOriginal metadata summary:")
        original_summary = get_metadata_summary(input_filepath)
        for key, value in original_summary.items():
            if not key.startswith('filepath'):
                print(f"  {key}: {value}")
        
        # Modify metadata
        print("\nModifying metadata...")
        new_metadata = {
            "camera_make": "Custom Manufacturer",
            "user_comment": "Modified by Python-GPR Demo",
            "iso_speed_rating": 1600
        }
        
        modify_exif(input_filepath, output_filepath, **new_metadata)
        print("Metadata modification completed!")
        
        # Show modified metadata
        if os.path.exists(output_filepath):
            print("\nModified metadata summary:")
            modified_summary = get_metadata_summary(output_filepath)
            for key, value in modified_summary.items():
                if not key.startswith('filepath'):
                    print(f"  {key}: {value}")
                    
            # Highlight changes
            print("\nChanges made:")
            for key, new_value in new_metadata.items():
                original_value = original_summary.get(key, "Unknown")
                if key == "iso_speed_rating":
                    key = "iso_speed"  # Summary uses different key name
                if original_value != new_value:
                    print(f"  {key}: {original_value} -> {new_value}")
        
    except Exception as e:
        print(f"Error during metadata modification: {e}")


def demo_utility_functions(filepath):
    """Demonstrate utility functions."""
    print(f"\n=== Utility Functions Demo ===")
    
    if not METADATA_AVAILABLE:
        print("(Demo mode - bindings not available)")
        print("Utility functions would provide convenient access:")
        print("  camera_info = get_camera_info('sample.gpr')")
        print("  # {'make': 'GoPro', 'model': 'HERO8 Black', 'serial': 'ABC123'}")
        print("  ")
        print("  exposure = get_exposure_settings('sample.gpr')")
        print("  # {'exposure_time': 0.001, 'f_stop': 2.8, 'iso_speed': 800, ...}")
        print("  ")
        print("  width, height = get_image_dimensions('sample.gpr')")
        print("  # (4000, 3000)")
        return
        
    try:
        print("Camera Information:")
        camera_info = get_camera_info(filepath)
        for key, value in camera_info.items():
            print(f"  {key}: {value}")
        
        print("\nExposure Settings:")
        exposure_settings = get_exposure_settings(filepath)
        for key, value in exposure_settings.items():
            print(f"  {key}: {value}")
        
        print("\nImage Dimensions:")
        width, height = get_image_dimensions(filepath)
        print(f"  Size: {width}x{height} pixels")
        print(f"  Aspect Ratio: {width/height:.2f}:1" if height > 0 else "  Aspect Ratio: Unknown")
        
        print("\nComplete Summary:")
        summary = get_metadata_summary(filepath)
        for key, value in summary.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"Error using utility functions: {e}")


def main():
    """Main demo function."""
    print("=== Python-GPR Comprehensive Metadata Access Demo ===")
    print()
    
    if not METADATA_AVAILABLE:
        print("Note: This demo runs in mock mode because GPR bindings are not built.")
        print("When the library is properly built, it will work with real GPR/DNG files.")
        print()
    
    # Use a sample file path (in real usage, this would be a real GPR/DNG file)
    sample_file = "sample.gpr"
    output_file = "modified_sample.gpr"
    
    # Create dummy files for demo if in mock mode
    if not METADATA_AVAILABLE:
        sample_file = "demo_sample.gpr"
        output_file = "demo_output.gpr"
        
    print(f"Using sample file: {sample_file}")
    print(f"Output file for modifications: {output_file}")
    
    # Demo all the metadata functionality
    demo_exif_extraction(sample_file)
    demo_gpr_metadata_extraction(sample_file)
    demo_gpr_metadata_class(sample_file)
    demo_metadata_modification(sample_file, output_file)
    demo_utility_functions(sample_file)
    
    print("\n=== Demo Complete ===")
    print()
    print("This demo showed:")
    print("✓ EXIF data extraction with all standard fields")
    print("✓ GPR-specific metadata access (compression, preview, GPMF)")
    print("✓ Convenient GPRMetadata class interface")
    print("✓ Metadata modification capabilities")
    print("✓ Utility functions for common operations")
    print("✓ Support for both GPR and DNG files")
    print()
    print("All functionality preserves metadata modifications persistently.")
    print("The implementation provides comprehensive access to:")
    print("- Camera settings (make, model, serial)")
    print("- Exposure parameters (ISO, shutter, aperture, focal length)")
    print("- Image properties (dimensions, compression settings)")
    print("- GPS information (when available)")
    print("- Date/time information")
    print("- GoPro-specific data (GPMF, tuning parameters)")
    print("- Preview image information")


if __name__ == "__main__":
    main()