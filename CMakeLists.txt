# Minimum required CMake version
cmake_minimum_required(VERSION 3.15...3.28)

# Project name and version
project(
  python_gpr
  VERSION 0.1.0
  DESCRIPTION "Python bindings for the GPR (General Purpose Raw) library"
  LANGUAGES CXX C
)

# Require C++11 or later
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set C standard for GPR library
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Cross-platform compatibility settings
if(WIN32)
    # Windows-specific settings
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /EHsc")
    # Use static runtime to avoid dependency issues
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
elseif(APPLE)
    # macOS-specific settings
    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.9" CACHE STRING "Minimum macOS version")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")
elseif(UNIX)
    # Linux-specific settings
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIC")
endif()

# Find required packages - try standard approach first
find_package(pybind11 QUIET CONFIG)

# If standard approach fails, try alternative methods
if(NOT pybind11_FOUND)
    # Try to find it via Python
    execute_process(
        COMMAND python3 -c "import pybind11; print(pybind11.get_cmake_dir())"
        OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
    
    if(PYBIND11_CMAKE_DIR)
        set(pybind11_DIR ${PYBIND11_CMAKE_DIR})
        find_package(pybind11 QUIET CONFIG)
    endif()
endif()

if(NOT pybind11_FOUND)
    # Try to use pip installed pybind11
    execute_process(
        COMMAND python3 -m pybind11 --cmakedir
        OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
    
    if(PYBIND11_CMAKE_DIR)
        set(pybind11_DIR ${PYBIND11_CMAKE_DIR})
        find_package(pybind11 QUIET CONFIG)
    endif()
endif()

if(NOT pybind11_FOUND)
    message(FATAL_ERROR "Could not find pybind11. Please install it with: pip install pybind11")
endif()

message(STATUS "Found pybind11: ${pybind11_DIR}")

# Add GPR library subdirectory
# Set GPR build options to minimize dependencies
set(GPR_READING 1 CACHE BOOL "Enable GPR reading")
set(GPR_WRITING 1 CACHE BOOL "Enable GPR writing") 
set(GPR_JPEG_AVAILABLE 0 CACHE BOOL "Disable JPEG support for minimal build")

# Force position-independent code for static libraries
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Build GPR library
add_subdirectory(gpr EXCLUDE_FROM_ALL)

# Get GPR library targets
# The main libraries we need from GPR
set(GPR_LIBRARIES
    gpr_sdk
    dng_sdk
    common
    vc5_common
    xmp_core
    expat_lib
    md5_lib
)

# Check which optional libraries were actually built
# Only add them if they exist as targets
if(TARGET vc5_decoder)
    list(APPEND GPR_LIBRARIES vc5_decoder)
endif()

if(TARGET vc5_encoder)
    list(APPEND GPR_LIBRARIES vc5_encoder)
endif()

if(TARGET tiny_jpeg)
    list(APPEND GPR_LIBRARIES tiny_jpeg)
endif()

# Create pybind11 module
pybind11_add_module(_core
    src/python_gpr/_core_minimal.cpp
)

# Set properties for the module
target_compile_definitions(_core PRIVATE VERSION_INFO="${PROJECT_VERSION}")

# Link against GPR libraries
target_link_libraries(_core PRIVATE ${GPR_LIBRARIES})

# Include directories for GPR headers
target_include_directories(_core PRIVATE
    gpr/source/lib/gpr_sdk/public
    gpr/source/lib/gpr_sdk/private
    gpr/source/lib/dng_sdk
    gpr/source/lib/common/public
    gpr/source/lib/common/private
    gpr/source/lib/vc5_common
    gpr/source/lib/xmp_core
    gpr/source/lib/expat_lib
    gpr/source/lib/md5_lib
)

# Add optional include directories only if the targets exist
if(TARGET vc5_decoder)
    target_include_directories(_core PRIVATE gpr/source/lib/vc5_decoder)
endif()

if(TARGET vc5_encoder)
    target_include_directories(_core PRIVATE gpr/source/lib/vc5_encoder)
endif()

if(TARGET tiny_jpeg)
    target_include_directories(_core PRIVATE gpr/source/lib/tiny_jpeg)
endif()

# Install the module
install(TARGETS _core DESTINATION python_gpr)