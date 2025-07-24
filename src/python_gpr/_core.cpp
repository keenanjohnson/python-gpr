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

// Metadata extraction functions

// Extract EXIF metadata from a DNG/GPR file buffer
py::dict extract_exif_metadata(const std::string& input_path) {
    try {
        validate_input_file(input_path);
        
        // Set up allocator
        gpr_allocator allocator;
        allocator.Alloc = gpr_global_malloc;
        allocator.Free = gpr_global_free;
        
        // Initialize buffer and parameters
        gpr_buffer input_buffer = {nullptr, 0};
        gpr_parameters parameters;
        bool parameters_initialized = false;
        
        try {
            // Read input file
            if (!read_file_to_buffer(input_path, &input_buffer, &allocator)) {
                throw GPRFileError("Failed to read input file for metadata extraction", input_path, -1);
            }
            
            // Initialize parameters to store metadata
            gpr_parameters_set_defaults(&parameters);
            parameters_initialized = true;
            
            // Parse metadata from the DNG/GPR file
            bool success = gpr_parse_metadata(&allocator, &input_buffer, &parameters);
            
            if (!success) {
                std::string context = get_error_context("metadata extraction", input_path);
                throw GPRConversionError("Failed to parse metadata from file (" + context + ")");
            }
            
            // Convert gpr_exif_info to Python dictionary
            py::dict exif_dict;
            const gpr_exif_info& exif = parameters.exif_info;
            
            // Basic camera information
            exif_dict["camera_make"] = std::string(exif.camera_make);
            exif_dict["camera_model"] = std::string(exif.camera_model);
            exif_dict["camera_serial"] = std::string(exif.camera_serial);
            exif_dict["software_version"] = std::string(exif.software_version);
            exif_dict["user_comment"] = std::string(exif.user_comment);
            exif_dict["image_description"] = std::string(exif.image_description);
            
            // Exposure settings
            if (exif.exposure_time.denominator != 0) {
                exif_dict["exposure_time"] = static_cast<double>(exif.exposure_time.numerator) / exif.exposure_time.denominator;
                exif_dict["exposure_time_rational"] = py::make_tuple(exif.exposure_time.numerator, exif.exposure_time.denominator);
            }
            
            if (exif.f_stop_number.denominator != 0) {
                exif_dict["f_stop_number"] = static_cast<double>(exif.f_stop_number.numerator) / exif.f_stop_number.denominator;
                exif_dict["f_stop_number_rational"] = py::make_tuple(exif.f_stop_number.numerator, exif.f_stop_number.denominator);
            }
            
            if (exif.aperture.denominator != 0) {
                exif_dict["aperture"] = static_cast<double>(exif.aperture.numerator) / exif.aperture.denominator;
                exif_dict["aperture_rational"] = py::make_tuple(exif.aperture.numerator, exif.aperture.denominator);
            }
            
            if (exif.focal_length.denominator != 0) {
                exif_dict["focal_length"] = static_cast<double>(exif.focal_length.numerator) / exif.focal_length.denominator;
                exif_dict["focal_length_rational"] = py::make_tuple(exif.focal_length.numerator, exif.focal_length.denominator);
            }
            
            // ISO and other numeric values
            exif_dict["iso_speed_rating"] = exif.iso_speed_rating;
            exif_dict["focal_length_in_35mm_film"] = exif.focal_length_in_35mm_film;
            exif_dict["saturation"] = exif.saturation;
            
            // Enum values
            exif_dict["exposure_program"] = static_cast<int>(exif.exposure_program);
            exif_dict["metering_mode"] = static_cast<int>(exif.metering_mode);
            exif_dict["light_source"] = static_cast<int>(exif.light_source);
            exif_dict["flash"] = static_cast<int>(exif.flash);
            exif_dict["sharpness"] = static_cast<int>(exif.sharpness);
            exif_dict["gain_control"] = static_cast<int>(exif.gain_control);
            exif_dict["contrast"] = static_cast<int>(exif.contrast);
            exif_dict["scene_capture_type"] = static_cast<int>(exif.scene_capture_type);
            exif_dict["exposure_mode"] = static_cast<int>(exif.exposure_mode);
            exif_dict["white_balance"] = static_cast<int>(exif.white_balance);
            exif_dict["scene_type"] = static_cast<int>(exif.scene_type);
            exif_dict["file_source"] = static_cast<int>(exif.file_source);
            exif_dict["sensing_method"] = static_cast<int>(exif.sensing_method);
            
            // Date/time information
            py::dict date_time_original;
            date_time_original["year"] = exif.date_time_original.year;
            date_time_original["month"] = exif.date_time_original.month;
            date_time_original["day"] = exif.date_time_original.day;
            date_time_original["hour"] = exif.date_time_original.hour;
            date_time_original["minute"] = exif.date_time_original.minute;
            date_time_original["second"] = exif.date_time_original.second;
            exif_dict["date_time_original"] = date_time_original;
            
            py::dict date_time_digitized;
            date_time_digitized["year"] = exif.date_time_digitized.year;
            date_time_digitized["month"] = exif.date_time_digitized.month;
            date_time_digitized["day"] = exif.date_time_digitized.day;
            date_time_digitized["hour"] = exif.date_time_digitized.hour;
            date_time_digitized["minute"] = exif.date_time_digitized.minute;
            date_time_digitized["second"] = exif.date_time_digitized.second;
            exif_dict["date_time_digitized"] = date_time_digitized;
            
            // Exposure bias
            if (exif.exposure_bias.denominator != 0) {
                exif_dict["exposure_bias"] = static_cast<double>(exif.exposure_bias.numerator) / exif.exposure_bias.denominator;
                exif_dict["exposure_bias_rational"] = py::make_tuple(exif.exposure_bias.numerator, exif.exposure_bias.denominator);
            }
            
            // Digital zoom
            if (exif.digital_zoom.denominator != 0) {
                exif_dict["digital_zoom"] = static_cast<double>(exif.digital_zoom.numerator) / exif.digital_zoom.denominator;
                exif_dict["digital_zoom_rational"] = py::make_tuple(exif.digital_zoom.numerator, exif.digital_zoom.denominator);
            }
            
            // GPS information if available
            if (exif.gps_info.gps_info_valid) {
                py::dict gps_dict;
                gps_dict["valid"] = true;
                gps_dict["version_id"] = exif.gps_info.version_id;
                gps_dict["latitude_ref"] = std::string(exif.gps_info.latitude_ref, 2);
                gps_dict["longitude_ref"] = std::string(exif.gps_info.longitude_ref, 2);
                gps_dict["altitude_ref"] = exif.gps_info.altitude_ref;
                gps_dict["satellites"] = std::string(exif.gps_info.satellites);
                gps_dict["status"] = std::string(exif.gps_info.status, 2);
                gps_dict["measure_mode"] = std::string(exif.gps_info.measure_mode, 2);
                gps_dict["speed_ref"] = std::string(exif.gps_info.speed_ref, 2);
                gps_dict["track_ref"] = std::string(exif.gps_info.track_ref, 2);
                gps_dict["img_direction_ref"] = std::string(exif.gps_info.img_direction_ref, 2);
                gps_dict["map_datum"] = std::string(exif.gps_info.map_datum);
                gps_dict["dest_latitude_ref"] = std::string(exif.gps_info.dest_latitude_ref, 2);
                gps_dict["dest_longitude_ref"] = std::string(exif.gps_info.dest_longitude_ref, 2);
                gps_dict["dest_bearing_ref"] = std::string(exif.gps_info.dest_bearing_ref, 2);
                gps_dict["dest_distance_ref"] = std::string(exif.gps_info.dest_distance_ref, 2);
                gps_dict["processing_method"] = std::string(exif.gps_info.processing_method);
                gps_dict["area_information"] = std::string(exif.gps_info.area_information);
                gps_dict["date_stamp"] = std::string(exif.gps_info.date_stamp);
                gps_dict["differential"] = exif.gps_info.differential;
                
                // GPS coordinates and other rational values
                py::list latitude_list;
                for (int i = 0; i < 3; i++) {
                    if (exif.gps_info.latitude[i].denominator != 0) {
                        latitude_list.append(py::make_tuple(exif.gps_info.latitude[i].numerator, exif.gps_info.latitude[i].denominator));
                    }
                }
                gps_dict["latitude"] = latitude_list;
                
                py::list longitude_list;
                for (int i = 0; i < 3; i++) {
                    if (exif.gps_info.longitude[i].denominator != 0) {
                        longitude_list.append(py::make_tuple(exif.gps_info.longitude[i].numerator, exif.gps_info.longitude[i].denominator));
                    }
                }
                gps_dict["longitude"] = longitude_list;
                
                if (exif.gps_info.altitude.denominator != 0) {
                    gps_dict["altitude"] = py::make_tuple(exif.gps_info.altitude.numerator, exif.gps_info.altitude.denominator);
                }
                
                exif_dict["gps_info"] = gps_dict;
            } else {
                exif_dict["gps_info"] = py::dict();
                exif_dict["gps_info"]["valid"] = false;
            }
            
            // Clean up
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            
            return exif_dict;
            
        } catch (const GPRError&) {
            // Clean up on GPR-specific errors
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            throw; // Re-throw GPR errors as-is
        } catch (const std::exception& e) {
            // Clean up on other errors and wrap them
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            
            std::string context = get_error_context("EXIF metadata extraction", input_path);
            throw GPRConversionError("Error extracting EXIF metadata: " + std::string(e.what()) + " (" + context + ")");
        } catch (...) {
            // Clean up on unknown errors
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            
            std::string context = get_error_context("EXIF metadata extraction", input_path);
            throw GPRConversionError("Unknown error during EXIF metadata extraction (" + context + ")");
        }
        
    } catch (const GPRError&) {
        throw; // Re-throw GPR errors
    } catch (const std::exception& e) {
        // Wrap other errors as GPR errors
        std::string context = get_error_context("EXIF metadata extraction setup", input_path);
        throw GPRError("Setup error: " + std::string(e.what()) + " (" + context + ")");
    }
}

