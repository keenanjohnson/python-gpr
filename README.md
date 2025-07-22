# python-gpr

[![CI](https://github.com/keenanjohnson/python-gpr/actions/workflows/ci.yml/badge.svg)](https://github.com/keenanjohnson/python-gpr/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/python-gpr.svg)](https://badge.fury.io/py/python-gpr)
[![License](https://img.shields.io/badge/License-Apache%202.0%20OR%20MIT-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Python bindings for the GPR (General Purpose Raw) image format library developed by GoPro.

## Overview

python-gpr provides Python access to the GPR library, enabling conversion between GPR, DNG, RAW, PPM, and JPG image formats with high-performance VC-5 wavelet compression. GPR is a 12-bit raw image format based on Adobe DNG standard that provides better compression ratios (4:1 to 10:1) while maintaining compatibility with DNG-aware applications.

**Key Features:**
- Convert between GPR, DNG, and RAW formats
- High-performance VC-5 wavelet compression
- Scalable thumbnail and preview generation  
- NumPy integration for image data access
- Cross-platform support (Windows, macOS, Linux)
- Object-oriented and functional APIs

## Installation

### Prerequisites
- Python 3.8 or later
- CMake 3.15 or later
- C++11 compatible compiler

### Install from PyPI (coming soon)
```bash
pip install python-gpr
```

### Install from Source
```bash
git clone https://github.com/keenanjohnson/python-gpr.git
cd python-gpr
git submodule update --init --recursive
pip install -e .
```

## Quick Start

```python
import python_gpr as gpr

# Convert GPR to DNG
gpr.convert_gpr_to_dng("input.gpr", "output.dng")

# Convert DNG to GPR with custom parameters
parameters = {"quality": 4, "preserve_metadata": True}
gpr.convert_dng_to_gpr("input.dng", "output.gpr", parameters=parameters)

# Extract RAW data
gpr.convert_gpr_to_raw("input.gpr", "output.raw")

# Get image information
info = gpr.get_image_info("input.gpr")
print(f"Dimensions: {info['width']}x{info['height']}")

# Object-oriented interface
image = gpr.GPRImage("input.gpr")
print(f"Size: {image.width}x{image.height}")
raw_data = image.to_numpy()  # Get as NumPy array
```

## Development Status

⚠️ **This project is currently in early development.** The current version provides a complete project structure and stub implementation. Active development is ongoing to integrate the actual GPR library functionality.

### Current Status:
- [x] Project structure and build system
- [x] Python package skeleton with proper API design
- [x] CI/CD pipeline and testing framework
- [x] Comprehensive development plan
- [ ] GPR library integration (in progress)
- [ ] Core conversion functionality
- [ ] Advanced features (thumbnails, metadata)
- [ ] Documentation and examples

See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) for detailed roadmap and technical specifications.

## API Reference

### Conversion Functions
- `convert_gpr_to_dng(input_path, output_path, parameters=None)` - Convert GPR to DNG
- `convert_dng_to_gpr(input_path, output_path, parameters=None)` - Convert DNG to GPR  
- `convert_gpr_to_raw(input_path, output_path)` - Extract RAW data from GPR
- `get_image_info(file_path)` - Get image metadata and information

### GPRImage Class
- `GPRImage(file_path)` - Load GPR/DNG image
- `width`, `height`, `format` - Image properties
- `to_dng(output_path)` - Convert to DNG format
- `to_numpy()` - Get image data as NumPy array

See [examples/](examples/) for detailed usage examples.

## Contributing

We welcome contributions! Please see our [development plan](DEVELOPMENT_PLAN.md) for technical details and [issues](https://github.com/keenanjohnson/python-gpr/issues) for areas where help is needed.

### Development Setup
```bash
git clone https://github.com/keenanjohnson/python-gpr.git
cd python-gpr
git submodule update --init --recursive
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .[dev]
pytest tests/
```

## Related Projects

- [gopro/gpr](https://github.com/gopro/gpr) - Original C/C++ GPR library
- [Adobe DNG SDK](https://www.adobe.com/support/downloads/dng/dng_sdk.html) - Adobe DNG Software Development Kit

## License

This project is dual licensed under either:
- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option, matching the upstream GPR library licensing.
