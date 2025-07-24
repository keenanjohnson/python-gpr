#!/usr/bin/env python3
"""
Demo script showing NumPy integration for GPR raw image data access.

This script demonstrates the new NumPy integration functionality
for efficient access to raw image data from GPR files.

Note: This requires the C++ bindings to be built and NumPy to be installed.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import numpy as np
    from python_gpr.core import GPRImage, load_gpr_as_numpy, get_gpr_image_info
    
    print("NumPy Integration Demo for Python-GPR")
    print("=" * 40)
    
    # Example GPR file path (replace with actual GPR file)
    gpr_file = "sample.gpr"
    
    print(f"Processing GPR file: {gpr_file}")
    print()
    
    # Method 1: Using GPRImage class
    print("Method 1: Using GPRImage class")
    try:
        image = GPRImage(gpr_file)
        
        # Get image information
        info = image.get_image_info()
        print(f"Image info: {info}")
        
        # Extract as uint16 array (raw sensor data)
        raw_data = image.to_numpy(dtype="uint16")
        print(f"Raw data shape: {raw_data.shape}")
        print(f"Raw data dtype: {raw_data.dtype}")
        print(f"Raw data range: {raw_data.min()} - {raw_data.max()}")
        
        # Extract as float32 array (normalized 0-1)
        normalized_data = image.to_numpy(dtype="float32")
        print(f"Normalized data shape: {normalized_data.shape}")
        print(f"Normalized data dtype: {normalized_data.dtype}")
        print(f"Normalized data range: {normalized_data.min():.3f} - {normalized_data.max():.3f}")
        
    except (FileNotFoundError, NotImplementedError, ValueError) as e:
        print(f"Error: {e}")
    
    print()
    
    # Method 2: Using standalone functions
    print("Method 2: Using standalone functions")
    try:
        # Get image info
        info = get_gpr_image_info(gpr_file)
        print(f"Image info: {info}")
        
        # Load as NumPy array
        image_array = load_gpr_as_numpy(gpr_file, dtype="uint16")
        print(f"Loaded array shape: {image_array.shape}")
        print(f"Loaded array dtype: {image_array.dtype}")
        
        # Demonstrate array operations
        print(f"Mean pixel value: {image_array.mean():.2f}")
        print(f"Standard deviation: {image_array.std():.2f}")
        
        # Show histogram of pixel values
        hist, bins = np.histogram(image_array.flatten(), bins=50)
        print(f"Histogram (first 10 bins): {hist[:10]}")
        
    except (FileNotFoundError, NotImplementedError, ValueError) as e:
        print(f"Error: {e}")
    
    print()
    
    # Method 3: Memory efficiency demonstration
    print("Method 3: Memory efficiency features")
    try:
        # Zero-copy access for uint16 data
        raw_array = load_gpr_as_numpy(gpr_file, dtype="uint16")
        print(f"Zero-copy uint16 array: {raw_array.nbytes / 1024 / 1024:.2f} MB")
        
        # Normalized float32 copy
        float_array = load_gpr_as_numpy(gpr_file, dtype="float32") 
        print(f"Float32 normalized array: {float_array.nbytes / 1024 / 1024:.2f} MB")
        
        # Demonstrate that modifications to uint16 array affect original data
        # (Note: In practice, be careful with modifying raw data)
        original_value = raw_array[0, 0] if raw_array.size > 0 else 0
        print(f"Original pixel [0,0]: {original_value}")
        
    except (FileNotFoundError, NotImplementedError, ValueError) as e:
        print(f"Error: {e}")
    
    print()
    print("Demo completed!")
    print()
    print("Available data types:")
    print("- 'uint16': Raw sensor data (16-bit unsigned integers)")
    print("- 'float32': Normalized data (0.0 - 1.0 range)")
    print()
    print("Key features:")
    print("- Zero-copy access for uint16 data (memory efficient)")
    print("- Automatic normalization for float32 data")
    print("- Proper memory management for large images")
    print("- Shape information: (height, width)")
    print("- Dtype information preserved")

except ImportError as e:
    if "numpy" in str(e).lower():
        print("Error: NumPy is required for this demo.")
        print("Install with: pip install numpy")
    else:
        print(f"Error: {e}")
        print("Make sure the python-gpr package is installed and built.")
    sys.exit(1)

except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)