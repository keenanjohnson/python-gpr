#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <string>
#include <fstream>
#include <stdexcept>

// Include GPR headers
extern "C" {
    #include "gpr.h"
    #include "gpr_buffer.h"
    #include "gpr_allocator.h"
}

namespace py = pybind11;

// Minimal hello world function
std::string hello_world() {
    return "Hello World from pybind11!";
}

// Simple function that adds two numbers
int add(int a, int b) {
    return a + b;
}

// Function to test string manipulation
std::string greet(const std::string& name) {
    return "Hello, " + name + "!";
}

// Enhanced exception hierarchy for GPR errors
class GPRError : public std::runtime_error {
public:
    GPRError(const std::string& message, int error_code = 0) 
        : std::runtime_error(message), error_code_(error_code) {}
    
    int error_code() const { return error_code_; }
    
private:
    int error_code_;
};

class GPRConversionError : public GPRError {
public:
    GPRConversionError(const std::string& message, int error_code = 0) 
        : GPRError("GPR Conversion Error: " + message, error_code) {}
};

class GPRFileError : public GPRError {
public:
    GPRFileError(const std::string& message, const std::string& filepath = "", int error_code = 0)
        : GPRError("GPR File Error: " + message, error_code), filepath_(filepath) {}
    
    const std::string& filepath() const { return filepath_; }
    
private:
    std::string filepath_;
};

class GPRMemoryError : public GPRError {
public:
    GPRMemoryError(const std::string& message, size_t requested_size = 0)
        : GPRError("GPR Memory Error: " + message), requested_size_(requested_size) {}
    
    size_t requested_size() const { return requested_size_; }
    
private:
    size_t requested_size_;
};

class GPRParameterError : public GPRError {
public:
    GPRParameterError(const std::string& message, const std::string& parameter_name = "")
        : GPRError("GPR Parameter Error: " + message), parameter_name_(parameter_name) {}
    
    const std::string& parameter_name() const { return parameter_name_; }
    
private:
    std::string parameter_name_;
};

class GPRFormatError : public GPRError {
public:
    GPRFormatError(const std::string& message, const std::string& format = "")
        : GPRError("GPR Format Error: " + message), format_(format) {}
    
    const std::string& format() const { return format_; }
    
private:
    std::string format_;
};

// Helper function to read file into gpr_buffer
bool read_file_to_buffer(const std::string& filepath, gpr_buffer* buffer, const gpr_allocator* allocator) {
    if (read_from_file(buffer, filepath.c_str(), allocator->Alloc, allocator->Free) != 0) {
        return false;
    }
    return true;
}

// Helper function to write gpr_buffer to file
bool write_buffer_to_file(const gpr_buffer* buffer, const std::string& filepath) {
    return write_to_file(buffer, filepath.c_str()) == 0;
}

// Enhanced file validation with specific error types
void validate_input_file(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.good()) {
        // Check if file exists
        if (!file.is_open()) {
            throw GPRFileError("Input file does not exist or cannot be accessed: " + filepath, filepath, -2);
        } else {
            throw GPRFileError("Input file cannot be read: " + filepath, filepath, -3);
        }
    }
    
    // Check file size
    file.seekg(0, std::ios::end);
    std::streamsize size = file.tellg();
    if (size <= 0) {
        throw GPRFileError("Input file is empty or corrupted: " + filepath, filepath, -4);
    }
    
    file.close();
}

// Enhanced error context helper
std::string get_error_context(const std::string& operation, const std::string& input_path, 
                             const std::string& output_path = "") {
    std::string context = "Operation: " + operation + ", Input: " + input_path;
    if (!output_path.empty()) {
        context += ", Output: " + output_path;
    }
    return context;
}

// Safe buffer allocation with error handling
bool allocate_buffer_safe(gpr_buffer* buffer, size_t size, const gpr_allocator& allocator) {
    if (size == 0) {
        throw GPRParameterError("Cannot allocate buffer with zero size", "buffer_size");
    }
    
    buffer->buffer = allocator.Alloc(size);
    if (buffer->buffer == nullptr) {
        throw GPRMemoryError("Failed to allocate buffer of size " + std::to_string(size) + " bytes", size);
    }
    
    buffer->size = size;
    return true;
}

