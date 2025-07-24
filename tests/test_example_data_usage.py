"""
Example test demonstrating the new test data management system.

This test shows how to use the new test data management
system in actual test cases.
"""

import unittest
from pathlib import Path

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

try:
    from .test_data import get_test_data_manager, validate_all_test_data
except ImportError:
    # Handle case when running with unittest discovery
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from test_data import get_test_data_manager, validate_all_test_data


class TestExampleDataUsage(unittest.TestCase):
    """Example tests demonstrating the test data management system."""
    
    def setUp(self):
        """Set up test data manager."""
        self.test_data_manager = get_test_data_manager()

    @unittest.skipUnless(PYTEST_AVAILABLE, "Requires real data - normally marked with pytest")
    def test_with_real_gpr_file(self):
        """Test using the real GPR test file."""
        # Find real GPR files
        real_files = self.test_data_manager.list_files(file_type="gpr")
        if real_files:
            sample_gpr_file = self.test_data_manager.get_file_path(real_files[0])
            self.assertTrue(sample_gpr_file.exists())
            self.assertIn(sample_gpr_file.suffix.lower(), [".gpr"])
            self.assertGreater(sample_gpr_file.stat().st_size, 0)
            print(f"Using real GPR file: {sample_gpr_file.name}")

    def test_with_synthetic_data(self):
        """Test using synthetic test data."""
        # Get synthetic test data
        synthetic_files = self.test_data_manager.list_files(file_type="synthetic_gpr")
        
        # Look for specific types of synthetic files
        small_files = [f for f in synthetic_files if "small" in f]
        large_files = [f for f in synthetic_files if "large" in f or "4k" in f]
        corrupted_files = [f for f in synthetic_files if "corrupted" in f]
        empty_files = [f for f in synthetic_files if "empty" in f]
        
        # Check we have expected variety
        self.assertGreater(len(synthetic_files), 0, "Should have synthetic files")
        
        # All synthetic files should exist
        for filename in synthetic_files:
            path = self.test_data_manager.get_file_path(filename)
            self.assertTrue(path.exists(), f"Synthetic file {filename} should exist")
        
        # Check sizes are appropriate if we have the expected files
        if small_files and large_files:
            small_size = self.test_data_manager.get_file_path(small_files[0]).stat().st_size
            large_size = self.test_data_manager.get_file_path(large_files[0]).stat().st_size
            self.assertGreater(large_size, small_size, "Large file should be bigger than small file")
        
        if empty_files:
            empty_size = self.test_data_manager.get_file_path(empty_files[0]).stat().st_size
            self.assertEqual(empty_size, 0, "Empty file should be 0 bytes")

    def test_with_corrupted_data(self):
        """Test handling of corrupted GPR files."""
        corrupted_files = [f for f in self.test_data_manager.list_files() if "corrupted" in f]
        
        if corrupted_files:
            corrupted_gpr = self.test_data_manager.get_file_path(corrupted_files[0])
            self.assertTrue(corrupted_gpr.exists())
            self.assertGreater(corrupted_gpr.stat().st_size, 0)
            
            # Test that file doesn't start with valid GPR header
            with open(corrupted_gpr, 'rb') as f:
                header = f.read(4)
                self.assertNotEqual(header, b"GPR\x00", "Corrupted file should not have valid header")

    def test_with_large_synthetic_gpr(self):
        """Test with large synthetic GPR file."""
        large_files = [f for f in self.test_data_manager.list_files() 
                      if "large" in f or "4k" in f or "fullhd" in f]
        
        if large_files:
            large_synthetic_gpr = self.test_data_manager.get_file_path(large_files[0])
            self.assertTrue(large_synthetic_gpr.exists())
            
            # Should be reasonably large
            size = large_synthetic_gpr.stat().st_size
            expected_min_size = 1000  # Minimal size expectation
            self.assertGreater(size, expected_min_size, f"Large file should be at least {expected_min_size} bytes")

    def test_test_data_manager_integration(self):
        """Test integration with test data manager."""
        # test_data_manager provides access to the registry
        files = self.test_data_manager.list_files()
        self.assertIsInstance(files, list)
        
        # Should have at least one file
        if files:
            # Test getting file info
            first_file = files[0]
            info = self.test_data_manager.get_file_info(first_file)
            self.assertIsInstance(info, dict)
            self.assertIn("type", info)

    def test_validate_test_data_integration(self):
        """Test test data validation integration."""
        # Get validation results
        validate_test_data = validate_all_test_data()
        self.assertIsInstance(validate_test_data, dict)
        
        # All validation results should be boolean
        for filename, is_valid in validate_test_data.items():
            self.assertIsInstance(is_valid, bool, f"Validation result for {filename} should be boolean")

    def test_different_synthetic_file_types(self):
        """Test using multiple synthetic file types."""
        small_files = [f for f in self.test_data_manager.list_files() if "small" in f]
        empty_files = [f for f in self.test_data_manager.list_files() if "empty" in f]
        
        # Check files exist if available
        if small_files:
            small_synthetic_gpr = self.test_data_manager.get_file_path(small_files[0])
            self.assertTrue(small_synthetic_gpr.exists())
            small_size = small_synthetic_gpr.stat().st_size
            self.assertGreater(small_size, 0)
        
        if empty_files:
            empty_gpr = self.test_data_manager.get_file_path(empty_files[0])
            self.assertTrue(empty_gpr.exists())
            empty_size = empty_gpr.stat().st_size
            self.assertEqual(empty_size, 0)


if __name__ == '__main__':
    unittest.main()