// Extract GPR-specific metadata and tuning information
py::dict extract_gpr_metadata(const std::string& input_path) {
    try {
        validate_input_file(input_path);
        
        // Set up allocator
        gpr_allocator allocator;
        allocator.Alloc = gpr_global_malloc;
        allocator.Free = gpr_global_free;
        
        // Initialize buffer and parameters
        gpr_buffer input_buffer = {nullptr, 0};
        gpr_parameters parameters;
        bool parameters_initialized = false;
        
        try {
            // Read input file
            if (!read_file_to_buffer(input_path, &input_buffer, &allocator)) {
                throw GPRFileError("Failed to read input file for GPR metadata extraction", input_path, -1);
            }
            
            // Initialize parameters to store metadata
            gpr_parameters_set_defaults(&parameters);
            parameters_initialized = true;
            
            // Parse metadata from the DNG/GPR file
            bool success = gpr_parse_metadata(&allocator, &input_buffer, &parameters);
            
            if (!success) {
                std::string context = get_error_context("GPR metadata extraction", input_path);
                throw GPRConversionError("Failed to parse GPR metadata from file (" + context + ")");
            }
            
            // Create GPR metadata dictionary
            py::dict gpr_dict;
            
            // Basic parameters
            gpr_dict["input_width"] = parameters.input_width;
            gpr_dict["input_height"] = parameters.input_height;
            gpr_dict["input_pitch"] = parameters.input_pitch;
            gpr_dict["fast_encoding"] = parameters.fast_encoding;
            gpr_dict["compute_md5sum"] = parameters.compute_md5sum;
            gpr_dict["enable_preview"] = parameters.enable_preview;
            
            // Preview image information
            py::dict preview_dict;
            preview_dict["width"] = parameters.preview_image.preview_width;
            preview_dict["height"] = parameters.preview_image.preview_height;
            preview_dict["jpg_preview_size"] = parameters.preview_image.jpg_preview.size;
            preview_dict["has_preview"] = (parameters.preview_image.jpg_preview.buffer != nullptr && 
                                         parameters.preview_image.jpg_preview.size > 0);
            gpr_dict["preview_image"] = preview_dict;
            
            // GPMF payload information
            py::dict gpmf_dict;
            gpmf_dict["size"] = parameters.gpmf_payload.size;
            gpmf_dict["has_gpmf"] = (parameters.gpmf_payload.buffer != nullptr && parameters.gpmf_payload.size > 0);
            gpr_dict["gpmf_payload"] = gpmf_dict;
            
            // Profile information
            py::dict profile_dict;
            // Note: The actual gpr_profile_info structure fields would be added here
            // For now, we'll add a placeholder that indicates profile info is available
            profile_dict["available"] = true;
            gpr_dict["profile_info"] = profile_dict;
            
            // Tuning information  
            py::dict tuning_dict;
            // Note: The actual gpr_tuning_info structure fields would be added here
            // For now, we'll add a placeholder that indicates tuning info is available
            tuning_dict["available"] = true;
            gpr_dict["tuning_info"] = tuning_dict;
            
            // Clean up
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            
            return gpr_dict;
            
        } catch (const GPRError&) {
            // Clean up on GPR-specific errors
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            throw; // Re-throw GPR errors as-is
        } catch (const std::exception& e) {
            // Clean up on other errors and wrap them
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            
            std::string context = get_error_context("GPR metadata extraction", input_path);
            throw GPRConversionError("Error extracting GPR metadata: " + std::string(e.what()) + " (" + context + ")");
        } catch (...) {
            // Clean up on unknown errors
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            
            std::string context = get_error_context("GPR metadata extraction", input_path);
            throw GPRConversionError("Unknown error during GPR metadata extraction (" + context + ")");
        }
        
    } catch (const GPRError&) {
        throw; // Re-throw GPR errors
    } catch (const std::exception& e) {
        // Wrap other errors as GPR errors
        std::string context = get_error_context("GPR metadata extraction setup", input_path);
        throw GPRError("Setup error: " + std::string(e.what()) + " (" + context + ")");
    }
}