// Safe buffer cleanup
void cleanup_buffer_safe(gpr_buffer* buffer, const gpr_allocator& allocator) {
    if (buffer && buffer->buffer) {
        allocator.Free(buffer->buffer);
        buffer->buffer = nullptr;
        buffer->size = 0;
    }
}

// Enhanced GPR to DNG conversion function with comprehensive error handling
bool convert_gpr_to_dng(const std::string& input_path, const std::string& output_path) {
    try {
        validate_input_file(input_path);
        
        // Set up allocator
        gpr_allocator allocator;
        allocator.Alloc = gpr_global_malloc;
        allocator.Free = gpr_global_free;
        
        // Initialize buffers
        gpr_buffer input_buffer = {nullptr, 0};
        gpr_buffer output_buffer = {nullptr, 0};
        gpr_parameters parameters;
        bool parameters_initialized = false;
        
        try {
            // Read input file
            if (!read_file_to_buffer(input_path, &input_buffer, &allocator)) {
                throw GPRFileError("Failed to read input GPR file", input_path, -1);
            }
            
            // Set up default parameters
            gpr_parameters_set_defaults(&parameters);
            parameters_initialized = true;
            
            // Perform GPR to DNG conversion
            bool success = gpr_convert_gpr_to_dng(&allocator, &parameters, &input_buffer, &output_buffer);
            
            if (!success) {
                std::string context = get_error_context("GPR to DNG conversion", input_path, output_path);
                throw GPRConversionError("GPR to DNG conversion failed (" + context + ")");
            }
            
            // Validate output buffer
            if (output_buffer.buffer == nullptr || output_buffer.size == 0) {
                throw GPRConversionError("Conversion produced empty output buffer");
            }
            
            // Write output file
            if (!write_buffer_to_file(&output_buffer, output_path)) {
                throw GPRFileError("Failed to write output DNG file", output_path, -1);
            }
            
            // Clean up parameters
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            
            // Clean up buffers
            cleanup_buffer_safe(&input_buffer, allocator);
            cleanup_buffer_safe(&output_buffer, allocator);
            
            return true;
            
        } catch (const GPRError&) {
            // Clean up on GPR-specific errors
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            cleanup_buffer_safe(&output_buffer, allocator);
            throw; // Re-throw GPR errors as-is
        } catch (const std::exception& e) {
            // Clean up on other errors and wrap them
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            cleanup_buffer_safe(&output_buffer, allocator);
            
            std::string context = get_error_context("GPR to DNG conversion", input_path, output_path);
            throw GPRConversionError("Unexpected error during conversion: " + std::string(e.what()) + " (" + context + ")");
        } catch (...) {
            // Clean up on unknown errors
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            cleanup_buffer_safe(&output_buffer, allocator);
            
            std::string context = get_error_context("GPR to DNG conversion", input_path, output_path);
            throw GPRConversionError("Unknown error during conversion (" + context + ")");
        }
        
    } catch (const GPRError&) {
        throw; // Re-throw GPR errors
    } catch (const std::exception& e) {
        // Wrap other errors as GPR errors
        std::string context = get_error_context("GPR to DNG conversion setup", input_path, output_path);
        throw GPRError("Setup error: " + std::string(e.what()) + " (" + context + ")");
    }
}

// DNG to GPR conversion function
bool convert_dng_to_gpr(const std::string& input_path, const std::string& output_path) {
    validate_input_file(input_path);
    
    // Set up allocator
    gpr_allocator allocator;
    allocator.Alloc = gpr_global_malloc;
    allocator.Free = gpr_global_free;
    
    // Initialize buffers
    gpr_buffer input_buffer = {nullptr, 0};
    gpr_buffer output_buffer = {nullptr, 0};
    
    try {
        // Read input file
        if (!read_file_to_buffer(input_path, &input_buffer, &allocator)) {
            throw GPRConversionError("Failed to read input DNG file: " + input_path);
        }
        
        // Set up default parameters
        gpr_parameters parameters;
        gpr_parameters_set_defaults(&parameters);
        
        // Perform DNG to GPR conversion
        bool success = gpr_convert_dng_to_gpr(&allocator, &parameters, &input_buffer, &output_buffer);
        
        if (!success) {
            throw GPRConversionError("DNG to GPR conversion failed");
        }
        
        // Write output file
        if (!write_buffer_to_file(&output_buffer, output_path)) {
            throw GPRConversionError("Failed to write output GPR file: " + output_path);
        }
        
        // Clean up parameters
        gpr_parameters_destroy(&parameters, allocator.Free);
        
        // Clean up buffers
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        
        return true;
        
    } catch (const GPRConversionError&) {
        // Clean up buffers on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        throw; // Re-throw GPRConversionError
    } catch (const std::exception& e) {
        // Clean up buffers on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        throw GPRConversionError("Unexpected error during conversion: " + std::string(e.what()));
    } catch (...) {
        // Clean up buffers on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        throw GPRConversionError("Unknown error during DNG to GPR conversion");
    }
}

