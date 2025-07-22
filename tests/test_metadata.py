"""
Tests for project metadata and configuration.

This test validates that the pyproject.toml follows PEP 518/621 standards
and that all required metadata is properly defined.
"""

import pytest
import toml
from pathlib import Path


def test_pyproject_toml_exists():
    """Test that pyproject.toml exists in project root."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml not found"


def test_pyproject_toml_valid():
    """Test that pyproject.toml is valid TOML."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    try:
        data = toml.load(pyproject_path)
        assert isinstance(data, dict), "pyproject.toml should parse to a dictionary"
    except Exception as e:
        pytest.fail(f"pyproject.toml is not valid TOML: {e}")


def test_pep518_build_system():
    """Test PEP 518 build system compliance."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    data = toml.load(pyproject_path)
    
    assert "build-system" in data, "build-system section missing"
    build_system = data["build-system"]
    
    assert "requires" in build_system, "build-system.requires missing"
    assert "build-backend" in build_system, "build-system.build-backend missing"
    
    assert isinstance(build_system["requires"], list), "build-system.requires should be a list"
    assert len(build_system["requires"]) > 0, "build-system.requires should not be empty"
    
    assert build_system["build-backend"] == "scikit_build_core.build", "Expected scikit-build-core backend"


def test_pep621_project_metadata():
    """Test PEP 621 project metadata compliance."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    data = toml.load(pyproject_path)
    
    assert "project" in data, "project section missing"
    project = data["project"]
    
    # Required fields
    required_fields = ["name", "description", "requires-python"]
    for field in required_fields:
        assert field in project, f"project.{field} is required"
        assert project[field], f"project.{field} should not be empty"
    
    # Version handling (either static or dynamic)
    assert ("version" in project) or ("dynamic" in project and "version" in project["dynamic"]), \
           "project.version must be specified either statically or dynamically"
    
    # Authors
    assert "authors" in project, "project.authors is required"
    assert isinstance(project["authors"], list), "project.authors should be a list"
    assert len(project["authors"]) > 0, "project.authors should not be empty"
    
    for author in project["authors"]:
        assert "name" in author, "Each author should have a name"
        assert author["name"], "Author name should not be empty"


def test_project_name():
    """Test project name is correct."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    data = toml.load(pyproject_path)
    
    assert data["project"]["name"] == "python-gpr", "Project name should be 'python-gpr'"


def test_dependencies():
    """Test that dependencies are properly specified."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    data = toml.load(pyproject_path)
    
    project = data["project"]
    
    # Main dependencies
    assert "dependencies" in project, "project.dependencies should be specified"
    assert isinstance(project["dependencies"], list), "project.dependencies should be a list"
    
    # Should have numpy as a dependency
    numpy_deps = [dep for dep in project["dependencies"] if dep.startswith("numpy")]
    assert len(numpy_deps) > 0, "numpy should be a dependency"


def test_optional_dependencies():
    """Test optional dependencies configuration."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    data = toml.load(pyproject_path)
    
    project = data["project"]
    
    assert "optional-dependencies" in project, "optional-dependencies should be specified"
    optional_deps = project["optional-dependencies"]
    
    # Should have dev dependencies
    assert "dev" in optional_deps, "dev optional dependencies should be specified"
    dev_deps = optional_deps["dev"]
    assert isinstance(dev_deps, list), "dev dependencies should be a list"
    assert len(dev_deps) > 0, "dev dependencies should not be empty"
    
    # Check for common dev tools
    dev_tools = ["pytest", "black", "flake8", "mypy"]
    for tool in dev_tools:
        tool_found = any(dep.startswith(tool) for dep in dev_deps)
        assert tool_found, f"{tool} should be in dev dependencies"


def test_scikit_build_configuration():
    """Test scikit-build configuration."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    data = toml.load(pyproject_path)
    
    assert "tool" in data, "tool section missing"
    assert "scikit-build" in data["tool"], "tool.scikit-build section missing"
    
    skb = data["tool"]["scikit-build"]
    
    assert "minimum-version" in skb, "scikit-build minimum-version should be specified"
    
    # Check cmake configuration if present
    if "cmake" in skb:
        cmake = skb["cmake"]
        if "args" in cmake:
            assert isinstance(cmake["args"], list), "cmake.args should be a list"


def test_python_version_requirement():
    """Test Python version requirement."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    data = toml.load(pyproject_path)
    
    requires_python = data["project"]["requires-python"]
    assert "3.8" in requires_python, "Should support Python 3.8+"


def test_project_urls():
    """Test project URLs are specified."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    data = toml.load(pyproject_path)
    
    project = data["project"]
    
    if "urls" in project:
        urls = project["urls"]
        # Check for common URLs
        expected_urls = ["Homepage", "Repository", "Issues"]
        for url_type in expected_urls:
            if url_type in urls:
                assert urls[url_type], f"{url_type} URL should not be empty"
                assert urls[url_type].startswith("http"), f"{url_type} URL should be a valid URL"


def test_classifiers():
    """Test project classifiers."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    data = toml.load(pyproject_path)
    
    project = data["project"]
    
    if "classifiers" in project:
        classifiers = project["classifiers"]
        assert isinstance(classifiers, list), "classifiers should be a list"
        
        # Should have development status
        dev_status_found = any("Development Status" in c for c in classifiers)
        assert dev_status_found, "Should have Development Status classifier"
        
        # Should have license classifier
        license_found = any("License ::" in c for c in classifiers)
        assert license_found, "Should have License classifier"
        
        # Should have Python version classifiers
        python_found = any("Programming Language :: Python ::" in c for c in classifiers)
        assert python_found, "Should have Python version classifiers"