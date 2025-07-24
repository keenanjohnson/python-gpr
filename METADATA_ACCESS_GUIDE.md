# Comprehensive Metadata Access Documentation

This document describes the comprehensive metadata access capabilities implemented in Python-GPR, providing complete access to EXIF data, DNG metadata, and GPR-specific information.

## Overview

The metadata functionality provides:
- **Complete EXIF data access** - All standard EXIF fields are accessible via Python
- **DNG metadata support** - Read and write DNG-specific metadata fields
- **GPR-specific metadata** - Access to compression parameters, tuning info, and GoPro-specific data
- **Metadata modification** - Modify and persist metadata changes
- **Convenient interfaces** - Both low-level and high-level APIs available

## Core Features

### 1. EXIF Data Extraction

Extract comprehensive EXIF metadata from GPR and DNG files:

```python
from python_gpr.metadata import extract_exif

# Extract all EXIF data
exif_data = extract_exif("sample.gpr")

# Access camera information
print(f"Camera: {exif_data['camera_make']} {exif_data['camera_model']}")
print(f"Serial: {exif_data['camera_serial']}")

# Access exposure settings
print(f"ISO: {exif_data['iso_speed_rating']}")
print(f"Exposure: {exif_data['exposure_time']} seconds")
print(f"Aperture: f/{exif_data['f_stop_number']}")
print(f"Focal Length: {exif_data['focal_length']} mm")

# Access date/time information
date_info = exif_data['date_time_original']
print(f"Captured: {date_info['year']}-{date_info['month']:02d}-{date_info['day']:02d}")

# Access GPS information (if available)
gps_info = exif_data['gps_info']
if gps_info['valid']:
    print("GPS data available")
    print(f"Latitude: {gps_info['latitude_ref']} {gps_info['latitude']}")
    print(f"Longitude: {gps_info['longitude_ref']} {gps_info['longitude']}")
```

### 2. GPR-Specific Metadata

Access GPR compression parameters and GoPro-specific information:

```python
from python_gpr.metadata import extract_gpr_info

# Extract GPR-specific metadata
gpr_data = extract_gpr_info("sample.gpr")

# Image dimensions and compression
print(f"Dimensions: {gpr_data['input_width']}x{gpr_data['input_height']}")
print(f"Fast Encoding: {gpr_data['fast_encoding']}")
print(f"MD5 Checksum: {gpr_data['compute_md5sum']}")

# Preview image information
preview = gpr_data['preview_image']
if preview['has_preview']:
    print(f"Preview: {preview['width']}x{preview['height']}")
    print(f"Preview Size: {preview['jpg_preview_size']} bytes")

# GPMF (GoPro Metadata Format) information
gpmf = gpr_data['gpmf_payload']
if gpmf['has_gpmf']:
    print(f"GPMF Data: {gpmf['size']} bytes")
```

### 3. High-Level GPRMetadata Class

Convenient object-oriented interface for metadata access:

```python
from python_gpr.metadata import GPRMetadata

# Create metadata object
metadata = GPRMetadata("sample.gpr")

# Access properties directly
print(f"Camera: {metadata.camera_make} {metadata.camera_model}")
print(f"ISO: {metadata.iso_speed}")
print(f"Exposure: {metadata.exposure_time}")
print(f"F-Number: f/{metadata.f_number}")
print(f"Focal Length: {metadata.focal_length} mm")

# Check for features
print(f"Has GPS: {metadata.gps_info['valid']}")
print(f"Has Preview: {metadata.has_preview}")
print(f"Has GPMF: {metadata.has_gpmf}")

# Get compression information
compression = metadata.compression_info
print(f"Dimensions: {compression['input_width']}x{compression['input_height']}")
print(f"Fast Encoding: {compression['fast_encoding']}")

# Get all metadata as dictionaries
all_metadata = metadata.to_dict()
print(f"EXIF fields: {len(all_metadata['exif'])}")
print(f"GPR fields: {len(all_metadata['gpr'])}")
```

### 4. Metadata Modification

Modify EXIF data and save to new files:

```python
from python_gpr.metadata import modify_exif, GPRMetadata

# Method 1: Direct modification
modify_exif(
    "input.gpr", 
    "output.gpr",
    camera_make="Custom Manufacturer",
    camera_model="Modified Model",
    iso_speed_rating=1600,
    user_comment="Modified by Python-GPR"
)

# Method 2: Using GPRMetadata class
metadata = GPRMetadata("input.gpr")
metadata.save_with_metadata("output.gpr", {
    "camera_make": "Custom Manufacturer",
    "user_comment": "Modified metadata",
    "exposure_time_rational": (1, 2000)  # 1/2000 second
})

# Method 3: Modify and save with updates
metadata = GPRMetadata("input.gpr")
metadata.update_exif(
    camera_make="New Make",
    iso_speed_rating=800
)
metadata.save_with_metadata("output.gpr")
```

### 5. Utility Functions

Convenient functions for common operations:

```python
from python_gpr.metadata import (
    get_camera_info, get_exposure_settings, 
    get_image_dimensions, get_metadata_summary
)

# Get camera information
camera_info = get_camera_info("sample.gpr")
print(f"Make: {camera_info['make']}")
print(f"Model: {camera_info['model']}")
print(f"Serial: {camera_info['serial']}")

# Get exposure settings
exposure = get_exposure_settings("sample.gpr")
print(f"Exposure Time: {exposure['exposure_time']}")
print(f"F-Stop: {exposure['f_stop']}")
print(f"ISO: {exposure['iso_speed']}")
print(f"Focal Length: {exposure['focal_length']}")

# Get image dimensions
width, height = get_image_dimensions("sample.gpr")
print(f"Resolution: {width}x{height}")

# Get comprehensive summary
summary = get_metadata_summary("sample.gpr")
for key, value in summary.items():
    print(f"{key}: {value}")
```

