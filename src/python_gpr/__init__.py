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

# Import exception classes first to ensure they're available
try:
    from .exceptions import *
    _exceptions_available = True
except ImportError as e:
    import warnings
    warnings.warn(f"Exception classes could not be imported: {e}", ImportWarning)
    _exceptions_available = False

# Import main functionality when available
try:
    from .core import *
    from .conversion import *
    from .metadata import *
    # Import C++ core module
    from ._core import *
    _bindings_available = True
except ImportError as e:
    # Bindings not yet available - this is expected during initial development
    import warnings
    warnings.warn(f"Some modules could not be imported: {e}", ImportWarning)
    _bindings_available = False

# Make exception classes available at package level
if _exceptions_available:
    # Re-export exception classes at package level for easy access
    __all__ = [
        "__version__",
        "__author__", 
        "__email__",
        "__description__",
        # Exception classes
        "GPRError",
        "GPRConversionError", 
        "GPRFileError",
        "GPRFileNotFoundError",
        "GPRFilePermissionError", 
        "GPRFileCorruptedError",
        "GPRMemoryError",
        "GPRParameterError",
        "GPRFormatError",
        "GPRUnsupportedFormatError",
        "GPRCompressionError",
        "GPRMetadataError",
        "GPRBitstreamError",
        "GPRResourceError",
        # Error handling utilities
        "map_error_code",
        "create_file_error",
    ]
else:
    __all__ = [
        "__version__",
        "__author__", 
        "__email__",
        "__description__",
    ]