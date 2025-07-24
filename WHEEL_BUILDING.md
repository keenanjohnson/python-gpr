# Wheel Building Setup

This document describes the automated wheel building setup for python-gpr.

## Overview

The project uses [cibuildwheel](https://cibuildwheel.readthedocs.io/) to automatically build binary wheels for multiple platforms:

- **Linux**: x86_64 (manylinux)
- **Windows**: x86_64 
- **macOS**: x86_64 and arm64 (Apple Silicon)

Wheels are built for Python 3.9, 3.10, 3.11, and 3.12.

## Automated Building

Wheels are automatically built on:

1. **Pushes to main branch**: For testing and validation
2. **Pull requests**: To ensure changes don't break wheel building
3. **Tagged releases** (v*): Wheels are built and automatically uploaded to PyPI
4. **Manual trigger**: Via GitHub Actions workflow_dispatch

## Configuration

The wheel building is configured in two places:

### pyproject.toml
Contains the cibuildwheel configuration:
- Build matrix (Python versions, platforms)
- Platform-specific build dependencies
- Test commands to validate wheels
- Environment variables for compilation

### .github/workflows/wheels.yml
GitHub Actions workflow that:
- Builds wheels on all platforms
- Creates source distribution
- Tests wheels on multiple platforms/Python versions
- Uploads to PyPI for tagged releases (using trusted publishing)

## Local Testing

To test wheel building locally:

```bash
# Install cibuildwheel
pip install cibuildwheel

# Build for current platform only
cibuildwheel --platform auto

# Test the built wheel
pip install wheelhouse/*.whl
python -c "import python_gpr; print('Test passed!')"
```

## PyPI Publishing

The project uses PyPI's trusted publishing feature for secure, keyless uploads:

- No API tokens needed in repository secrets
- Automatic uploads on tagged releases
- Controlled via GitHub environment protection rules

## Dependencies

The wheels include all necessary compiled dependencies:
- GPR library (built from source via git submodule)
- pybind11 bindings
- Platform-specific runtime libraries

## Troubleshooting

Common issues and solutions:

1. **Build failures**: Check platform-specific build dependencies in pyproject.toml
2. **Import errors**: Ensure test commands in cibuildwheel configuration are correct
3. **Missing symbols**: Verify that all required libraries are being linked properly

## Security

- Wheels are built in isolated environments
- Source code integrity via git submodules with pinned commits
- Trusted publishing eliminates need for stored credentials
- All builds are logged and auditable via GitHub Actions