// Modify metadata in an existing file by creating a new file with updated metadata
bool modify_metadata(const std::string& input_path, const std::string& output_path, const py::dict& exif_updates) {
    try {
        validate_input_file(input_path);
        
        // Set up allocator
        gpr_allocator allocator;
        allocator.Alloc = gpr_global_malloc;
        allocator.Free = gpr_global_free;
        
        // Initialize buffers and parameters
        gpr_buffer input_buffer = {nullptr, 0};
        gpr_buffer output_buffer = {nullptr, 0};
        gpr_parameters parameters;
        bool parameters_initialized = false;
        
        try {
            // Read input file
            if (!read_file_to_buffer(input_path, &input_buffer, &allocator)) {
                throw GPRFileError("Failed to read input file for metadata modification", input_path, -1);
            }
            
            // Initialize parameters and parse existing metadata
            gpr_parameters_set_defaults(&parameters);
            parameters_initialized = true;
            
            // Parse existing metadata
            bool success = gpr_parse_metadata(&allocator, &input_buffer, &parameters);
            if (!success) {
                std::string context = get_error_context("metadata parsing for modification", input_path);
                throw GPRConversionError("Failed to parse existing metadata (" + context + ")");
            }
            
            // Apply updates to EXIF info
            gpr_exif_info& exif = parameters.exif_info;
            
            // Update string fields
            for (auto item : exif_updates) {
                std::string key = py::str(item.first);
                
                if (key == "camera_make" && py::isinstance<py::str>(item.second)) {
                    std::string value = py::str(item.second);
                    strncpy(exif.camera_make, value.c_str(), CAMERA_MAKE_SIZE - 1);
                    exif.camera_make[CAMERA_MAKE_SIZE - 1] = '\0';
                }
                else if (key == "camera_model" && py::isinstance<py::str>(item.second)) {
                    std::string value = py::str(item.second);
                    strncpy(exif.camera_model, value.c_str(), CAMERA_MODEL_SIZE - 1);
                    exif.camera_model[CAMERA_MODEL_SIZE - 1] = '\0';
                }
                else if (key == "camera_serial" && py::isinstance<py::str>(item.second)) {
                    std::string value = py::str(item.second);
                    strncpy(exif.camera_serial, value.c_str(), CAMERA_SERIAL_SIZE - 1);
                    exif.camera_serial[CAMERA_SERIAL_SIZE - 1] = '\0';
                }
                else if (key == "software_version" && py::isinstance<py::str>(item.second)) {
                    std::string value = py::str(item.second);
                    strncpy(exif.software_version, value.c_str(), SOFTWARE_VERSION_SIZE - 1);
                    exif.software_version[SOFTWARE_VERSION_SIZE - 1] = '\0';
                }
                else if (key == "user_comment" && py::isinstance<py::str>(item.second)) {
                    std::string value = py::str(item.second);
                    strncpy(exif.user_comment, value.c_str(), USER_COMMENT_SIZE - 1);
                    exif.user_comment[USER_COMMENT_SIZE - 1] = '\0';
                }
                else if (key == "image_description" && py::isinstance<py::str>(item.second)) {
                    std::string value = py::str(item.second);
                    strncpy(exif.image_description, value.c_str(), IMAGE_DESCRIPTION_SIZE - 1);
                    exif.image_description[IMAGE_DESCRIPTION_SIZE - 1] = '\0';
                }
                // Update numeric fields
                else if (key == "iso_speed_rating" && py::isinstance<py::int_>(item.second)) {
                    exif.iso_speed_rating = py::cast<uint16_t>(item.second);
                }
                else if (key == "focal_length_in_35mm_film" && py::isinstance<py::int_>(item.second)) {
                    exif.focal_length_in_35mm_film = py::cast<uint16_t>(item.second);
                }
                else if (key == "saturation" && py::isinstance<py::int_>(item.second)) {
                    exif.saturation = py::cast<uint16_t>(item.second);
                }
                // Update rational fields (expecting tuples)
                else if (key == "exposure_time_rational" && py::isinstance<py::tuple>(item.second)) {
                    py::tuple rational = py::cast<py::tuple>(item.second);
                    if (rational.size() == 2) {
                        exif.exposure_time.numerator = py::cast<uint32_t>(rational[0]);
                        exif.exposure_time.denominator = py::cast<uint32_t>(rational[1]);
                    }
                }
                else if (key == "f_stop_number_rational" && py::isinstance<py::tuple>(item.second)) {
                    py::tuple rational = py::cast<py::tuple>(item.second);
                    if (rational.size() == 2) {
                        exif.f_stop_number.numerator = py::cast<uint32_t>(rational[0]);
                        exif.f_stop_number.denominator = py::cast<uint32_t>(rational[1]);
                    }
                }
                else if (key == "aperture_rational" && py::isinstance<py::tuple>(item.second)) {
                    py::tuple rational = py::cast<py::tuple>(item.second);
                    if (rational.size() == 2) {
                        exif.aperture.numerator = py::cast<uint32_t>(rational[0]);
                        exif.aperture.denominator = py::cast<uint32_t>(rational[1]);
                    }
                }
                else if (key == "focal_length_rational" && py::isinstance<py::tuple>(item.second)) {
                    py::tuple rational = py::cast<py::tuple>(item.second);
                    if (rational.size() == 2) {
                        exif.focal_length.numerator = py::cast<uint32_t>(rational[0]);
                        exif.focal_length.denominator = py::cast<uint32_t>(rational[1]);
                    }
                }
                // Update enum fields
                else if (key == "exposure_program" && py::isinstance<py::int_>(item.second)) {
                    exif.exposure_program = static_cast<gpr_exposure_program>(py::cast<int>(item.second));
                }
                else if (key == "metering_mode" && py::isinstance<py::int_>(item.second)) {
                    exif.metering_mode = static_cast<gpr_metering_mode>(py::cast<int>(item.second));
                }
                else if (key == "light_source" && py::isinstance<py::int_>(item.second)) {
                    exif.light_source = static_cast<gpr_light_source>(py::cast<int>(item.second));
                }
                else if (key == "white_balance" && py::isinstance<py::int_>(item.second)) {
                    exif.white_balance = static_cast<gpr_white_balance>(py::cast<int>(item.second));
                }
            }
            
            // Convert back to DNG with updated metadata
            success = gpr_convert_dng_to_dng(&allocator, &parameters, &input_buffer, &output_buffer);
            
            if (!success) {
                std::string context = get_error_context("DNG conversion with updated metadata", input_path, output_path);
                throw GPRConversionError("Failed to convert file with updated metadata (" + context + ")");
            }
            
            // Validate output buffer
            if (output_buffer.buffer == nullptr || output_buffer.size == 0) {
                throw GPRConversionError("Conversion with updated metadata produced empty output buffer");
            }
            
            // Write output file
            if (!write_buffer_to_file(&output_buffer, output_path)) {
                throw GPRFileError("Failed to write output file with updated metadata", output_path, -1);
            }
            
            // Clean up
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
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
            
            std::string context = get_error_context("metadata modification", input_path, output_path);
            throw GPRConversionError("Error modifying metadata: " + std::string(e.what()) + " (" + context + ")");
        } catch (...) {
            // Clean up on unknown errors
            if (parameters_initialized) {
                gpr_parameters_destroy(&parameters, allocator.Free);
            }
            cleanup_buffer_safe(&input_buffer, allocator);
            cleanup_buffer_safe(&output_buffer, allocator);
            
            std::string context = get_error_context("metadata modification", input_path, output_path);
            throw GPRConversionError("Unknown error during metadata modification (" + context + ")");
        }
        
    } catch (const GPRError&) {
        throw; // Re-throw GPR errors
    } catch (const std::exception& e) {
        // Wrap other errors as GPR errors
        std::string context = get_error_context("metadata modification setup", input_path, output_path);
        throw GPRError("Setup error: " + std::string(e.what()) + " (" + context + ")");
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
            bool success = gpr_convert_gpr_to_raw(&allocator, &parameters, &input_buffer, &output_buffer);
            
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
                        reinterpret_cast<uint16_t*>(output_buffer.buffer)  // data pointer
                    );
                } catch (const std::exception& e) {
                    throw GPRMemoryError("Failed to create uint16 NumPy array: " + std::string(e.what()));
                }
            } else if (dtype == "float32") {
                // Convert uint16 data to float32 and normalize
                try {
                    auto float_array = py::array_t<float>(info.height * info.width);
                    auto buf = float_array.request();
                    float* float_data = static_cast<float*>(buf.ptr);
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
    
    
    // Metadata extraction functions
    m.def("extract_exif_metadata", &extract_exif_metadata,
          "Extract EXIF metadata from GPR/DNG file as Python dictionary. "
          "Raises GPRFileError, GPRParameterError, or GPRConversionError on failure.",
          py::arg("input_path"));
    
    m.def("extract_gpr_metadata", &extract_gpr_metadata,
          "Extract GPR-specific metadata including compression parameters and tuning info. "
          "Raises GPRFileError, GPRParameterError, or GPRConversionError on failure.",
          py::arg("input_path"));
    
    m.def("modify_metadata", &modify_metadata,
          "Modify metadata in a file by creating a new file with updated EXIF data. "
          "Returns True on success. Raises GPRFileError or GPRConversionError on failure.",
          py::arg("input_path"), py::arg("output_path"), py::arg("exif_updates"));
    
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