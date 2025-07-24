# python-gpr Compatibility Matrix

This document outlines the tested compatibility matrix for the python-gpr library across different platforms, Python versions, and NumPy versions.

## Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| **Linux** (Ubuntu 20.04+) | ✅ Fully Supported | Primary development platform |
| **macOS** (11.0+) | ✅ Fully Supported | Tested on Intel and Apple Silicon |
| **Windows** (10+) | ✅ Fully Supported | Tested on x64 architecture |

## Python Version Support

| Python Version | Status | Notes |
|----------------|--------|-------|
| **3.9** | ✅ Supported | Minimum supported version |
| **3.10** | ✅ Supported | Recommended for stability |
| **3.11** | ✅ Supported | Good performance improvements |
| **3.12** | ✅ Supported | Latest features, actively tested |
| **3.13+** | 🔄 Future | Not yet tested, may work |

## NumPy Version Compatibility

| NumPy Version | Python 3.9 | Python 3.10 | Python 3.11 | Python 3.12 | Notes |
|---------------|-------------|--------------|--------------|--------------|-------|
| **1.20.x** | ✅ | ✅ | ✅ | ✅ | Minimum supported version |
| **1.21.x** | ✅ | ✅ | ✅ | ✅ | Stable |
| **1.22.x** | ✅ | ✅ | ✅ | ✅ | Stable |
| **1.23.x** | ✅ | ✅ | ✅ | ✅ | Stable |
| **1.24.x** | ✅ | ✅ | ✅ | ✅ | Stable |
| **1.25.x** | ✅ | ✅ | ✅ | ✅ | Stable |
| **1.26.x** | ✅ | ✅ | ✅ | ✅ | Latest 1.x series |
| **2.0.x** | ⚠️ | ✅ | ✅ | ✅ | Some combinations may have issues |
| **2.1.x+** | ⚠️ | ✅ | ✅ | ✅ | Latest features |

### NumPy 2.0+ Notes
- NumPy 2.0 introduced breaking changes in some APIs
- String dtypes and array creation may behave differently
- Most functionality remains compatible
- Some platform-specific combinations may have installation issues

## Platform-Specific Considerations

### Linux
- **File paths**: Full POSIX path support including Unicode
- **Memory management**: Standard Linux memory allocation
- **Dependencies**: Requires `build-essential` for C++ compilation
- **Performance**: Generally fastest due to optimized builds

### macOS
- **File paths**: Full Unicode support, case-sensitive filesystem handling
- **Memory management**: Standard Darwin memory allocation
- **Dependencies**: Requires Xcode command line tools or CMake via Homebrew
- **Performance**: Good performance on both Intel and Apple Silicon

### Windows
- **File paths**: Windows path separators handled automatically, Unicode support
- **Memory management**: Windows heap management
- **Dependencies**: Requires Visual Studio Build Tools or MinGW
- **Performance**: Comparable to other platforms

## Known Platform-Specific Issues

### Windows-Specific
- Some NumPy 2.0.x combinations may have installation issues on older Windows versions
- File path length limitations may affect deeply nested directories
- Unicode paths in legacy Windows applications may need special handling

### macOS-Specific
- Apple Silicon (M1/M2) requires universal binary builds for some NumPy versions
- Homebrew vs system Python may have different behaviors
- Code signing requirements for distributed applications

### Linux-Specific
- Different distributions may have varying dependency requirements
- Alpine Linux requires additional considerations for NumPy
- glibc vs musl libc compatibility for binary distributions

## Testing Matrix

The CI system tests the following combinations:

| OS | Python | NumPy | Test Type |
|----|--------|-------|-----------|
| Ubuntu | 3.9-3.12 | 1.20.*, 1.24.*, 2.0.*, latest | Standard |
| Windows | 3.9-3.12 | 1.20.*, 1.24.*, 2.0.*, latest | Standard |
| macOS | 3.9-3.12 | 1.20.*, 1.24.*, 2.0.*, latest | Standard |
| Ubuntu | 3.12 | latest | Comprehensive |

## Recommended Combinations

For **production use**:
- Python 3.10 or 3.11 with NumPy 1.24.x or 1.25.x
- Any supported platform

For **development**:
- Python 3.12 with NumPy latest
- Linux or macOS for best development experience

For **maximum compatibility**:
- Python 3.9 with NumPy 1.20.x
- Works on all supported platforms

## Performance Considerations

### Memory Usage
- NumPy 2.0+ may use slightly more memory due to dtype changes
- Platform memory allocators can affect performance:
  - Linux: Generally most efficient
  - macOS: Good performance, especially on Apple Silicon
  - Windows: Comparable but may vary by configuration

### CPU Performance
- C++ extensions perform similarly across platforms
- NumPy operations benefit from platform-optimized BLAS libraries:
  - OpenBLAS (Linux/Windows)
  - Accelerate Framework (macOS)

## Troubleshooting

### Installation Issues
1. **NumPy compilation fails**: Ensure proper build tools are installed
2. **Import errors**: Check Python/NumPy version compatibility
3. **Path issues**: Use `pathlib.Path` for cross-platform compatibility

### Runtime Issues
1. **Memory errors**: Check available RAM and NumPy array sizes
2. **Unicode errors**: Ensure proper file path encoding
3. **Performance issues**: Verify NumPy is using optimized BLAS

## Future Compatibility

### Planned Support
- Python 3.13 when released and stabilized
- NumPy 2.2+ as they become available
- Additional platforms (ARM Linux, etc.) as requested

### Deprecation Timeline
- Python 3.9 support may be dropped when Python 3.13 is released
- NumPy 1.20.x support may be dropped when NumPy 2.5+ is released
- Platform support follows respective vendor support timelines

---

**Last Updated**: December 2024  
**Next Review**: March 2025

For issues related to specific platform combinations, please open an issue on GitHub with:
- Platform details (`platform.platform()`)
- Python version (`sys.version`)  
- NumPy version (`numpy.__version__`)
- Full error traceback