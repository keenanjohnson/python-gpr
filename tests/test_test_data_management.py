"""
Test the test data management system itself.

This module tests the test data management infrastructure to ensure
it works correctly and provides reliable test data for other tests.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from .test_data import (
    TestDataRegistry,
    SyntheticDataGenerator, 
    get_test_data_manager,
    validate_all_test_data,
    ensure_test_data_available
)


class TestDataRegistryTests(unittest.TestCase):
    """Test the TestDataRegistry class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(self._cleanup)
        
        # Create a test manifest
        self.manifest_data = {
            "version": "1.0.0",
            "description": "Test manifest",
            "generated": "2024-01-01T00:00:00Z",
            "files": {
                "test.gpr": {
                    "type": "gpr",
                    "size": 1000,
                    "checksum": {
                        "algorithm": "sha256",
                        "value": "abc123"
                    },
                    "use_cases": ["testing"]
                }
            }
        }
        
        # Create manifest file
        manifest_path = self.temp_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(self.manifest_data, f)
        
        # Create test data file
        test_file = self.temp_dir / "test.gpr"
        test_file.write_bytes(b"x" * 1000)
        
        self.manager = TestDataRegistry(self.temp_dir)
    
    def _cleanup(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_load_manifest(self):
        """Test manifest loading."""
        manifest = self.manager.manifest
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertIn("test.gpr", manifest["files"])
    
    def test_get_file_path(self):
        """Test getting file paths."""
        file_path = self.manager.get_file_path("test.gpr")
        self.assertEqual(file_path, self.temp_dir / "test.gpr")
        self.assertTrue(file_path.exists())
    
    def test_get_file_path_missing(self):
        """Test getting path for missing file."""
        with self.assertRaises(FileNotFoundError):
            self.manager.get_file_path("missing.gpr")
    
    def test_validate_file_size(self):
        """Test file size validation."""
        # File should validate successfully with correct size (no checksum validation)
        # Remove checksum to test only size validation
        del self.manager.manifest["files"]["test.gpr"]["checksum"]
        result = self.manager.validate_file("test.gpr")
        self.assertTrue(result)
        
        # Change expected size in manifest
        self.manager.manifest["files"]["test.gpr"]["size"] = 2000
        result = self.manager.validate_file("test.gpr")
        self.assertFalse(result)
    
    def test_validate_file_checksum(self):
        """Test file checksum validation."""
        # Calculate actual checksum for test file
        actual_checksum = self.manager._calculate_checksum(self.temp_dir / "test.gpr")
        
        # Update manifest with correct checksum
        self.manager.manifest["files"]["test.gpr"]["checksum"]["value"] = actual_checksum
        result = self.manager.validate_file("test.gpr")
        self.assertTrue(result)
        
        # Test with wrong checksum
        self.manager.manifest["files"]["test.gpr"]["checksum"]["value"] = "wrong_checksum"
        result = self.manager.validate_file("test.gpr")
        self.assertFalse(result)
    
    def test_list_files(self):
        """Test file listing functionality."""
        # List all files
        files = self.manager.list_files()
        self.assertEqual(files, ["test.gpr"])
        
        # List by type
        files = self.manager.list_files(file_type="gpr")
        self.assertEqual(files, ["test.gpr"])
        
        files = self.manager.list_files(file_type="dng")
        self.assertEqual(files, [])
        
        # List by use case
        files = self.manager.list_files(use_case="testing")
        self.assertEqual(files, ["test.gpr"])
        
        files = self.manager.list_files(use_case="conversion")
        self.assertEqual(files, [])
    
    def test_get_file_info(self):
        """Test getting file metadata."""
        info = self.manager.get_file_info("test.gpr")
        self.assertEqual(info["type"], "gpr")
        self.assertEqual(info["size"], 1000)
        
        with self.assertRaises(KeyError):
            self.manager.get_file_info("missing.gpr")
    
    def test_update_manifest(self):
        """Test manifest updating."""
        # Update manifest with current file info
        self.manager.update_manifest("test.gpr")
        
        # Check that manifest was updated
        file_info = self.manager.manifest["files"]["test.gpr"]
        self.assertEqual(file_info["size"], 1000)
        self.assertIsNotNone(file_info["checksum"]["value"])


class SyntheticDataGeneratorTests(unittest.TestCase):
    """Test the SyntheticDataGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(self._cleanup)
    
    def _cleanup(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_dummy_gpr_valid(self):
        """Test creating valid dummy GPR files."""
        output_path = self.temp_dir / "test.gpr"
        SyntheticDataGenerator.create_dummy_gpr(output_path, 640, 480, "valid")
        
        self.assertTrue(output_path.exists())
        self.assertGreater(output_path.stat().st_size, 0)
        
        # Check file starts with expected header
        with open(output_path, 'rb') as f:
            header = f.read(16)
            self.assertTrue(header.startswith(b"GPR\x00"))
    
    def test_create_dummy_gpr_corrupted(self):
        """Test creating corrupted dummy GPR files."""
        output_path = self.temp_dir / "corrupted.gpr"
        SyntheticDataGenerator.create_dummy_gpr(output_path, 640, 480, "corrupted")
        
        self.assertTrue(output_path.exists())
        self.assertGreater(output_path.stat().st_size, 0)
        
        # Check file starts with invalid header
        with open(output_path, 'rb') as f:
            header = f.read(16)
            self.assertFalse(header.startswith(b"GPR\x00"))
    
    def test_create_dummy_gpr_empty(self):
        """Test creating empty dummy GPR files."""
        output_path = self.temp_dir / "empty.gpr"
        SyntheticDataGenerator.create_dummy_gpr(output_path, 0, 0, "empty")
        
        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.stat().st_size, 0)
    
    def test_create_test_data_set(self):
        """Test creating a complete test data set."""
        created_files = SyntheticDataGenerator.create_test_data_set(self.temp_dir)
        
        # Check all expected files were created
        expected_files = ["small_test.gpr", "large_test.gpr", "corrupted_test.gpr", "empty_test.gpr"]
        self.assertEqual(set(created_files), set(expected_files))
        
        # Check all files exist
        for filename in created_files:
            file_path = self.temp_dir / filename
            self.assertTrue(file_path.exists())


class TestDataIntegrationTests(unittest.TestCase):
    """Test integration of test data management with the actual test suite."""
    
    def test_get_test_data_manager(self):
        """Test getting singleton test data manager."""
        manager1 = get_test_data_manager()
        manager2 = get_test_data_manager()
        
        # Should return TestDataRegistry instances
        self.assertIsInstance(manager1, TestDataRegistry)
        self.assertIsInstance(manager2, TestDataRegistry)
        
        # Should use same data directory
        self.assertEqual(manager1.data_dir, manager2.data_dir)
    
    def test_validate_all_test_data(self):
        """Test validating all test data."""
        results = validate_all_test_data()
        
        # Should return dict with validation results
        self.assertIsInstance(results, dict)
        
        # All files in manifest should have results
        manager = get_test_data_manager()
        try:
            manifest_files = set(manager.manifest.get("files", {}).keys())
            result_files = set(results.keys())
            self.assertEqual(manifest_files, result_files)
        except FileNotFoundError:
            # No manifest file - this is acceptable for new installations
            pass
    
    def test_ensure_test_data_available(self):
        """Test ensuring test data availability."""
        result = ensure_test_data_available()
        
        # Should return boolean
        self.assertIsInstance(result, bool)
        
        # If False, some test data is missing/invalid (this is acceptable)
        if not result:
            print("Note: Some test data is missing or invalid")


class TestDataPytestIntegrationTests(unittest.TestCase):
    """Test integration with pytest fixtures and markers."""
    
    def test_conftest_imports(self):
        """Test that conftest.py imports work correctly."""
        try:
            from . import conftest
            # If we get here, imports work
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"conftest.py imports failed: {e}")
    
    def test_synthetic_data_generation_consistency(self):
        """Test that synthetic data generation is consistent."""
        temp_dir1 = Path(tempfile.mkdtemp())
        temp_dir2 = Path(tempfile.mkdtemp())
        
        try:
            # Generate same file twice
            SyntheticDataGenerator.create_dummy_gpr(
                temp_dir1 / "test.gpr", 640, 480, "valid"
            )
            SyntheticDataGenerator.create_dummy_gpr(
                temp_dir2 / "test.gpr", 640, 480, "valid"
            )
            
            # Files should have same size
            size1 = (temp_dir1 / "test.gpr").stat().st_size
            size2 = (temp_dir2 / "test.gpr").stat().st_size
            self.assertEqual(size1, size2)
            
        finally:
            shutil.rmtree(temp_dir1)
            shutil.rmtree(temp_dir2)


if __name__ == '__main__':
    unittest.main()