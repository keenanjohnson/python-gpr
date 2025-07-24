"""
Test data management utilities for python-gpr test suite.

This module provides utilities for managing test data including:
- Test data discovery and validation
- Synthetic test data generation
- Test data integrity checking
- Version management
"""

import json
import hashlib
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import struct
import datetime


class TestDataRegistry:
    """Manages test data for the python-gpr test suite.
    
    Note: This is not a pytest test class despite the name starting with 'Test'.
    """
    # This class is not a pytest test class
    __test__ = False
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the test data manager.
        
        Args:
            data_dir: Path to the test data directory. If None, uses default.
        """
        if data_dir is None:
            # Default to tests/data relative to this file
            self.data_dir = Path(__file__).parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.manifest_path = self.data_dir / "manifest.json"
        self._manifest = None
    
    @property
    def manifest(self) -> Dict[str, Any]:
        """Get the test data manifest."""
        if self._manifest is None:
            self._load_manifest()
        return self._manifest
    
    def _load_manifest(self):
        """Load the test data manifest from disk."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Test data manifest not found: {self.manifest_path}")
        
        with open(self.manifest_path, 'r') as f:
            self._manifest = json.load(f)
    
    def get_file_path(self, filename: str) -> Path:
        """Get the full path to a test data file.
        
        Args:
            filename: Name of the test data file
            
        Returns:
            Path to the test data file
            
        Raises:
            FileNotFoundError: If the file is not found
        """
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Test data file not found: {file_path}")
        return file_path
    
    def validate_file(self, filename: str) -> bool:
        """Validate a test data file against its manifest entry.
        
        Args:
            filename: Name of the test data file to validate
            
        Returns:
            True if file is valid, False otherwise
        """
        if filename not in self.manifest.get("files", {}):
            return False
        
        file_info = self.manifest["files"][filename]
        file_path = self.get_file_path(filename)
        
        # Check file size
        expected_size = file_info.get("size")
        if expected_size is not None:
            actual_size = file_path.stat().st_size
            if actual_size != expected_size:
                return False
        
        # Check checksum if available and not null/placeholder
        checksum_info = file_info.get("checksum", {})
        expected_checksum = checksum_info.get("value")
        if expected_checksum and expected_checksum not in [None, "null", ""]:
            algorithm = checksum_info.get("algorithm", "sha256")
            actual_checksum = self._calculate_checksum(file_path, algorithm)
            if actual_checksum != expected_checksum:
                return False
        
        return True
    
    def _calculate_checksum(self, file_path: Path, algorithm: str = "sha256") -> str:
        """Calculate checksum for a file.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use
            
        Returns:
            Hexadecimal checksum string
        """
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    def update_manifest(self, filename: str):
        """Update manifest entry for a file with current metadata.
        
        Args:
            filename: Name of the file to update in manifest
        """
        file_path = self.get_file_path(filename)
        
        # Calculate current metadata
        size = file_path.stat().st_size
        checksum = self._calculate_checksum(file_path)
        
        # Update manifest
        if "files" not in self.manifest:
            self.manifest["files"] = {}
        
        if filename not in self.manifest["files"]:
            self.manifest["files"][filename] = {}
        
        self.manifest["files"][filename].update({
            "size": size,
            "checksum": {
                "algorithm": "sha256",
                "value": checksum
            }
        })
        
        # Save manifest
        self._save_manifest()
    
    def _save_manifest(self):
        """Save the manifest to disk."""
        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def list_files(self, file_type: Optional[str] = None, 
                   use_case: Optional[str] = None) -> List[str]:
        """List available test data files.
        
        Args:
            file_type: Filter by file type (e.g., 'gpr', 'dng')
            use_case: Filter by use case (e.g., 'conversion_testing')
            
        Returns:
            List of matching file names
        """
        files = []
        
        for filename, file_info in self.manifest.get("files", {}).items():
            # Apply type filter
            if file_type and file_info.get("type") != file_type:
                continue
            
            # Apply use case filter
            if use_case:
                use_cases = file_info.get("use_cases", [])
                if use_case not in use_cases:
                    continue
            
            files.append(filename)
        
        return files
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """Get metadata for a test data file.
        
        Args:
            filename: Name of the test data file
            
        Returns:
            Dictionary containing file metadata
            
        Raises:
            KeyError: If file is not in manifest
        """
        if filename not in self.manifest.get("files", {}):
            raise KeyError(f"File not found in manifest: {filename}")
        
        return self.manifest["files"][filename].copy()


