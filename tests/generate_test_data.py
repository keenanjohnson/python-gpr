#!/usr/bin/env python3
"""
Generate additional test data for the python-gpr test suite.

This script creates various types of synthetic test data files
to provide comprehensive test coverage.
"""

import argparse
import json
from pathlib import Path
import datetime

from test_data import TestDataRegistry, SyntheticDataGenerator


def create_comprehensive_test_data(data_dir: Path, update_manifest: bool = True):
    """Create a comprehensive set of test data files.
    
    Args:
        data_dir: Directory to create test files in
        update_manifest: Whether to update the manifest file
    """
    print(f"Creating test data in: {data_dir}")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create various sizes of synthetic GPR files
    test_files = [
        # Small files for quick tests
        ("tiny_64x48.gpr", 64, 48, "valid", "Tiny GPR file for minimal testing"),
        ("small_320x240.gpr", 320, 240, "valid", "Small GPR file for basic testing"),
        ("medium_640x480.gpr", 640, 480, "valid", "Medium GPR file for standard testing"),
        
        # Standard resolution files
        ("hd_1280x720.gpr", 1280, 720, "valid", "HD resolution GPR file"),
        ("fullhd_1920x1080.gpr", 1920, 1080, "valid", "Full HD GPR file"),
        
        # High resolution files for stress testing
        ("4k_3840x2160.gpr", 3840, 2160, "valid", "4K resolution GPR file"),
        
        # Edge case files
        ("wide_2560x720.gpr", 2560, 720, "valid", "Ultra-wide aspect ratio GPR file"),
        ("tall_720x2560.gpr", 720, 2560, "valid", "Tall aspect ratio GPR file"),
        ("square_1024x1024.gpr", 1024, 1024, "valid", "Square aspect ratio GPR file"),
        
        # Error condition files
        ("corrupted_header.gpr", 1920, 1080, "corrupted", "GPR file with corrupted header"),
        ("empty_file.gpr", 0, 0, "empty", "Empty GPR file"),
        ("truncated_file.gpr", 1920, 1080, "valid", "GPR file that will be truncated"),
    ]
    
    created_files = []
    
    for filename, width, height, content_type, description in test_files:
        file_path = data_dir / filename
        print(f"Creating {filename} ({width}x{height}, {content_type})")
        
        SyntheticDataGenerator.create_dummy_gpr(file_path, width, height, content_type)
        
        # Truncate the truncated file to simulate incomplete download
        if "truncated" in filename:
            original_size = file_path.stat().st_size
            truncated_size = original_size // 2
            with open(file_path, 'r+b') as f:
                f.truncate(truncated_size)
            print(f"  Truncated {filename} from {original_size} to {truncated_size} bytes")
        
        created_files.append({
            "filename": filename,
            "width": width,
            "height": height,
            "type": content_type,
            "description": description,
            "size": file_path.stat().st_size,
            "use_cases": get_use_cases_for_file(filename, content_type)
        })
    
    if update_manifest:
        update_test_data_manifest(data_dir, created_files)
    
    print(f"\nCreated {len(created_files)} test data files")
    return created_files


def get_use_cases_for_file(filename: str, content_type: str) -> list:
    """Determine appropriate use cases for a test file."""
    use_cases = []
    
    if content_type == "valid":
        use_cases.append("conversion_testing")
        use_cases.append("format_detection")
        
        if "tiny" in filename or "small" in filename:
            use_cases.append("unit_testing")
            use_cases.append("performance_testing")
        elif "4k" in filename or "3840" in filename:
            use_cases.append("stress_testing")
            use_cases.append("memory_testing")
        elif "wide" in filename or "tall" in filename or "square" in filename:
            use_cases.append("aspect_ratio_testing")
        else:
            use_cases.append("integration_testing")
    
    elif content_type == "corrupted":
        use_cases.extend(["error_handling", "robustness_testing"])
    elif content_type == "empty":
        use_cases.extend(["edge_case_testing", "error_handling"])
    
    if "truncated" in filename:
        use_cases.extend(["incomplete_data_testing", "error_handling"])
    
    return use_cases


def update_test_data_manifest(data_dir: Path, new_files: list):
    """Update the test data manifest with new files."""
    manifest_path = data_dir / "manifest.json"
    
    # Load existing manifest or create new one
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    else:
        manifest = {
            "version": "1.0.0",
            "description": "Test data manifest for python-gpr test suite",
            "files": {},
            "synthetic_data": {},
            "expected_outputs": {}
        }
    
    # Update with new files
    for file_info in new_files:
        filename = file_info["filename"]
        
        # Calculate checksum
        registry = TestDataRegistry(data_dir)
        checksum = registry._calculate_checksum(data_dir / filename)
        
        manifest["files"][filename] = {
            "type": "synthetic_gpr" if file_info["type"] in ["valid", "corrupted", "empty"] else "gpr",
            "size": file_info["size"],
            "description": file_info["description"],
            "source": "synthetic",
            "width": file_info["width"] if file_info["width"] > 0 else None,
            "height": file_info["height"] if file_info["height"] > 0 else None,
            "checksum": {
                "algorithm": "sha256",
                "value": checksum
            },
            "use_cases": file_info["use_cases"]
        }
    
    # Update manifest metadata
    manifest["generated"] = datetime.datetime.now().isoformat() + "Z"
    
    # Save manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Updated manifest at {manifest_path}")


def validate_existing_data(data_dir: Path):
    """Validate all existing test data."""
    registry = TestDataRegistry(data_dir)
    
    try:
        validation_results = {}
        for filename in registry.manifest.get("files", {}):
            try:
                is_valid = registry.validate_file(filename)
                validation_results[filename] = is_valid
                status = "✓" if is_valid else "✗"
                print(f"{status} {filename}")
            except FileNotFoundError:
                validation_results[filename] = False
                print(f"✗ {filename} (not found)")
        
        valid_count = sum(validation_results.values())
        total_count = len(validation_results)
        print(f"\nValidation summary: {valid_count}/{total_count} files valid")
        
        return validation_results
        
    except FileNotFoundError:
        print("No manifest found - no files to validate")
        return {}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate test data for python-gpr")
    parser.add_argument(
        "--data-dir", 
        type=Path,
        default=Path(__file__).parent / "data",
        help="Directory to create test data in"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate existing data, don't create new files"
    )
    parser.add_argument(
        "--no-manifest",
        action="store_true",
        help="Don't update the manifest file"
    )
    
    args = parser.parse_args()
    
    if args.validate_only:
        print("Validating existing test data...")
        validate_existing_data(args.data_dir)
    else:
        print("Creating comprehensive test data...")
        create_comprehensive_test_data(args.data_dir, not args.no_manifest)
        
        print("\nValidating created test data...")
        validate_existing_data(args.data_dir)


if __name__ == "__main__":
    main()