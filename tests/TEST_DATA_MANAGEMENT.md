# Test Data Management

This document describes the test data management system for the python-gpr test suite.

## Overview

The test data management system provides:

- **Comprehensive test data set** with real and synthetic GPR files
- **Version tracking and integrity validation** for all test data
- **Easy access through pytest fixtures** for different testing scenarios
- **Synthetic data generation** for edge cases and specific test requirements

## Test Data Types

### Real Data
- `2024_10_08_10-37-22.GPR` - Production GPR file for real-world testing (15.9MB)

### Synthetic Data

#### Basic Test Files
- `tiny_64x48.gpr` - Minimal file for quick tests (3KB)
- `small_320x240.gpr` - Small file for basic testing (77KB)
- `medium_640x480.gpr` - Medium file for standard testing (301KB)

#### Standard Resolutions
- `hd_1280x720.gpr` - HD resolution for common use cases (901KB)
- `fullhd_1920x1080.gpr` - Full HD for standard testing (2MB)

#### High Resolution
- `4k_3840x2160.gpr` - 4K resolution for stress testing (8MB)

#### Aspect Ratio Variants
- `wide_2560x720.gpr` - Ultra-wide aspect ratio (1.8MB)
- `tall_720x2560.gpr` - Portrait/tall aspect ratio (1.8MB)
- `square_1024x1024.gpr` - Square aspect ratio (1.1MB)

#### Error Condition Files
- `corrupted_header.gpr` - File with invalid header for error handling
- `empty_file.gpr` - Empty file for edge case testing
- `truncated_file.gpr` - Incomplete file for robustness testing

## Using Test Data in Tests

### Pytest Fixtures

The test suite provides several fixtures for easy access to test data:

```python
def test_with_real_data(sample_gpr_file):
    """Test using real GPR file."""
    assert sample_gpr_file.exists()
    # File is automatically available from test data

def test_with_synthetic_data(synthetic_test_data):
    """Test using synthetic data."""
    small_file = synthetic_test_data["small_gpr"]
    large_file = synthetic_test_data["large_gpr"]
    # Multiple synthetic files available

def test_with_specific_synthetic_file(small_synthetic_gpr):
    """Test with specific synthetic file type."""
    assert small_synthetic_gpr.exists()
    # Direct access to specific file types

def test_error_handling(corrupted_gpr):
    """Test error handling with corrupted file."""
    # Test robustness with intentionally invalid data
```

### Available Fixtures

- `test_data_manager` - Access to the test data registry
- `sample_gpr_file` - Real GPR file for authentic testing
- `synthetic_test_data` - Dictionary of all synthetic test files
- `small_synthetic_gpr` - Small valid GPR file
- `large_synthetic_gpr` - Large valid GPR file  
- `corrupted_gpr` - Invalid GPR file for error testing
- `empty_gpr` - Empty file for edge case testing
- `temp_dir` - Temporary directory for test outputs

### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.requires_real_data
def test_real_conversion():
    """Test that requires real GPR data."""
    pass

@pytest.mark.stress_test  
def test_large_file_processing():
    """Stress test with large files."""
    pass

@pytest.mark.edge_case
def test_empty_file_handling():
    """Test edge case scenarios."""
    pass
```

## Test Data Management

### Validation

The system automatically validates test data integrity:

```python
from tests.test_data import validate_all_test_data

# Check all test data files
results = validate_all_test_data()
for filename, is_valid in results.items():
    print(f"{filename}: {'✓' if is_valid else '✗'}")
```

### Manifest System

Test data is tracked in `tests/data/manifest.json` with:

- File metadata (size, checksum, dimensions)
- Use case classifications
- Versioning information
- Validation checksums

### Adding New Test Data

1. **Add real GPR files**: Place in `tests/data/` and run:
   ```bash
   cd tests
   python -c "from test_data import TestDataRegistry; TestDataRegistry().update_manifest('newfile.gpr')"
   ```

2. **Generate synthetic data**: Use the generation script:
   ```bash
   cd tests
   python generate_test_data.py
   ```

3. **Custom synthetic files**: Use the SyntheticDataGenerator:
   ```python
   from tests.test_data import SyntheticDataGenerator
   SyntheticDataGenerator.create_dummy_gpr(
       output_path=Path("custom.gpr"),
       width=1024, height=768,
       content_type="valid"
   )
   ```

## File Organization

```
tests/
├── data/                          # Test data directory
│   ├── manifest.json             # Test data registry
│   ├── 2024_10_08_10-37-22.GPR  # Real GPR file
│   ├── tiny_64x48.gpr           # Small synthetic files
│   ├── 4k_3840x2160.gpr         # Large synthetic files
│   └── corrupted_header.gpr     # Error condition files
├── conftest.py                   # Pytest fixtures
├── test_data.py                  # Test data management utilities
├── generate_test_data.py         # Test data generation script
└── test_example_data_usage.py    # Usage examples
```

## Use Cases by File Type

### Conversion Testing
- Real GPR files for authentic conversion validation
- Various synthetic resolutions for format support testing

### Performance Testing  
- Small files for quick iteration during development
- Large files for memory and performance validation

### Stress Testing
- 4K resolution files for high-load scenarios
- Multiple aspect ratios for edge case coverage

### Error Handling
- Corrupted files for robustness testing
- Empty files for boundary condition testing
- Truncated files for incomplete data scenarios

### Integration Testing
- Mixed real and synthetic data for comprehensive validation
- Full workflow testing with various file types

## Best Practices

1. **Use appropriate fixtures** for your test's needs
2. **Mark tests** with appropriate markers for organization
3. **Test with both real and synthetic data** when possible
4. **Validate assumptions** about test data in your tests
5. **Use temporary directories** for test outputs
6. **Keep test data sizes reasonable** for CI/CD performance

## Maintenance

The test data system is designed to be self-maintaining:

- Automatic integrity checking during test runs
- Manifest updates when files are added/changed
- Validation warnings for missing or invalid files
- Easy regeneration of synthetic test data

For any issues with test data, run the validation script:

```bash
cd tests
python generate_test_data.py --validate-only
```