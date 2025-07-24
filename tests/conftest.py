"""
Pytest configuration and fixtures for python-gpr test suite.

This module provides pytest fixtures for test data management and common
test utilities. When pytest is not available, this module can still be
imported without errors.
"""

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Create dummy pytest object to prevent import errors
    class DummyPytest:
        def fixture(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    pytest = DummyPytest()

import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any

try:
    from .test_data import (
        TestDataRegistry, 
        SyntheticDataGenerator, 
        get_test_data_manager,
        validate_all_test_data
    )
except ImportError:
    # Handle case when running with unittest discovery
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from test_data import (
        TestDataRegistry, 
        SyntheticDataGenerator, 
        get_test_data_manager,
        validate_all_test_data
    )


@pytest.fixture(scope="session")
def test_data_manager() -> TestDataRegistry:
    """Provide a test data manager instance for the test session."""
    return get_test_data_manager()


@pytest.fixture(scope="session")
def validate_test_data(test_data_manager: TestDataRegistry) -> Dict[str, bool]:
    """Validate all test data at the start of the test session."""
    return validate_all_test_data()


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_gpr_file(test_data_manager: TestDataRegistry) -> Path:
    """Provide path to a real sample GPR file."""
    gpr_files = test_data_manager.list_files(file_type="gpr")
    if not gpr_files:
        pytest.skip("No GPR test files available")
    
    # Use the first available GPR file
    return test_data_manager.get_file_path(gpr_files[0])


@pytest.fixture
def synthetic_test_data(temp_dir: Path) -> Dict[str, Path]:
    """Provide synthetic test data files."""
    created_files = SyntheticDataGenerator.create_test_data_set(temp_dir)
    
    # Return dictionary mapping names to paths
    return {
        "small_gpr": temp_dir / "small_test.gpr",
        "large_gpr": temp_dir / "large_test.gpr", 
        "corrupted_gpr": temp_dir / "corrupted_test.gpr",
        "empty_gpr": temp_dir / "empty_test.gpr"
    }


@pytest.fixture
def small_synthetic_gpr(temp_dir: Path) -> Path:
    """Provide a small synthetic GPR file for basic testing."""
    gpr_path = temp_dir / "small_test.gpr"
    SyntheticDataGenerator.create_dummy_gpr(gpr_path, 640, 480, "valid")
    return gpr_path


@pytest.fixture
def large_synthetic_gpr(temp_dir: Path) -> Path:
    """Provide a large synthetic GPR file for stress testing."""
    gpr_path = temp_dir / "large_test.gpr"
    SyntheticDataGenerator.create_dummy_gpr(gpr_path, 4096, 3072, "valid")
    return gpr_path


@pytest.fixture
def corrupted_gpr(temp_dir: Path) -> Path:
    """Provide a corrupted GPR file for error handling testing."""
    gpr_path = temp_dir / "corrupted_test.gpr"
    SyntheticDataGenerator.create_dummy_gpr(gpr_path, 1920, 1080, "corrupted")
    return gpr_path


@pytest.fixture
def empty_gpr(temp_dir: Path) -> Path:
    """Provide an empty GPR file for edge case testing."""
    gpr_path = temp_dir / "empty_test.gpr"
    SyntheticDataGenerator.create_dummy_gpr(gpr_path, 0, 0, "empty")
    return gpr_path


@pytest.fixture(scope="session", autouse=True)
def check_test_data_integrity(test_data_manager: TestDataRegistry):
    """Automatically check test data integrity at session start."""
    validation_results = validate_all_test_data()
    
    # Report any validation failures but don't fail the tests
    # This allows tests to run even with missing/invalid data
    for filename, is_valid in validation_results.items():
        if not is_valid:
            print(f"Warning: Test data file '{filename}' failed validation")


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "requires_real_data: mark test as requiring real GPR test data"
    )
    config.addinivalue_line(
        "markers", "requires_synthetic_data: mark test as requiring synthetic test data"
    )
    config.addinivalue_line(
        "markers", "stress_test: mark test as a stress/performance test"
    )
    config.addinivalue_line(
        "markers", "edge_case: mark test as testing edge cases"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle test data requirements."""
    # Check if real test data is available
    try:
        manager = get_test_data_manager()
        real_data_available = bool(manager.list_files(file_type="gpr"))
    except (FileNotFoundError, KeyError):
        real_data_available = False
    
    # Skip tests that require real data if not available
    skip_real_data = pytest.mark.skip(reason="Real GPR test data not available")
    
    for item in items:
        if "requires_real_data" in item.keywords and not real_data_available:
            item.add_marker(skip_real_data)