#!/usr/bin/env python3
"""
Demonstration of the high-level Python wrapper API for python-gpr.

This script showcases the enhanced GPRImage class with context manager support
and convenience functions for common operations.
"""

import os
import tempfile
import sys

# Add the src directory to the path for demo purposes
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_context_manager():
    """Demonstrate context manager usage for automatic resource cleanup."""
    print("=== Context Manager Demo ===")
    
    # Create a temporary dummy GPR file for demonstration
    with tempfile.NamedTemporaryFile(suffix='.gpr', delete=False) as tmp:
        tmp.write(b"dummy gpr content for demo")
        temp_gpr = tmp.name
    
    try:
        # Import the high-level API
        from python_gpr.core import GPRImage, open_gpr
        
        print("1. Using GPRImage as context manager:")
        with GPRImage(temp_gpr) as img:
            print(f"   - File path: {img.filepath}")
            print(f"   - Is closed: {img.is_closed}")
            print(f"   - Representation: {repr(img)}")
            
            # Try to access properties (will raise NotImplementedError since bindings aren't built)
            try:
                print(f"   - Dimensions: {img.width}x{img.height}")
            except NotImplementedError:
                print("   - Dimensions: [Available when C++ bindings are built]")
        
        print(f"   - Image closed after context: {img.is_closed}")
        
        print("\n2. Using open_gpr convenience function:")
        with open_gpr(temp_gpr) as img:
            print(f"   - Opened with convenience function: {type(img).__name__}")
            print(f"   - Same functionality as GPRImage")
            
    finally:
        # Clean up
        if os.path.exists(temp_gpr):
            os.unlink(temp_gpr)


def demo_conversion_api():
    """Demonstrate the enhanced conversion API."""
    print("\n=== Conversion API Demo ===")
    
    # Create temporary files for demonstration
    with tempfile.NamedTemporaryFile(suffix='.gpr', delete=False) as tmp:
        tmp.write(b"dummy gpr content")
        temp_gpr = tmp.name
    
    try:
        from python_gpr.core import GPRImage, convert_image
        
        print("1. Object-oriented conversion methods:")
        with GPRImage(temp_gpr) as img:
            try:
                # These will raise NotImplementedError until C++ bindings are available
                print("   - img.convert_to_dng('output.dng')  # Enhanced method name")
                img.convert_to_dng('output.dng')
            except NotImplementedError:
                print("   - [Available when C++ bindings are built]")
            
            try:
                print("   - img.to_raw('output.raw')  # Convenient alias")
                img.to_raw('output.raw')
            except NotImplementedError:
                print("   - [Available when C++ bindings are built]")
        
        print("\n2. Functional conversion API:")
        try:
            print("   - convert_image('input.gpr', 'output.dng')  # Auto-detects formats")
            convert_image(temp_gpr, 'output.dng')
        except NotImplementedError:
            print("   - [Available when C++ bindings are built]")
            
        print("   - convert_image('input.dng', 'output.gpr', target_format='gpr')  # Explicit format")
        
    finally:
        if os.path.exists(temp_gpr):
            os.unlink(temp_gpr)


def demo_pythonic_api():
    """Demonstrate Python naming conventions and best practices."""
    print("\n=== Pythonic API Design Demo ===")
    
    with tempfile.NamedTemporaryFile(suffix='.gpr', delete=False) as tmp:
        tmp.write(b"dummy gpr content")
        temp_gpr = tmp.name
    
    try:
        from python_gpr.core import GPRImage, get_info, get_gpr_info
        
        print("1. Method and function names follow Python conventions:")
        print("   - snake_case for functions: get_info(), convert_image(), load_gpr_as_numpy()")
        print("   - snake_case for methods: to_numpy(), get_image_info(), convert_to_dng()")
        print("   - CamelCase for classes: GPRImage, GPRParameters")
        
        print("\n2. Intuitive method names with both explicit and convenient forms:")
        with GPRImage(temp_gpr) as img:
            print("   - img.convert_to_dng()  # Explicit, descriptive")
            print("   - img.to_dng()         # Convenient, shorter alias")
            print("   - img.convert_to_raw() # Explicit, descriptive")
            print("   - img.to_raw()        # Convenient, shorter alias")
        
        print("\n3. Convenience functions for common operations:")
        try:
            print("   - info = get_info('image.gpr')  # New, consistent naming")
            info = get_info(temp_gpr)
        except NotImplementedError:
            print("   - [Available when C++ bindings are built]")
            
        try:
            print("   - info = get_gpr_info('image.gpr')  # Legacy, delegates to get_info()")
            info = get_gpr_info(temp_gpr)
        except NotImplementedError:
            print("   - [Available when C++ bindings are built]")
            
    finally:
        if os.path.exists(temp_gpr):
            os.unlink(temp_gpr)


