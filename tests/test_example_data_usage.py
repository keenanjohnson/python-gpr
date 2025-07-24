"""
Example test demonstrating the new test data management system.

This test shows how to use the new test data fixtures and management
system in actual test cases.
"""

import pytest
from pathlib import Path


@pytest.mark.requires_real_data
def test_with_real_gpr_file(sample_gpr_file):
    """Test using the real GPR file fixture."""
    # sample_gpr_file fixture provides a real GPR test file
    assert sample_gpr_file.exists()
    assert sample_gpr_file.suffix == ".GPR"
    assert sample_gpr_file.stat().st_size > 0
    print(f"Using real GPR file: {sample_gpr_file.name}")


def test_with_synthetic_data(synthetic_test_data):
    """Test using synthetic test data."""
    # synthetic_test_data fixture provides a dict of synthetic files
    assert "small_gpr" in synthetic_test_data
    assert "large_gpr" in synthetic_test_data
    assert "corrupted_gpr" in synthetic_test_data
    assert "empty_gpr" in synthetic_test_data
    
    # All synthetic files should exist
    for name, path in synthetic_test_data.items():
        assert path.exists(), f"Synthetic file {name} should exist"
    
    # Check sizes are appropriate
    small_size = synthetic_test_data["small_gpr"].stat().st_size
    large_size = synthetic_test_data["large_gpr"].stat().st_size
    empty_size = synthetic_test_data["empty_gpr"].stat().st_size
    
    assert large_size > small_size, "Large file should be bigger than small file"
    assert empty_size == 0, "Empty file should be 0 bytes"


@pytest.mark.edge_case
def test_with_corrupted_data(corrupted_gpr):
    """Test handling of corrupted GPR files."""
    assert corrupted_gpr.exists()
    assert corrupted_gpr.stat().st_size > 0
    
    # Test that file doesn't start with valid GPR header
    with open(corrupted_gpr, 'rb') as f:
        header = f.read(4)
        assert header != b"GPR\x00", "Corrupted file should not have valid header"


@pytest.mark.stress_test
def test_with_large_synthetic_gpr(large_synthetic_gpr):
    """Test with large synthetic GPR file."""
    assert large_synthetic_gpr.exists()
    
    # Should be reasonably large
    size = large_synthetic_gpr.stat().st_size
    expected_min_size = 4096 * 3072  # At least 1 byte per pixel
    assert size >= expected_min_size, f"Large file should be at least {expected_min_size} bytes"


def test_test_data_manager_integration(test_data_manager):
    """Test integration with test data manager."""
    # test_data_manager fixture provides access to the registry
    files = test_data_manager.list_files()
    assert isinstance(files, list)
    
    # Should have at least one file (the real GPR file)
    if files:
        # Test getting file info
        first_file = files[0]
        info = test_data_manager.get_file_info(first_file)
        assert isinstance(info, dict)
        assert "type" in info


def test_validate_test_data_integration(validate_test_data):
    """Test test data validation integration."""
    # validate_test_data fixture provides validation results
    assert isinstance(validate_test_data, dict)
    
    # All validation results should be boolean
    for filename, is_valid in validate_test_data.items():
        assert isinstance(is_valid, bool), f"Validation result for {filename} should be boolean"


def test_temp_dir_fixture(temp_dir):
    """Test that temp_dir fixture works correctly."""
    assert temp_dir.exists()
    assert temp_dir.is_dir()
    
    # Should be able to create files in temp dir
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")
    assert test_file.exists()
    assert test_file.read_text() == "test content"


def test_different_synthetic_file_types(small_synthetic_gpr, empty_gpr):
    """Test using multiple synthetic file fixtures."""
    # Both files should exist
    assert small_synthetic_gpr.exists()
    assert empty_gpr.exists()
    
    # Should have different sizes
    small_size = small_synthetic_gpr.stat().st_size
    empty_size = empty_gpr.stat().st_size
    
    assert small_size > 0
    assert empty_size == 0