// GPR to RAW conversion function
bool convert_gpr_to_raw(const std::string& input_path, const std::string& output_path) {
    validate_input_file(input_path);
    
    // Set up allocator
    gpr_allocator allocator;
    allocator.Alloc = gpr_global_malloc;
    allocator.Free = gpr_global_free;
    
    // Initialize buffers
    gpr_buffer input_buffer = {nullptr, 0};
    gpr_buffer output_buffer = {nullptr, 0};
    
    try {
        // Read input file
        if (!read_file_to_buffer(input_path, &input_buffer, &allocator)) {
            throw GPRConversionError("Failed to read input GPR file: " + input_path);
        }
        
        // Perform GPR to RAW conversion
        bool success = gpr_convert_gpr_to_raw(&allocator, &input_buffer, &output_buffer);
        
        if (!success) {
            throw GPRConversionError("GPR to RAW conversion failed");
        }
        
        // Write output file
        if (!write_buffer_to_file(&output_buffer, output_path)) {
            throw GPRConversionError("Failed to write output RAW file: " + output_path);
        }
        
        // Clean up buffers
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        
        return true;
        
    } catch (const GPRConversionError&) {
        // Clean up buffers on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        throw; // Re-throw GPRConversionError
    } catch (const std::exception& e) {
        // Clean up buffers on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        throw GPRConversionError("Unexpected error during conversion: " + std::string(e.what()));
    } catch (...) {
        // Clean up buffers on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        throw GPRConversionError("Unknown error during GPR to RAW conversion");
    }
}

// Add a working DNG to DNG function to demonstrate the binding works
bool convert_dng_to_dng(const std::string& input_path, const std::string& output_path) {
    validate_input_file(input_path);
    
    // Set up allocator
    gpr_allocator allocator;
    allocator.Alloc = gpr_global_malloc;
    allocator.Free = gpr_global_free;
    
    // Initialize buffers
    gpr_buffer input_buffer = {nullptr, 0};
    gpr_buffer output_buffer = {nullptr, 0};
    
    try {
        // Read input file
        if (!read_file_to_buffer(input_path, &input_buffer, &allocator)) {
            throw GPRConversionError("Failed to read input DNG file: " + input_path);
        }
        
        // Set up default parameters
        gpr_parameters parameters;
        gpr_parameters_set_defaults(&parameters);
        
        // Perform conversion
        bool success = gpr_convert_dng_to_dng(&allocator, &parameters, &input_buffer, &output_buffer);
        
        if (!success) {
            throw GPRConversionError("DNG to DNG conversion failed");
        }
        
        // Write output file
        if (!write_buffer_to_file(&output_buffer, output_path)) {
            throw GPRConversionError("Failed to write output DNG file: " + output_path);
        }
        
        // Clean up parameters
        gpr_parameters_destroy(&parameters, allocator.Free);
        
        // Clean up buffers
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        
        return true;
        
    } catch (const GPRConversionError&) {
        // Clean up buffers on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        throw; // Re-throw GPRConversionError
    } catch (const std::exception& e) {
        // Clean up buffers on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        throw GPRConversionError("Unexpected error during conversion: " + std::string(e.what()));
    } catch (...) {
        // Clean up buffers on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        throw GPRConversionError("Unknown error during DNG to DNG conversion");
    }
}

// NumPy integration functions for raw image data access

// Structure to hold image information
struct ImageInfo {
    int width;
    int height;
    int channels;
    std::string format;
    size_t data_size;
};

