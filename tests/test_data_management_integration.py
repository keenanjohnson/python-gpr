"""
Integration test for test data management system.

This test validates that all components of the test data management
system work correctly together and provide the required functionality.
"""

import unittest
from pathlib import Path

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

try:
    from .test_data import get_test_data_manager, SyntheticDataGenerator
except ImportError:
    # Handle case when running with unittest discovery
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from test_data import get_test_data_manager, SyntheticDataGenerator


class TestDataManagementIntegration(unittest.TestCase):
    """Integration tests for the complete test data management system."""
    
    def setUp(self):
        """Set up test data manager."""
        self.test_data_manager = get_test_data_manager()
    
    def test_comprehensive_test_data_available(self):
        """Test that comprehensive test data is available."""
        # Should have both real and synthetic data
        all_files = self.test_data_manager.list_files()
        self.assertGreaterEqual(len(all_files), 10, "Should have comprehensive test data set")
        
        # Should have real data
        real_files = self.test_data_manager.list_files(file_type="gpr")
        self.assertGreaterEqual(len(real_files), 1, "Should have at least one real GPR file")
        
        # Should have synthetic data
        synthetic_files = self.test_data_manager.list_files(file_type="synthetic_gpr")
        self.assertGreaterEqual(len(synthetic_files), 5, "Should have multiple synthetic files")
    
    def test_various_image_types_and_sizes(self):
        """Test that test data covers various image types and sizes."""
        files_info = []
        for filename in self.test_data_manager.list_files():
            info = self.test_data_manager.get_file_info(filename)
            if info.get("width") and info.get("height"):
                files_info.append((filename, info["width"], info["height"], info["size"]))
        
        # Should have multiple different resolutions
        resolutions = {(info[1], info[2]) for info in files_info}
        self.assertGreaterEqual(len(resolutions), 5, f"Should have multiple resolutions, got {len(resolutions)}")
        
        # Should have size variety (small, medium, large files)
        sizes = [info[3] for info in files_info]
        min_size = min(sizes) if sizes else 0
        max_size = max(sizes) if sizes else 0
        
        # Should have files ranging from small to large
        self.assertLess(min_size, 10000, "Should have small test files")
        self.assertGreater(max_size, 1000000, "Should have large test files")
    
    def test_test_data_versioning_and_distribution(self):
        """Test that test data is properly versioned and distributed."""
        # Check manifest has version information
        manifest = self.test_data_manager.manifest
        self.assertIn("version", manifest)
        self.assertIn("generated", manifest)
        self.assertEqual(manifest["version"], "1.0.0")
        
        # All files should be valid (properly distributed)
        from test_data import validate_all_test_data
        validate_test_data = validate_all_test_data()
        self.assertIsInstance(validate_test_data, dict)
        valid_files = sum(validate_test_data.values())
        total_files = len(validate_test_data)
        
        self.assertEqual(valid_files, total_files, f"All files should be valid: {valid_files}/{total_files}")
    
    def test_real_and_synthetic_data_integration(self):
        """Test that tests work with both real and synthetic data."""
        # Real data should be available
        real_files = self.test_data_manager.list_files(file_type="gpr")
        if real_files:
            sample_gpr_file = self.test_data_manager.get_file_path(real_files[0])
            self.assertTrue(sample_gpr_file.exists())
            self.assertGreater(sample_gpr_file.stat().st_size, 0)
        
        # Synthetic data should be available
        synthetic_files = self.test_data_manager.list_files(file_type="synthetic_gpr")
        self.assertGreaterEqual(len(synthetic_files), 4)
        for filename in synthetic_files:
            path = self.test_data_manager.get_file_path(filename)
            self.assertTrue(path.exists(), f"Synthetic file {filename} should exist")
        
        # Should have variety in synthetic data
        sizes = [self.test_data_manager.get_file_path(f).stat().st_size for f in synthetic_files]
        self.assertEqual(min(sizes), 0, "Should have empty file")
        self.assertGreater(max(sizes), 100000, "Should have large synthetic file")
    
    def test_edge_cases_coverage(self):
        """Test that edge cases are covered by test data."""
        # Look for corrupted file for error handling
        corrupted_files = [f for f in self.test_data_manager.list_files() if "corrupted" in f]
        if corrupted_files:
            corrupted_gpr = self.test_data_manager.get_file_path(corrupted_files[0])
            self.assertTrue(corrupted_gpr.exists())
            with open(corrupted_gpr, 'rb') as f:
                header = f.read(4)
                self.assertNotEqual(header, b"GPR\x00", "Should have invalid header")
        
        # Look for empty file for boundary testing
        empty_files = [f for f in self.test_data_manager.list_files() if "empty" in f]
        if empty_files:
            empty_gpr = self.test_data_manager.get_file_path(empty_files[0])
            self.assertTrue(empty_gpr.exists())
            self.assertEqual(empty_gpr.stat().st_size, 0, "Should be empty")
    
    def test_test_data_use_case_classification(self):
        """Test that test data is properly classified by use case."""
        # Check that files have appropriate use case classifications
        use_cases_found = set()
        
        for filename in self.test_data_manager.list_files():
            info = self.test_data_manager.get_file_info(filename)
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
        self.assertFalse(missing_use_cases, f"Missing essential use cases: {missing_use_cases}")
    
    def test_performance_with_different_file_sizes(self):
        """Test performance considerations with different file sizes."""
        # Get files suitable for performance testing (small) and stress testing (large)
        small_files = []
        large_files = []
        
        for filename in self.test_data_manager.list_files():
            info = self.test_data_manager.get_file_info(filename)
            use_cases = info.get("use_cases", [])
            
            # Small files good for performance testing
            if "performance_testing" in use_cases:
                small_files.append(filename)
            
            # Large files good for stress testing
            if "stress_testing" in use_cases or info["size"] > 1000000:
                large_files.append(filename)
        
        # Should have both small files for quick tests and large files for stress tests
        self.assertGreaterEqual(len(small_files), 1, "Should have small files for performance testing")
        self.assertGreaterEqual(len(large_files), 1, "Should have large files for stress testing")
    
    @unittest.skipUnless(PYTEST_AVAILABLE, "Requires pytest for stress test marking")
    def test_memory_usage_with_large_files(self):
        """Test memory considerations with large test files."""
        # Find the largest test file
        largest_file = None
        largest_size = 0
        
        for filename in self.test_data_manager.list_files():
            info = self.test_data_manager.get_file_info(filename)
            if info["size"] > largest_size:
                largest_size = info["size"]
                largest_file = filename
        
        self.assertIsNotNone(largest_file, "Should have at least one test file")
        self.assertGreater(largest_size, 5000000, "Should have files large enough for memory testing")
        
        # Verify file is accessible
        file_path = self.test_data_manager.get_file_path(largest_file)
        self.assertTrue(file_path.exists())
    
    def test_test_data_validation_workflow(self):
        """Test the complete test data validation workflow."""
        try:
            from .test_data import validate_all_test_data, ensure_test_data_available
        except ImportError:
            from test_data import validate_all_test_data, ensure_test_data_available
        
        # Full validation should work
        validation_results = validate_all_test_data()
        self.assertIsInstance(validation_results, dict)
        self.assertGreater(len(validation_results), 0)
        
        # Availability check should work
        is_available = ensure_test_data_available()
        self.assertIsInstance(is_available, bool)
        
        # If validation passes, availability should be True
        all_valid = all(validation_results.values())
        if all_valid:
            self.assertTrue(is_available, "If all files are valid, availability should be True")


if __name__ == '__main__':
    unittest.main()