# Building the pybind11 Binding

This document describes how to build and test the minimal pybind11 binding for python-gpr.

## Prerequisites

- CMake 3.15 or later
- C++11 compatible compiler
- Python 3.8 or later
- pybind11 (install with `pip install pybind11`)

## Building

1. Initialize the git submodule (if not already done):
   ```bash
   git submodule update --init --recursive
   ```

2. Create and enter build directory:
   ```bash
   mkdir build
   cd build
   ```

3. Configure with CMake:
   ```bash
   cmake ..
   ```

4. Build the project:
   ```bash
   make
   ```

This will create a `_core.cpython-*.so` file in the build directory.

## Testing the Binding

### Direct Testing

From the build directory:
```bash
python3 -c "
import sys
sys.path.insert(0, '.')
import _core
print('hello_world():', _core.hello_world())
print('add(5, 3):', _core.add(5, 3))
print('greet(\"World\"):', _core.greet('World'))
"
```

### Using with Python Package

Copy the compiled module to the source directory:
```bash
cp _core*.so ../src/python_gpr/
```

Then test from the project root:
```bash
cd ..
python3 -c "
import sys
sys.path.insert(0, 'src')
import python_gpr
print('hello_world():', python_gpr.hello_world())
print('add(2, 3):', python_gpr.add(2, 3))
print('greet(\"pybind11\"):', python_gpr.greet('pybind11'))
"
```

### Running Unit Tests

Run all tests including the new pybind11 binding tests:
```bash
python -m unittest discover tests/ -v
```

Run only the pybind11 binding tests:
```bash
python -m unittest tests.test_pybind11_binding -v
```

## What's Implemented

The minimal pybind11 binding includes:

- **hello_world()**: Returns a simple "Hello World from pybind11!" string
- **add(a, b)**: Adds two integers and returns the result
- **greet(name)**: Takes a string name and returns "Hello, {name}!"
- **__version__**: Module version attribute

## CMake Build System Features

The CMake configuration includes:

- **Auto-detection of pybind11**: Tries multiple methods to find pybind11
- **Fallback manual setup**: If pybind11 can't be found via find_package, it attempts manual configuration
- **Cross-platform compatibility**: Works on Windows, macOS, and Linux
- **Minimal dependencies**: No complex GPR library dependencies for the basic binding

## Integration with Existing Code

The binding integrates with the existing python-gpr package structure:

- The `_core` module is imported in `src/python_gpr/__init__.py`
- Functions are made available in the `python_gpr` namespace via `from ._core import *`
- Existing tests continue to work unchanged
- New tests specifically verify the pybind11 functionality

This provides a foundation for future GPR library bindings while proving that the build system and pybind11 integration work correctly.