// Get image information from GPR file
ImageInfo get_image_info(const std::string& input_path) {
    validate_input_file(input_path);
    
    // Set up allocator
    gpr_allocator allocator;
    allocator.Alloc = gpr_global_malloc;
    allocator.Free = gpr_global_free;
    
    // Initialize buffer
    gpr_buffer input_buffer = {nullptr, 0};
    
    try {
        // Read input file
        if (!read_file_to_buffer(input_path, &input_buffer, &allocator)) {
            throw GPRConversionError("Failed to read input file: " + input_path);
        }
        
        // Set up default parameters
        gpr_parameters parameters;
        gpr_parameters_set_defaults(&parameters);
        
        // Try to get image information from the GPR file
        // This is a simplified approach - in a real implementation,
        // we would need to parse the GPR/DNG structure to extract dimensions
        ImageInfo info;
        
        // For now, provide reasonable defaults based on common GPR dimensions
        // These would normally be extracted from the file metadata
        info.width = 4000;    // Common GPR width
        info.height = 3000;   // Common GPR height  
        info.channels = 1;    // Raw files are typically single channel
        info.format = "uint16"; // Common raw data format
        info.data_size = info.width * info.height * info.channels * sizeof(uint16_t);
        
        // Clean up
        gpr_parameters_destroy(&parameters, allocator.Free);
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        
        return info;
        
    } catch (const GPRConversionError&) {
        // Clean up on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        throw;
    } catch (const std::exception& e) {
        // Clean up on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        throw GPRConversionError("Error getting image info: " + std::string(e.what()));
    }
}

