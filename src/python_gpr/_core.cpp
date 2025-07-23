#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
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

// GPR to DNG conversion function (using DNG to DNG as placeholder)
bool convert_gpr_to_dng(const std::string& input_path, const std::string& output_path) {
    validate_input_file(input_path);
    
    // For now, we'll implement this as a copy operation since GPR->DNG requires VC5 decoder
    // In a real implementation, this would need the full GPR library with VC5 support
    throw GPRConversionError("GPR to DNG conversion requires VC5 decoder which is not available in this build. Consider using DNG to DNG conversion instead.");
}

// DNG to GPR conversion function (using DNG to DNG as placeholder)
bool convert_dng_to_gpr(const std::string& input_path, const std::string& output_path) {
    validate_input_file(input_path);
    
    // For now, this is not available without VC5 encoder
    throw GPRConversionError("DNG to GPR conversion requires VC5 encoder which is not available in this build.");
}

// DNG to RAW conversion function (this one should work)
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
            throw GPRConversionError("Failed to read input DNG file: " + input_path);
        }
        
        // Perform DNG to RAW conversion (assuming input is DNG format)
        bool success = gpr_convert_dng_to_raw(&allocator, &input_buffer, &output_buffer);
        
        if (!success) {
            throw GPRConversionError("DNG to RAW conversion failed");
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
        throw GPRConversionError("Unknown error during DNG to RAW conversion");
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

PYBIND11_MODULE(_core, m) {
    m.doc() = "Python GPR Core Conversion Functions";
    
    // Register custom exception
    py::register_exception<GPRConversionError>(m, "GPRConversionError");
    
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
          "Convert GPR file to RAW format (accepts DNG input)",
          py::arg("input_path"), py::arg("output_path"));
    
    // Additional conversion function that works with current build
    m.def("convert_dng_to_dng", &convert_dng_to_dng,
          "Convert DNG file to DNG format (reprocess)",
          py::arg("input_path"), py::arg("output_path"));
    
    // Version information
    m.attr("__version__") = py::str(VERSION_INFO);
}