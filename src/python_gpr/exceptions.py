"""
Comprehensive exception hierarchy for Python GPR library.

This module defines custom exception classes that map GPR library errors
to appropriate Python exceptions with clear error messages and context.
"""

from typing import Optional, Dict, Any


class GPRError(Exception):
    """
    Base exception for all GPR-related errors.
    
    This is the root exception class for all errors originating from
    the GPR library bindings.
    """
    
    def __init__(self, message: str, error_code: Optional[int] = None, 
                 context: Optional[Dict[str, Any]] = None):
        """
        Initialize GPR error with message, optional error code and context.
        
        Args:
            message: Human-readable error description
            error_code: Numeric error code from GPR library (if applicable)
            context: Additional context information about the error
        """
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}
        
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.error_code is not None:
            base_msg = f"[Error {self.error_code}] {base_msg}"
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base_msg = f"{base_msg} (Context: {context_str})"
            
        return base_msg


class GPRConversionError(GPRError):
    """
    Exception raised when GPR format conversion operations fail.
    
    This exception covers errors during conversion between different
    image formats (GPR, DNG, RAW, etc.).
    """
    pass


class GPRFileError(GPRError):
    """
    Exception raised for file-related operations.
    
    This includes file not found, permission errors, corrupted files, etc.
    """
    
    def __init__(self, message: str, error_code: Optional[int] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code=error_code, context=context)


class GPRFileNotFoundError(GPRFileError):
    """Exception raised when a required file cannot be found."""
    
    def __init__(self, filepath: str, message: Optional[str] = None, error_code: Optional[int] = None):
        self.filepath = filepath
        if message is None:
            message = f"File not found: {filepath}"
        super().__init__(message, error_code=error_code or -2, context={"filepath": filepath})


class GPRFilePermissionError(GPRFileError):
    """Exception raised when file access is denied due to permissions."""
    
    def __init__(self, filepath: str, operation: str, message: Optional[str] = None, error_code: Optional[int] = None):
        self.filepath = filepath
        self.operation = operation
        if message is None:
            message = f"Permission denied for {operation} operation on file: {filepath}"
        super().__init__(message, error_code=error_code or -3, context={"filepath": filepath, "operation": operation})


class GPRFileCorruptedError(GPRFileError):
    """Exception raised when a file is corrupted or has invalid format."""
    
    def __init__(self, filepath: str, reason: Optional[str] = None, message: Optional[str] = None, error_code: Optional[int] = None):
        self.filepath = filepath
        self.reason = reason
        if message is None:
            base_msg = f"File appears to be corrupted: {filepath}"
            if reason:
                message = f"{base_msg} (Reason: {reason})"
            else:
                message = base_msg
        context = {"filepath": filepath}
        if reason:
            context["reason"] = reason
        super().__init__(message, error_code=error_code or -4, context=context)


class GPRMemoryError(GPRError):
    """
    Exception raised for memory allocation and management errors.
    
    This includes out of memory conditions, buffer allocation failures, etc.
    """
    
    def __init__(self, message: str, requested_size: Optional[int] = None, error_code: Optional[int] = None):
        self.requested_size = requested_size
        context = {}
        if requested_size is not None:
            context["requested_size"] = requested_size
        super().__init__(message, error_code=error_code or -10, context=context)


class GPRParameterError(GPRError):
    """
    Exception raised for invalid parameters or configuration.
    
    This covers invalid parameter values, incompatible settings, etc.
    """
    
    def __init__(self, message: str, parameter_name: Optional[str] = None, error_code: Optional[int] = None):
        self.parameter_name = parameter_name
        context = {}
        if parameter_name:
            context["parameter"] = parameter_name
        super().__init__(message, error_code=error_code or -20, context=context)


class GPRFormatError(GPRError):
    """
    Exception raised for image format-related errors.
    
    This includes unsupported formats, format mismatches, etc.
    """
    
    def __init__(self, message: str, error_code: Optional[int] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code=error_code, context=context)


class GPRUnsupportedFormatError(GPRFormatError):
    """Exception raised when an unsupported format is encountered."""
    
    def __init__(self, format_name: str, supported_formats: Optional[list] = None, 
                 message: Optional[str] = None, error_code: Optional[int] = None):
        self.format_name = format_name
        self.supported_formats = supported_formats or []
        
        if message is None:
            if self.supported_formats:
                supported_str = ", ".join(self.supported_formats)
                message = f"Unsupported format '{format_name}'. Supported formats: {supported_str}"
            else:
                message = f"Unsupported format: {format_name}"
                
        context = {"format": format_name}
        if self.supported_formats:
            context["supported_formats"] = self.supported_formats
            
        super().__init__(message, error_code=error_code or -31, context=context)


class GPRCompressionError(GPRError):
    """
    Exception raised during compression/decompression operations.
    
    This covers VC-5 wavelet compression errors, codec failures, etc.
    """
    
    def __init__(self, message: str, error_code: Optional[int] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code=error_code, context=context)