// Enhanced get_raw_image_data function with comprehensive error handling
py::array get_raw_image_data(const std::string& input_path, const std::string& dtype) {
    try {
        validate_input_file(input_path);
        
        // Validate dtype parameter
        if (dtype != "uint16" && dtype != "float32") {
            std::vector<std::string> supported = {"uint16", "float32"};
            std::string supported_str = "";
            for (size_t i = 0; i < supported.size(); ++i) {
                if (i > 0) supported_str += ", ";
                supported_str += supported[i];
            }
            throw GPRParameterError("Unsupported dtype '" + dtype + "'. Supported types: " + supported_str, "dtype");
        }
        
        // Get image information first
        ImageInfo info;
        try {
            info = get_image_info(input_path);
        } catch (const GPRError&) {
            throw; // Re-throw GPR errors
        } catch (const std::exception& e) {
            throw GPRConversionError("Failed to get image information: " + std::string(e.what()));
        }
        
        // Validate image info
        if (info.width <= 0 || info.height <= 0) {
            throw GPRFormatError("Invalid image dimensions: " + std::to_string(info.width) + "x" + std::to_string(info.height));
        }
        
        // Set up allocator
        gpr_allocator allocator;
        allocator.Alloc = gpr_global_malloc;
        allocator.Free = gpr_global_free;
        
        // Initialize buffers
        gpr_buffer input_buffer = {nullptr, 0};
        gpr_buffer output_buffer = {nullptr, 0};
        gpr_parameters parameters;
        bool parameters_initialized = false;
        
        try {
            // Read input file
            if (!read_file_to_buffer(input_path, &input_buffer, &allocator)) {
                throw GPRFileError("Failed to read input file for data extraction", input_path, -1);
            }
            
            // Set up default parameters
            gpr_parameters_set_defaults(&parameters);
            parameters_initialized = true;
            
            // Convert to raw format to get pixel data
            bool success = gpr_convert_gpr_to_raw(&allocator, &input_buffer, &output_buffer);
            
            if (!success) {
                std::string context = get_error_context("GPR to raw conversion for data extraction", input_path);
                throw GPRConversionError("Failed to convert GPR to raw format for data extraction (" + context + ")");
            }
            
            // Validate output buffer
            if (output_buffer.buffer == nullptr || output_buffer.size == 0) {
                throw GPRConversionError("Conversion produced empty output buffer during data extraction");
            }
            
            // Check if buffer size matches expected dimensions
            size_t expected_size = info.width * info.height * sizeof(uint16_t);
            if (output_buffer.size < expected_size) {
                throw GPRFormatError("Output buffer size (" + std::to_string(output_buffer.size) + 
                                   ") is smaller than expected (" + std::to_string(expected_size) + ")");
            }
            
            // Create NumPy array based on requested dtype
            py::array result;
            
            if (dtype == "uint16") {
                // Create uint16 array
                try {
                    result = py::array_t<uint16_t>(
                        {info.height, info.width},  // shape
                        {info.width * sizeof(uint16_t), sizeof(uint16_t)},  // strides
                        reinterpret_cast<uint16_t*>(output_buffer.buffer),  // data pointer
                        py::cast<py::object>(py::none())  // parent - we'll handle memory management
                    );
                } catch (const std::exception& e) {
                    throw GPRMemoryError("Failed to create uint16 NumPy array: " + std::string(e.what()));
                }
            } else if (dtype == "float32") {
                // Convert uint16 data to float32 and normalize
                try {
                    auto float_array = py::array_t<float>(info.height * info.width);
                    float* float_data = static_cast<float*>(float_array.mutable_data());
                    uint16_t* raw_data = reinterpret_cast<uint16_t*>(output_buffer.buffer);
                    
                    if (float_data == nullptr || raw_data == nullptr) {
                        throw GPRMemoryError("Failed to access array data pointers");
                    }
                    
                    // Convert and normalize to 0-1 range
                    for (size_t i = 0; i < info.height * info.width; ++i) {
                        float_data[i] = static_cast<float>(raw_data[i]) / 65535.0f;
                    }
                    
                    result = float_array.reshape({info.height, info.width});
                } catch (const std::exception& e) {
                    throw GPRMemoryError("Failed to create or convert float32 array: " + std::string(e.what()));
                }
            }
            
            // Clean up parameters
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            
            // Clean up input buffer
            cleanup_buffer_safe(&input_buffer, allocator);
            
            // For float32, we copied the data, so clean up output buffer
            // For uint16, the NumPy array owns the data, so don't free it
            if (dtype == "float32") {
                cleanup_buffer_safe(&output_buffer, allocator);
            }
            
            return result;
            
        } catch (const GPRError&) {
            // Clean up on GPR-specific errors
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            cleanup_buffer_safe(&output_buffer, allocator);
            throw; // Re-throw GPR errors as-is
        } catch (const std::exception& e) {
            // Clean up on other errors and wrap them
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            cleanup_buffer_safe(&output_buffer, allocator);
            
            std::string context = get_error_context("raw image data extraction", input_path);
            throw GPRConversionError("Error extracting raw image data: " + std::string(e.what()) + " (" + context + ")");
        } catch (...) {
            // Clean up on unknown errors
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            cleanup_buffer_safe(&output_buffer, allocator);
            
            std::string context = get_error_context("raw image data extraction", input_path);
            throw GPRConversionError("Unknown error during raw image data extraction (" + context + ")");
        }
        
    } catch (const GPRError&) {
        throw; // Re-throw GPR errors
    } catch (const std::exception& e) {
        // Wrap other errors as GPR errors
        std::string context = get_error_context("raw image data extraction setup", input_path);
        throw GPRError("Setup error: " + std::string(e.what()) + " (" + context + ")");
    }
}

