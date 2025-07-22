"""
Python-GPR: Python bindings for the GPR (General Purpose Raw) library.

This package provides Python bindings for the GoPro GPR library, enabling
conversion between RAW, DNG, GPR, PPM, and JPG formats with VC-5 wavelet
compression support.

https://github.com/gopro/gpr
"""

# Version information
try:
    from ._version import version as __version__
except ImportError:
    # Fallback version when setuptools_scm is not available
    __version__ = "0.1.0"

__author__ = "Keenan Johnson"
__email__ = "keenan.johnson@gmail.com"
__description__ = "Python bindings for the GPR (General Purpose Raw) library"

# Import main functionality when available
try:
    from .core import *
    from .conversion import *
    from .metadata import *
    # Import C++ core module
    from ._core import *
except ImportError as e:
    # Bindings not yet available - this is expected during initial development
    import warnings
    warnings.warn(f"Some modules could not be imported: {e}", ImportWarning)

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__description__",
]