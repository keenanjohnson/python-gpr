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

// Custom exception for GPR conversion errors
class GPRConversionError : public std::runtime_error {
public:
    GPRConversionError(const std::string& message) : std::runtime_error("GPR Conversion Error: " + message) {}
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

// Helper function to validate file exists
void validate_input_file(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.good()) {
        throw GPRConversionError("Input file does not exist or cannot be read: " + filepath);
    }
}

// GPR to DNG conversion function
bool convert_gpr_to_dng(const std::string& input_path, const std::string& output_path) {
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
        
        // Set up default parameters
        gpr_parameters parameters;
        gpr_parameters_set_defaults(&parameters);
        
        // Perform GPR to DNG conversion
        bool success = gpr_convert_gpr_to_dng(&allocator, &parameters, &input_buffer, &output_buffer);
        
        if (!success) {
            throw GPRConversionError("GPR to DNG conversion failed");
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
        throw GPRConversionError("Unknown error during GPR to DNG conversion");
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

// Extract raw image data as NumPy array
py::array get_raw_image_data(const std::string& input_path, const std::string& dtype) {
    validate_input_file(input_path);
    
    // Get image information first
    ImageInfo info = get_image_info(input_path);
    
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
            throw GPRConversionError("Failed to read input file: " + input_path);
        }
        
        // Set up default parameters
        gpr_parameters parameters;
        gpr_parameters_set_defaults(&parameters);
        
        // Convert to raw format to get pixel data
        bool success = gpr_convert_gpr_to_raw(&allocator, &parameters, &input_buffer, &output_buffer);
        
        if (!success) {
            throw GPRConversionError("Failed to convert GPR to raw format for data extraction");
        }
        
        // Create NumPy array based on requested dtype
        py::array result;
        
        if (dtype == "uint16") {
            // Create uint16 array
            result = py::array_t<uint16_t>(
                {info.height, info.width},  // shape
                {info.width * sizeof(uint16_t), sizeof(uint16_t)},  // strides
                reinterpret_cast<uint16_t*>(output_buffer.buffer),  // data pointer
                py::cast(py::none())  // parent - we'll handle memory management
            );
        } else if (dtype == "float32") {
            // Convert uint16 data to float32 and normalize
            auto float_array = py::array_t<float>(info.height * info.width);
            float* float_data = static_cast<float*>(float_array.mutable_ptr());
            uint16_t* raw_data = reinterpret_cast<uint16_t*>(output_buffer.buffer);
            
            // Convert and normalize to 0-1 range
            for (size_t i = 0; i < info.height * info.width; ++i) {
                float_data[i] = static_cast<float>(raw_data[i]) / 65535.0f;
            }
            
            result = float_array.reshape({info.height, info.width});
        } else {
            throw GPRConversionError("Unsupported dtype: " + dtype + ". Supported types: uint16, float32");
        }
        
        // Clean up parameters
        gpr_parameters_destroy(&parameters, allocator.Free);
        
        // Clean up input buffer
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        
        // Note: output_buffer is now owned by the NumPy array for uint16,
        // or we've copied the data for float32, so we clean it up for float32
        if (dtype == "float32" && output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        
        return result;
        
    } catch (const GPRConversionError&) {
        // Clean up on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        throw;
    } catch (const std::exception& e) {
        // Clean up on error
        if (input_buffer.buffer) {
            allocator.Free(input_buffer.buffer);
        }
        if (output_buffer.buffer) {
            allocator.Free(output_buffer.buffer);
        }
        throw GPRConversionError("Error extracting raw image data: " + std::string(e.what()));
    }
}

PYBIND11_MODULE(_core, m) {
    m.doc() = "Python GPR Core Conversion Functions";
    
    // Register custom exception
    py::register_exception<GPRConversionError>(m, "GPRConversionError");
    
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
    
    // Helper functions for gpr_parameters
    m.def("gpr_parameters_set_defaults", [](gpr_parameters& params) {
        gpr_parameters_set_defaults(&params);
    }, "Set default values for GPR parameters", py::arg("params"));
    
    m.def("gpr_parameters_create_default", []() {
        gpr_parameters params;
        gpr_parameters_set_defaults(&params);
        return params;
    }, "Create GPR parameters with default values");
    
    // Basic hello world function for testing
    m.def("hello_world", &hello_world, "A simple hello world function");
    
    // Simple math function for testing
    m.def("add", &add, "Add two integers");
    
    // String manipulation function for testing
    m.def("greet", &greet, "Greet someone by name");
    
    // Core GPR conversion functions
    m.def("convert_gpr_to_dng", &convert_gpr_to_dng, 
          "Convert GPR file to DNG format",
          py::arg("input_path"), py::arg("output_path"));
    
    m.def("convert_dng_to_gpr", &convert_dng_to_gpr,
          "Convert DNG file to GPR format", 
          py::arg("input_path"), py::arg("output_path"));
    
    m.def("convert_gpr_to_raw", &convert_gpr_to_raw,
          "Convert GPR file to RAW format",
          py::arg("input_path"), py::arg("output_path"));
    
    // Additional conversion function that works with current build
    m.def("convert_dng_to_dng", &convert_dng_to_dng,
          "Convert DNG file to DNG format (reprocess)",
          py::arg("input_path"), py::arg("output_path"));
    
    // NumPy integration functions for raw image data access
    m.def("get_raw_image_data", &get_raw_image_data,
          "Extract raw image data as NumPy array from GPR file",
          py::arg("input_path"), py::arg("dtype") = "uint16");
    
    m.def("get_image_info", &get_image_info,
          "Get image dimensions and metadata from GPR file",
          py::arg("input_path"));
    
    // Version information
    m.attr("__version__") = py::str(VERSION_INFO);
}