def demo_resource_management():
    """Demonstrate automatic resource management features."""
    print("\n=== Resource Management Demo ===")
    
    with tempfile.NamedTemporaryFile(suffix='.gpr', delete=False) as tmp:
        tmp.write(b"dummy gpr content")
        temp_gpr = tmp.name
    
    try:
        from python_gpr.core import GPRImage
        
        print("1. Manual resource management:")
        img = GPRImage(temp_gpr)
        print(f"   - Image created: {img.is_closed}")
        img.close()
        print(f"   - Image manually closed: {img.is_closed}")
        
        print("\n2. Automatic resource management with context manager:")
        with GPRImage(temp_gpr) as img:
            print(f"   - Inside context: {img.is_closed}")
        print(f"   - After context: {img.is_closed}")
        
        print("\n3. Exception safety:")
        try:
            with GPRImage(temp_gpr) as img:
                print(f"   - Before exception: {img.is_closed}")
                raise ValueError("Demo exception")
        except ValueError:
            print(f"   - After exception: {img.is_closed} (still closed properly)")
        
        print("\n4. Operations on closed images are prevented:")
        closed_img = GPRImage(temp_gpr)
        closed_img.close()
        try:
            _ = closed_img.width  # This will raise ValueError
        except ValueError as e:
            print(f"   - Accessing closed image: {e}")
            
    finally:
        if os.path.exists(temp_gpr):
            os.unlink(temp_gpr)


def demo_numpy_integration():
    """Demonstrate NumPy integration features."""
    print("\n=== NumPy Integration Demo ===")
    
    with tempfile.NamedTemporaryFile(suffix='.gpr', delete=False) as tmp:
        tmp.write(b"dummy gpr content")
        temp_gpr = tmp.name
    
    try:
        from python_gpr.core import GPRImage, load_gpr_as_numpy
        
        print("1. Object-oriented NumPy access:")
        with GPRImage(temp_gpr) as img:
            try:
                print("   - raw_data = img.to_numpy(dtype='uint16')  # Raw 16-bit data")
                print("   - float_data = img.to_numpy(dtype='float32')  # Normalized 0-1 range")
                raw_data = img.to_numpy(dtype='uint16')
            except NotImplementedError:
                print("   - [Available when C++ bindings are built]")
        
        print("\n2. Functional NumPy access:")
        try:
            print("   - data = load_gpr_as_numpy('image.gpr', dtype='uint16')")
            data = load_gpr_as_numpy(temp_gpr, dtype='uint16')
        except NotImplementedError:
            print("   - [Available when C++ bindings are built]")
        
        print("\n3. Supported data types:")
        print("   - 'uint16': Raw sensor data (0-65535 range)")
        print("   - 'float32': Normalized data (0.0-1.0 range)")
        
    finally:
        if os.path.exists(temp_gpr):
            os.unlink(temp_gpr)


def main():
    """Run all demonstration functions."""
    print("Python-GPR High-Level API Demonstration")
    print("=" * 50)
    print()
    print("This demo shows the enhanced high-level Python wrapper API")
    print("with context manager support, intuitive naming, and convenience functions.")
    print()
    
    # Note about C++ bindings
    print("Note: Most functionality requires C++ bindings to be built.")
    print("This demo shows the API structure and error handling when bindings are not available.")
    print()
    
    try:
        demo_context_manager()
        demo_conversion_api()
        demo_pythonic_api()
        demo_resource_management()
        demo_numpy_integration()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nTo build the C++ bindings and enable full functionality:")
        print("1. Ensure the GPR submodule is initialized: git submodule update --init --recursive")
        print("2. Install build dependencies: pip install scikit-build-core pybind11 setuptools_scm")
        print("3. Build the package: pip install -e .")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())