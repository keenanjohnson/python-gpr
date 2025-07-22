# Python GPR Example: Basic Usage

This example demonstrates basic usage of the python-gpr library for converting
between GPR, DNG, and RAW image formats.

## Prerequisites

```bash
pip install python-gpr
```

## Basic Conversion Examples

```python
import python_gpr as gpr

# Convert GPR to DNG
gpr.convert_gpr_to_dng("input.gpr", "output.dng")

# Convert DNG to GPR with custom parameters
parameters = {
    "quality": 4,  # Compression quality (1-5)
    "preserve_metadata": True
}
gpr.convert_dng_to_gpr("input.dng", "output.gpr", parameters=parameters)

# Extract RAW data from GPR
gpr.convert_gpr_to_raw("input.gpr", "output.raw")

# Get image information
info = gpr.get_image_info("input.gpr")
print(f"Dimensions: {info['width']}x{info['height']}")
print(f"Format: {info['format']}")
```

## Object-Oriented Interface

```python
# Load image using object-oriented interface
image = gpr.GPRImage("input.gpr")

# Get image properties
print(f"Size: {image.width}x{image.height}")
print(f"Format: {image.format}")

# Convert to different formats
image.to_dng("output.dng")

# Get raw image data as numpy array
import numpy as np
raw_data = image.to_numpy()
print(f"Raw data shape: {raw_data.shape}")
print(f"Data type: {raw_data.dtype}")
```

## Batch Processing

```python
import os
import glob

def batch_convert_gpr_to_dng(input_dir, output_dir):
    """Convert all GPR files in a directory to DNG format."""
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all GPR files
    gpr_files = glob.glob(os.path.join(input_dir, "*.gpr"))
    
    for gpr_file in gpr_files:
        # Generate output filename
        basename = os.path.splitext(os.path.basename(gpr_file))[0]
        dng_file = os.path.join(output_dir, f"{basename}.dng")
        
        try:
            print(f"Converting {gpr_file} -> {dng_file}")
            gpr.convert_gpr_to_dng(gpr_file, dng_file)
            print("✓ Success")
        except Exception as e:
            print(f"✗ Error: {e}")

# Usage
batch_convert_gpr_to_dng("./gpr_images", "./dng_images")
```

## Error Handling

```python
import python_gpr as gpr

def safe_convert(input_path, output_path):
    """Convert GPR to DNG with proper error handling."""
    
    try:
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Perform conversion
        gpr.convert_gpr_to_dng(input_path, output_path)
        print(f"Successfully converted {input_path} to {output_path}")
        
    except FileNotFoundError as e:
        print(f"File error: {e}")
    except ValueError as e:
        print(f"Parameter error: {e}")
    except RuntimeError as e:
        print(f"Conversion error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Usage
safe_convert("input.gpr", "output.dng")
```

## Working with Metadata

```python
def analyze_image(file_path):
    """Analyze GPR or DNG image and print detailed information."""
    
    try:
        info = gpr.get_image_info(file_path)
        
        print(f"File: {file_path}")
        print(f"Format: {info['format']}")
        print(f"Dimensions: {info['width']} x {info['height']}")
        
        if 'metadata' in info:
            metadata = info['metadata']
            print(f"Camera: {metadata.get('camera_model', 'Unknown')}")
            print(f"ISO: {metadata.get('iso', 'Unknown')}")
            print(f"Exposure: {metadata.get('exposure_time', 'Unknown')}")
            
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")

# Usage
analyze_image("sample.gpr")
```

## Performance Optimization

```python
import time
import python_gpr as gpr

def benchmark_conversion(input_file):
    """Benchmark different conversion operations."""
    
    print(f"Benchmarking conversions for {input_file}")
    
    # Test GPR to DNG conversion
    start_time = time.time()
    gpr.convert_gpr_to_dng(input_file, "temp_output.dng")
    dng_time = time.time() - start_time
    print(f"GPR -> DNG: {dng_time:.2f} seconds")
    
    # Test GPR to RAW conversion
    start_time = time.time()
    gpr.convert_gpr_to_raw(input_file, "temp_output.raw")
    raw_time = time.time() - start_time
    print(f"GPR -> RAW: {raw_time:.2f} seconds")
    
    # Clean up temporary files
    for temp_file in ["temp_output.dng", "temp_output.raw"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)

# Usage
benchmark_conversion("sample.gpr")
```

Note: This example shows the intended API. The actual implementation will be available once the GPR library integration is complete.