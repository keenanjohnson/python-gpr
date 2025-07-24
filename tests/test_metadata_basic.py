"""
Basic tests for project metadata and configuration.

This test validates that the pyproject.toml exists and contains basic required
information using only Python standard library (no external dependencies).
"""

import unittest
import os
from pathlib import Path


class TestProjectMetadata(unittest.TestCase):
    """Test basic project metadata without external dependencies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        
    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists in project root."""
        self.assertTrue(self.pyproject_path.exists(), "pyproject.toml not found")
        
    def test_pyproject_toml_readable(self):
        """Test that pyproject.toml is readable."""
        with open(self.pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertGreater(len(content), 0, "pyproject.toml should not be empty")
        
    def test_pyproject_contains_project_section(self):
        """Test that pyproject.toml contains [project] section."""
        with open(self.pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("[project]", content, "pyproject.toml should contain [project] section")
        
    def test_pyproject_contains_build_system(self):
        """Test that pyproject.toml contains [build-system] section."""
        with open(self.pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("[build-system]", content, "pyproject.toml should contain [build-system] section")
        
    def test_pyproject_contains_project_name(self):
        """Test that pyproject.toml contains project name."""
        with open(self.pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('name = "python-gpr"', content, "pyproject.toml should contain project name")
        
    def test_pyproject_contains_description(self):
        """Test that pyproject.toml contains description."""
        with open(self.pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("description =", content, "pyproject.toml should contain description")
        
    def test_pyproject_contains_python_version(self):
        """Test that pyproject.toml contains Python version requirement."""
        with open(self.pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("requires-python =", content, "pyproject.toml should contain Python version requirement")
        self.assertIn("3.9", content, "pyproject.toml should support Python 3.9+")
        
    def test_pyproject_contains_dependencies(self):
        """Test that pyproject.toml contains dependencies section."""
        with open(self.pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("dependencies =", content, "pyproject.toml should contain dependencies")
        
    def test_pyproject_contains_build_backend(self):
        """Test that pyproject.toml contains build backend."""
        with open(self.pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("build-backend =", content, "pyproject.toml should contain build backend")
        self.assertIn("scikit_build_core", content, "should use scikit-build-core backend")


class TestProjectStructure(unittest.TestCase):
    """Test basic project structure."""
    
    def test_src_directory_exists(self):
        """Test that src directory exists."""
        src_path = Path(__file__).parent.parent / "src"
        self.assertTrue(src_path.exists(), "src directory should exist")
        self.assertTrue(src_path.is_dir(), "src should be a directory")
        
    def test_python_gpr_package_exists(self):
        """Test that python_gpr package exists."""
        package_path = Path(__file__).parent.parent / "src" / "python_gpr"
        self.assertTrue(package_path.exists(), "python_gpr package should exist")
        self.assertTrue(package_path.is_dir(), "python_gpr should be a directory")
        
    def test_package_init_exists(self):
        """Test that package __init__.py exists."""
        init_path = Path(__file__).parent.parent / "src" / "python_gpr" / "__init__.py"
        self.assertTrue(init_path.exists(), "__init__.py should exist in package")
        
    def test_tests_directory_exists(self):
        """Test that tests directory exists."""
        tests_path = Path(__file__).parent
        self.assertTrue(tests_path.exists(), "tests directory should exist")
        self.assertTrue(tests_path.is_dir(), "tests should be a directory")
        
    def test_readme_exists(self):
        """Test that README.md exists."""
        readme_path = Path(__file__).parent.parent / "README.md"
        self.assertTrue(readme_path.exists(), "README.md should exist")


if __name__ == '__main__':
    unittest.main()