class GPRMetadataError(GPRError):
    """
    Exception raised for metadata parsing and handling errors.
    
    This includes EXIF data errors, profile information issues, etc.
    """
    
    def __init__(self, message: str, error_code: Optional[int] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code=error_code, context=context)


class GPRBitstreamError(GPRError):
    """
    Exception raised for bitstream processing errors.
    
    This maps to BITSTREAM_ERROR codes from the GPR library.
    """
    
    # Map bitstream error codes to human-readable descriptions
    BITSTREAM_ERROR_MESSAGES = {
        0: "No error",
        1: "Bitstream underflow - no unread bits remaining",
        2: "Bitstream overflow - no more bits can be written", 
        3: "Unexpected tag found in bitstream",
    }
    
    def __init__(self, error_code: int, message: Optional[str] = None):
        if message is None:
            message = self.BITSTREAM_ERROR_MESSAGES.get(
                error_code, f"Unknown bitstream error (code {error_code})"
            )
        super().__init__(message, error_code=error_code)


class GPRResourceError(GPRError):
    """
    Exception raised for resource management errors.
    
    This includes cleanup failures, resource leaks, etc.
    """
    
    def __init__(self, message: str, error_code: Optional[int] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code=error_code, context=context)


# Error code mapping for common GPR library errors
ERROR_CODE_MAPPING = {
    # File operation errors
    -1: GPRFileError,
    -2: GPRFileNotFoundError,
    -3: GPRFilePermissionError,
    -4: GPRFileCorruptedError,
    
    # Memory errors  
    -10: GPRMemoryError,
    
    # Parameter errors
    -20: GPRParameterError,
    
    # Format errors
    -30: GPRFormatError,
    -31: GPRUnsupportedFormatError,
    
    # Compression errors
    -40: GPRCompressionError,
    
    # Metadata errors
    -50: GPRMetadataError,
    
    # Bitstream errors (map to specific codes)
    1: GPRBitstreamError,
    2: GPRBitstreamError,
    3: GPRBitstreamError,
}


def map_error_code(error_code: int, message: str, context: Optional[Dict[str, Any]] = None) -> GPRError:
    """
    Map a GPR library error code to the appropriate Python exception.
    
    Args:
        error_code: Numeric error code from GPR library
        message: Error message 
        context: Additional context information
        
    Returns:
        Appropriate GPRError subclass instance
    """
    exception_class = ERROR_CODE_MAPPING.get(error_code, GPRError)
    
    # Special handling for bitstream errors
    if exception_class == GPRBitstreamError:
        return GPRBitstreamError(error_code, message)
    
    # Special handling for file errors with known parameters
    if exception_class == GPRFileNotFoundError:
        filepath = context.get("filepath", "") if context else ""
        return GPRFileNotFoundError(filepath, message, error_code)
    elif exception_class == GPRFilePermissionError:
        filepath = context.get("filepath", "") if context else ""
        operation = context.get("operation", "unknown") if context else "unknown"
        return GPRFilePermissionError(filepath, operation, message, error_code)
    elif exception_class == GPRFileCorruptedError:
        filepath = context.get("filepath", "") if context else ""
        reason = context.get("reason") if context else None
        return GPRFileCorruptedError(filepath, reason, message, error_code)
    elif exception_class == GPRUnsupportedFormatError:
        format_name = context.get("format", "unknown") if context else "unknown"
        supported = context.get("supported_formats") if context else None
        return GPRUnsupportedFormatError(format_name, supported, message, error_code)
    elif exception_class == GPRMemoryError:
        requested_size = context.get("requested_size") if context else None
        return GPRMemoryError(message, requested_size, error_code)
    elif exception_class == GPRParameterError:
        parameter_name = context.get("parameter") if context else None
        return GPRParameterError(message, parameter_name, error_code)
    
    # For other error types, use the standard constructor
    return exception_class(message, error_code=error_code, context=context)


def create_file_error(filepath: str, operation: str, system_error: Optional[Exception] = None) -> GPRFileError:
    """
    Create an appropriate file error based on the type of system error.
    
    Args:
        filepath: Path to the file that caused the error
        operation: Operation being performed (read, write, etc.)
        system_error: Original system exception (if any)
        
    Returns:
        Appropriate GPRFileError subclass instance
    """
    if isinstance(system_error, FileNotFoundError):
        return GPRFileNotFoundError(filepath)
    elif isinstance(system_error, PermissionError):
        return GPRFilePermissionError(filepath, operation)
    elif isinstance(system_error, (OSError, IOError)):
        reason = str(system_error) if system_error else None
        return GPRFileCorruptedError(filepath, reason)
    else:
        message = f"File error during {operation} operation on {filepath}"
        if system_error:
            message += f": {system_error}"
        return GPRFileError(message, context={"filepath": filepath, "operation": operation})