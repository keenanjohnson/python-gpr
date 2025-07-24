# python-gpr

This repo is an attempt to make a python compatible binding library to expose the functionality of the gpr library (C/C++) easily in python.

https://github.com/gopro/gpr

This is also somewhat my first experiement using the github copilot agent mode, so use with a bit of caution.

## Setup

This project uses the upstream GPR library as a git submodule. To clone and set up the repository:

```bash
# Clone the repository
git clone https://github.com/keenanjohnson/python-gpr.git
cd python-gpr

# Initialize and update the submodule
git submodule update --init --recursive
```

The GPR library will be available in the `gpr/` subdirectory after running the submodule update command.

## Compatibility

Python-GPR is extensively tested across multiple platforms and versions:

### Supported Platforms
- **Linux** (Ubuntu 20.04+) - Primary development platform
- **macOS** (11.0+) - Intel and Apple Silicon
- **Windows** (10+) - x64 architecture

### Python Versions
- Python 3.9 through 3.12 (actively tested)
- Python 3.13+ (may work, not yet tested)

### NumPy Compatibility
- NumPy 1.20.x through 2.1.x
- Comprehensive compatibility testing across versions
- Full support for NumPy 2.0+ with handling for breaking changes

For detailed compatibility information, including known issues and platform-specific considerations, see [COMPATIBILITY_MATRIX.md](COMPATIBILITY_MATRIX.md).

## Testing

The project includes comprehensive cross-platform testing:

```bash
# Run all tests
python -m unittest discover tests/ -v

# Run specific test modules
python -m unittest tests.test_core_basic -v
python -m unittest tests.test_metadata_basic -v
python -m unittest tests.test_numpy_integration -v
python -m unittest tests.test_platform_compatibility -v
```

The test suite includes:
- Core functionality tests (153+ tests)
- Platform-specific compatibility tests
- NumPy version compatibility validation
- Memory management verification
- Error handling across platforms

No external dependencies are required for the basic tests.

## NumPy Integration

Python-GPR provides efficient NumPy array integration for direct access to raw image data:

### Features

- **Zero-copy data access** for uint16 raw sensor data
- **Multiple data types** supported (uint16, float32)
- **Memory-efficient** handling of large images
- **Proper shape and dtype** information
- **Automatic normalization** for float32 data (0.0 - 1.0 range)

### Usage Examples

```python
import numpy as np
from python_gpr.core import GPRImage, load_gpr_as_numpy, get_gpr_image_info

# Method 1: Using GPRImage class
image = GPRImage("sample.gpr")

# Get image information
info = image.get_image_info()
print(f"Dimensions: {info['width']}x{info['height']}")

# Extract raw uint16 data (zero-copy when possible)
raw_data = image.to_numpy(dtype="uint16")
print(f"Raw data shape: {raw_data.shape}")  # (height, width)

# Extract normalized float32 data
normalized_data = image.to_numpy(dtype="float32")
print(f"Value range: {normalized_data.min():.3f} - {normalized_data.max():.3f}")

# Method 2: Using standalone functions
image_array = load_gpr_as_numpy("sample.gpr", dtype="uint16")
info = get_gpr_image_info("sample.gpr")
```

### Supported Data Types

- **`uint16`**: Raw sensor data (16-bit unsigned integers, 0-65535 range)
- **`float32`**: Normalized data (32-bit float, 0.0-1.0 range)

### Memory Management

The NumPy integration is designed for efficient memory usage:

- **uint16 arrays**: Zero-copy access when possible, directly referencing GPR data
- **float32 arrays**: Efficient conversion with automatic memory cleanup  
- **Large images**: Optimized memory management prevents memory leaks
- **Error handling**: Automatic resource cleanup on exceptions

### Demo Script

Run the included demo to see NumPy integration in action:

```bash
python demo_numpy_integration.py
```

*Note: Requires NumPy to be installed and C++ bindings to be built.*
