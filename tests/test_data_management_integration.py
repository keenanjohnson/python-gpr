"""
Integration test for test data management system.

This test validates that all components of the test data management
system work correctly together and provide the required functionality.
"""

import pytest
from pathlib import Path


class TestDataManagementIntegration:
    """Integration tests for the complete test data management system."""
    
    def test_comprehensive_test_data_available(self, test_data_manager):
        """Test that comprehensive test data is available."""
        # Should have both real and synthetic data
        all_files = test_data_manager.list_files()
        assert len(all_files) >= 10, "Should have comprehensive test data set"
        
        # Should have real data
        real_files = test_data_manager.list_files(file_type="gpr")
        assert len(real_files) >= 1, "Should have at least one real GPR file"
        
        # Should have synthetic data
        synthetic_files = test_data_manager.list_files(file_type="synthetic_gpr")
        assert len(synthetic_files) >= 5, "Should have multiple synthetic files"
    
    def test_various_image_types_and_sizes(self, test_data_manager):
        """Test that test data covers various image types and sizes."""
        files_info = []
        for filename in test_data_manager.list_files():
            info = test_data_manager.get_file_info(filename)
            if info.get("width") and info.get("height"):
                files_info.append((filename, info["width"], info["height"], info["size"]))
        
        # Should have multiple different resolutions
        resolutions = {(info[1], info[2]) for info in files_info}
        assert len(resolutions) >= 5, f"Should have multiple resolutions, got {len(resolutions)}"
        
        # Should have size variety (small, medium, large files)
        sizes = [info[3] for info in files_info]
        min_size = min(sizes) if sizes else 0
        max_size = max(sizes) if sizes else 0
        
        # Should have files ranging from small to large
        assert min_size < 10000, "Should have small test files"
        assert max_size > 1000000, "Should have large test files"
    
    def test_test_data_versioning_and_distribution(self, test_data_manager, validate_test_data):
        """Test that test data is properly versioned and distributed."""
        # Check manifest has version information
        manifest = test_data_manager.manifest
        assert "version" in manifest
        assert "generated" in manifest
        assert manifest["version"] == "1.0.0"
        
        # All files should be valid (properly distributed)
        assert isinstance(validate_test_data, dict)
        valid_files = sum(validate_test_data.values())
        total_files = len(validate_test_data)
        
        assert valid_files == total_files, f"All files should be valid: {valid_files}/{total_files}"
    
    def test_real_and_synthetic_data_integration(self, sample_gpr_file, synthetic_test_data):
        """Test that tests work with both real and synthetic data."""
        # Real data should be available
        assert sample_gpr_file.exists()
        assert sample_gpr_file.stat().st_size > 0
        
        # Synthetic data should be available
        assert len(synthetic_test_data) >= 4
        for name, path in synthetic_test_data.items():
            assert path.exists(), f"Synthetic file {name} should exist"
        
        # Should have variety in synthetic data
        sizes = [path.stat().st_size for path in synthetic_test_data.values()]
        assert min(sizes) == 0, "Should have empty file"
        assert max(sizes) > 100000, "Should have large synthetic file"
    
    def test_edge_cases_coverage(self, corrupted_gpr, empty_gpr):
        """Test that edge cases are covered by test data."""
        # Corrupted file for error handling
        assert corrupted_gpr.exists()
        with open(corrupted_gpr, 'rb') as f:
            header = f.read(4)
            assert header != b"GPR\x00", "Should have invalid header"
        
        # Empty file for boundary testing
        assert empty_gpr.exists()
        assert empty_gpr.stat().st_size == 0, "Should be empty"
    
    def test_test_data_use_case_classification(self, test_data_manager):
        """Test that test data is properly classified by use case."""
        # Check that files have appropriate use case classifications
        use_cases_found = set()
        
        for filename in test_data_manager.list_files():
            info = test_data_manager.get_file_info(filename)
            file_use_cases = info.get("use_cases", [])
            use_cases_found.update(file_use_cases)
        
        # Should have essential use cases covered
        essential_use_cases = {
            "conversion_testing",
            "format_detection", 
            "error_handling",
            "unit_testing",
            "stress_testing"
        }
        
        missing_use_cases = essential_use_cases - use_cases_found
        assert not missing_use_cases, f"Missing essential use cases: {missing_use_cases}"
    
    def test_performance_with_different_file_sizes(self, test_data_manager):
        """Test performance considerations with different file sizes."""
        # Get files suitable for performance testing (small) and stress testing (large)
        small_files = []
        large_files = []
        
        for filename in test_data_manager.list_files():
            info = test_data_manager.get_file_info(filename)
            use_cases = info.get("use_cases", [])
            
            # Small files good for performance testing
            if "performance_testing" in use_cases:
                small_files.append(filename)
            
            # Large files good for stress testing
            if "stress_testing" in use_cases or info["size"] > 1000000:
                large_files.append(filename)
        
        # Should have both small files for quick tests and large files for stress tests
        assert len(small_files) >= 1, "Should have small files for performance testing"
        assert len(large_files) >= 1, "Should have large files for stress testing"
    
    @pytest.mark.stress_test
    def test_memory_usage_with_large_files(self, test_data_manager):
        """Test memory considerations with large test files."""
        # Find the largest test file
        largest_file = None
        largest_size = 0
        
        for filename in test_data_manager.list_files():
            info = test_data_manager.get_file_info(filename)
            if info["size"] > largest_size:
                largest_size = info["size"]
                largest_file = filename
        
        assert largest_file is not None, "Should have at least one test file"
        assert largest_size > 5000000, "Should have files large enough for memory testing"
        
        # Verify file is accessible
        file_path = test_data_manager.get_file_path(largest_file)
        assert file_path.exists()
    
    def test_test_data_validation_workflow(self, test_data_manager):
        """Test the complete test data validation workflow."""
        from tests.test_data import validate_all_test_data, ensure_test_data_available
        
        # Full validation should work
        validation_results = validate_all_test_data()
        assert isinstance(validation_results, dict)
        assert len(validation_results) > 0
        
        # Availability check should work
        is_available = ensure_test_data_available()
        assert isinstance(is_available, bool)
        
        # If validation passes, availability should be True
        all_valid = all(validation_results.values())
        if all_valid:
            assert is_available, "If all files are valid, availability should be True"
    
    def test_fixture_integration(self, sample_gpr_file, small_synthetic_gpr, 
                                large_synthetic_gpr, temp_dir):
        """Test that all fixtures work together properly."""
        # All fixture-provided files should exist
        assert sample_gpr_file.exists()
        assert small_synthetic_gpr.exists()
        assert large_synthetic_gpr.exists()
        assert temp_dir.exists()
        
        # Files should have expected characteristics
        assert sample_gpr_file.suffix in [".GPR", ".gpr"]
        assert small_synthetic_gpr.suffix == ".gpr"
        assert large_synthetic_gpr.suffix == ".gpr"
        
        # Sizes should be appropriate
        small_size = small_synthetic_gpr.stat().st_size
        large_size = large_synthetic_gpr.stat().st_size
        assert large_size > small_size, "Large file should be bigger than small file"
        
        # Temp dir should be writable
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        assert test_file.exists()
    
    def test_documentation_consistency(self, test_data_manager):
        """Test that actual test data matches documentation."""
        doc_path = Path(__file__).parent / "TEST_DATA_MANAGEMENT.md"
        assert doc_path.exists(), "Documentation should exist"
        
        # Check that documented files actually exist
        documented_files = [
            "2024_10_08_10-37-22.GPR",
            "tiny_64x48.gpr", 
            "small_320x240.gpr",
            "4k_3840x2160.gpr",
            "corrupted_header.gpr",
            "empty_file.gpr"
        ]
        
        available_files = test_data_manager.list_files()
        for doc_file in documented_files:
            assert doc_file in available_files, f"Documented file {doc_file} should exist"