### 6. Metadata Copying

Copy metadata between files:

```python
from python_gpr.metadata import copy_metadata

# Copy all metadata from source to target
copy_metadata("source.gpr", "target.dng")
```

## Supported EXIF Fields

The implementation provides access to all standard EXIF fields:

### Camera Information
- `camera_make` - Camera manufacturer
- `camera_model` - Camera model name
- `camera_serial` - Camera serial number
- `software_version` - Firmware/software version
- `user_comment` - User comment
- `image_description` - Image description

### Exposure Settings
- `exposure_time` - Exposure time in seconds
- `exposure_time_rational` - Exposure time as fraction (numerator, denominator)
- `f_stop_number` - F-stop number
- `f_stop_number_rational` - F-stop as fraction
- `aperture` - Aperture value
- `aperture_rational` - Aperture as fraction
- `iso_speed_rating` - ISO speed setting
- `focal_length` - Focal length in mm
- `focal_length_rational` - Focal length as fraction
- `focal_length_in_35mm_film` - 35mm equivalent focal length
- `exposure_bias` - Exposure compensation
- `exposure_bias_rational` - Exposure bias as fraction

### Camera Settings
- `exposure_program` - Exposure program mode
- `metering_mode` - Metering mode
- `light_source` - Light source type
- `flash` - Flash setting
- `white_balance` - White balance setting
- `scene_capture_type` - Scene capture type
- `exposure_mode` - Exposure mode
- `sharpness` - Sharpness setting
- `saturation` - Saturation setting
- `contrast` - Contrast setting
- `gain_control` - Gain control setting
- `digital_zoom` - Digital zoom ratio
- `scene_type` - Scene type
- `file_source` - File source
- `sensing_method` - Sensing method

### Date/Time Information
- `date_time_original` - Original capture date/time
  - `year`, `month`, `day`, `hour`, `minute`, `second`
- `date_time_digitized` - Digitization date/time
  - `year`, `month`, `day`, `hour`, `minute`, `second`

### GPS Information (if available)
- `gps_info` - GPS metadata
  - `valid` - Whether GPS data is available
  - `version_id` - GPS version
  - `latitude_ref` - Latitude reference (N/S)
  - `latitude` - Latitude coordinates as list of (numerator, denominator) tuples
  - `longitude_ref` - Longitude reference (E/W)
  - `longitude` - Longitude coordinates as list of (numerator, denominator) tuples
  - `altitude_ref` - Altitude reference
  - `altitude` - Altitude as (numerator, denominator) tuple
  - `satellites` - Satellites used
  - `status` - GPS status
  - And many other GPS-specific fields

## GPR-Specific Metadata

### Image Properties
- `input_width` - Image width in pixels
- `input_height` - Image height in pixels
- `input_pitch` - Image pitch in pixels

### Compression Settings
- `fast_encoding` - Whether fast encoding is enabled
- `compute_md5sum` - Whether MD5 checksum is computed
- `enable_preview` - Whether preview image is enabled

### Preview Image Information
- `preview_image` - Preview image metadata
  - `has_preview` - Whether preview is available
  - `width` - Preview width
  - `height` - Preview height
  - `jpg_preview_size` - Preview JPEG size in bytes

### GPMF Information
- `gpmf_payload` - GPMF metadata
  - `has_gpmf` - Whether GPMF data is available
  - `size` - GPMF data size in bytes

### Profile and Tuning Information
- `profile_info` - Camera color profile information
- `tuning_info` - Camera tuning parameters

## Error Handling

The metadata functions provide comprehensive error handling:

```python
from python_gpr.metadata import extract_exif
from python_gpr.exceptions import GPRError, GPRFileError, GPRConversionError

try:
    exif_data = extract_exif("sample.gpr")
except FileNotFoundError:
    print("File not found")
except GPRFileError as e:
    print(f"File error: {e}")
except GPRConversionError as e:
    print(f"Conversion error: {e}")
except GPRError as e:
    print(f"GPR error: {e}")
except ValueError as e:
    print(f"Value error: {e}")
```

## Performance Considerations

- Metadata extraction is optimized to read only the necessary parts of the file
- The `GPRMetadata` class caches loaded metadata to avoid repeated parsing
- Large files are handled efficiently without loading the entire image data into memory
- Rational values (fractions) are provided alongside decimal values for precision

## Format Support

The metadata functionality works with:
- **.gpr files** - Full GPR format support with all GPR-specific metadata
- **.dng files** - Adobe DNG format with standard EXIF data
- **Both formats** support metadata modification and persistence

## Thread Safety

The metadata functions are thread-safe for read operations. For write operations (metadata modification), ensure proper synchronization when accessing the same files from multiple threads.

## Examples

See the following files for complete examples:
- `demo_metadata_comprehensive.py` - Comprehensive demonstration of all features
- `tests/test_metadata_comprehensive.py` - Complete test suite with examples
- Individual demo files for specific use cases

This implementation fulfills all requirements for comprehensive metadata access with complete EXIF data accessibility, DNG metadata field support, GPR-specific metadata exposure, and persistent metadata modification capabilities.