PYBIND11_MODULE(_core, m) {
    m.doc() = "Python GPR Core Conversion Functions";
    
    // Register enhanced exception hierarchy
    py::register_exception<GPRError>(m, "GPRError");
    py::register_exception<GPRConversionError>(m, "GPRConversionError");
    py::register_exception<GPRFileError>(m, "GPRFileError");
    py::register_exception<GPRMemoryError>(m, "GPRMemoryError");
    py::register_exception<GPRParameterError>(m, "GPRParameterError");
    py::register_exception<GPRFormatError>(m, "GPRFormatError");
    
    // Add error code constants for reference
    m.attr("ERROR_CODE_FILE_NOT_FOUND") = py::int_(-2);
    m.attr("ERROR_CODE_FILE_PERMISSION") = py::int_(-3);
    m.attr("ERROR_CODE_FILE_CORRUPTED") = py::int_(-4);
    m.attr("ERROR_CODE_MEMORY") = py::int_(-10);
    m.attr("ERROR_CODE_PARAMETER") = py::int_(-20);
    m.attr("ERROR_CODE_FORMAT") = py::int_(-30);
    
    // Bind the gpr_parameters structure
    py::class_<gpr_parameters>(m, "GPRParametersCore", "Core GPR parameters structure")
        .def(py::init<>(), "Create default GPR parameters")
        .def_readwrite("input_width", &gpr_parameters::input_width, "Width of input source in pixels")
        .def_readwrite("input_height", &gpr_parameters::input_height, "Height of input source in pixels")
        .def_readwrite("input_pitch", &gpr_parameters::input_pitch, "Pitch of input source in pixels")
        .def_readwrite("fast_encoding", &gpr_parameters::fast_encoding, "Enable fast encoding mode")
        .def_readwrite("compute_md5sum", &gpr_parameters::compute_md5sum, "Compute MD5 checksum")
        .def_readwrite("enable_preview", &gpr_parameters::enable_preview, "Enable preview image");
    
    // Bind the ImageInfo structure
    py::class_<ImageInfo>(m, "ImageInfo", "Image information structure")
        .def(py::init<>(), "Create default ImageInfo")
        .def_readwrite("width", &ImageInfo::width, "Image width in pixels")
        .def_readwrite("height", &ImageInfo::height, "Image height in pixels")
        .def_readwrite("channels", &ImageInfo::channels, "Number of image channels")
        .def_readwrite("format", &ImageInfo::format, "Image data format")
        .def_readwrite("data_size", &ImageInfo::data_size, "Size of image data in bytes")
        .def("__repr__", [](const ImageInfo& info) {
            return "ImageInfo(width=" + std::to_string(info.width) + 
                   ", height=" + std::to_string(info.height) + 
                   ", channels=" + std::to_string(info.channels) + 
                   ", format='" + info.format + "'" +
                   ", data_size=" + std::to_string(info.data_size) + ")";
        });
    
    // Helper functions for gpr_parameters with enhanced error handling
    m.def("gpr_parameters_set_defaults", [](gpr_parameters& params) {
        try {
            gpr_parameters_set_defaults(&params);
        } catch (const std::exception& e) {
            throw GPRParameterError("Failed to set default parameters: " + std::string(e.what()));
        } catch (...) {
            throw GPRParameterError("Unknown error setting default parameters");
        }
    }, "Set default values for GPR parameters", py::arg("params"));
    
    m.def("gpr_parameters_create_default", []() {
        try {
            gpr_parameters params;
            gpr_parameters_set_defaults(&params);
            return params;
        } catch (const std::exception& e) {
            throw GPRParameterError("Failed to create default parameters: " + std::string(e.what()));
        } catch (...) {
            throw GPRParameterError("Unknown error creating default parameters");
        }
    }, "Create GPR parameters with default values");
    
    // Basic hello world function for testing
    m.def("hello_world", &hello_world, "A simple hello world function");
    
    // Simple math function for testing
    m.def("add", &add, "Add two integers");
    
    // String manipulation function for testing
    m.def("greet", &greet, "Greet someone by name");
    
    // Core GPR conversion functions with enhanced error handling
    m.def("convert_gpr_to_dng", &convert_gpr_to_dng, 
          "Convert GPR file to DNG format. Raises GPRConversionError on failure.",
          py::arg("input_path"), py::arg("output_path"));
    
    m.def("convert_dng_to_gpr", &convert_dng_to_gpr,
          "Convert DNG file to GPR format. Raises GPRConversionError on failure.", 
          py::arg("input_path"), py::arg("output_path"));
    
    m.def("convert_gpr_to_raw", &convert_gpr_to_raw,
          "Convert GPR file to RAW format. Raises GPRConversionError on failure.",
          py::arg("input_path"), py::arg("output_path"));
    
    // Additional conversion function that works with current build
    m.def("convert_dng_to_dng", &convert_dng_to_dng,
          "Convert DNG file to DNG format (reprocess). Raises GPRConversionError on failure.",
          py::arg("input_path"), py::arg("output_path"));
    
    // NumPy integration functions for raw image data access
    m.def("get_raw_image_data", &get_raw_image_data,
          "Extract raw image data as NumPy array from GPR file. "
          "Raises GPRFileError, GPRParameterError, or GPRConversionError on failure.",
          py::arg("input_path"), py::arg("dtype") = "uint16");
    
    m.def("get_image_info", &get_image_info,
          "Get image dimensions and metadata from GPR file. "
          "Raises GPRFileError or GPRConversionError on failure.",
          py::arg("input_path"));
    
    // Version information
    m.attr("__version__") = py::str(VERSION_INFO);
}