class SyntheticDataGenerator:
    """Generates synthetic test data for various testing scenarios."""
    
    @staticmethod
    def create_dummy_gpr(output_path: Path, width: int = 1920, height: int = 1080,
                        content_type: str = "valid") -> None:
        """Create a dummy GPR file for testing.
        
        Args:
            output_path: Where to save the dummy file
            width: Image width
            height: Image height
            content_type: Type of content ('valid', 'corrupted', 'empty')
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if content_type == "empty":
            # Create empty file
            output_path.touch()
        elif content_type == "corrupted":
            # Create file with invalid header
            with open(output_path, 'wb') as f:
                f.write(b"INVALID_GPR_HEADER" + b"\x00" * 1000)
        else:
            # Create file with basic GPR-like structure
            with open(output_path, 'wb') as f:
                # Write a basic header-like structure
                f.write(b"GPR\x00")  # Magic bytes
                f.write(struct.pack('<I', width))  # Width (little endian)
                f.write(struct.pack('<I', height))  # Height (little endian)
                f.write(struct.pack('<I', 1))  # Version
                f.write(struct.pack('<I', 0))  # Flags
                
                # Write dummy image data
                pixel_count = width * height
                dummy_data = bytes([i % 256 for i in range(min(pixel_count, 1024))])
                # Repeat pattern to fill image
                full_data = (dummy_data * ((pixel_count // len(dummy_data)) + 1))[:pixel_count]
                f.write(full_data)
    
    @staticmethod
    def create_test_data_set(output_dir: Path) -> List[str]:
        """Create a comprehensive set of synthetic test data.
        
        Args:
            output_dir: Directory to create test files in
            
        Returns:
            List of created file names
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        created_files = []
        
        # Small valid GPR file
        small_gpr = output_dir / "small_test.gpr"
        SyntheticDataGenerator.create_dummy_gpr(small_gpr, 640, 480, "valid")
        created_files.append(small_gpr.name)
        
        # Large valid GPR file
        large_gpr = output_dir / "large_test.gpr"
        SyntheticDataGenerator.create_dummy_gpr(large_gpr, 4096, 3072, "valid")
        created_files.append(large_gpr.name)
        
        # Corrupted GPR file
        corrupted_gpr = output_dir / "corrupted_test.gpr"
        SyntheticDataGenerator.create_dummy_gpr(corrupted_gpr, 1920, 1080, "corrupted")
        created_files.append(corrupted_gpr.name)
        
        # Empty GPR file
        empty_gpr = output_dir / "empty_test.gpr"
        SyntheticDataGenerator.create_dummy_gpr(empty_gpr, 0, 0, "empty")
        created_files.append(empty_gpr.name)
        
        return created_files


def get_test_data_manager() -> TestDataRegistry:
    """Get a singleton test data manager instance."""
    return TestDataRegistry()


def validate_all_test_data() -> Dict[str, bool]:
    """Validate all test data files.
    
    Returns:
        Dictionary mapping file names to validation results
    """
    manager = get_test_data_manager()
    results = {}
    
    for filename in manager.manifest.get("files", {}):
        try:
            results[filename] = manager.validate_file(filename)
        except FileNotFoundError:
            results[filename] = False
    
    return results


def ensure_test_data_available() -> bool:
    """Ensure all required test data is available and valid.
    
    Returns:
        True if all test data is available and valid
    """
    validation_results = validate_all_test_data()
    return all(validation_results.values())