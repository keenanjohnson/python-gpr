cmake_minimum_required(VERSION 3.15...3.27)

project(python_gpr LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(pybind11 REQUIRED)

# Add GPR library as subdirectory when available
# For now, we'll create a stub that can be expanded later
set(GPR_DIR "${CMAKE_CURRENT_SOURCE_DIR}/gpr")
if(EXISTS "${GPR_DIR}/CMakeLists.txt")
    message(STATUS "Found GPR library at ${GPR_DIR}")
    add_subdirectory(${GPR_DIR})
    set(GPR_AVAILABLE TRUE)
else()
    message(WARNING "GPR library not found at ${GPR_DIR}. Building stub version.")
    set(GPR_AVAILABLE FALSE)
endif()

# Create the pybind11 module
pybind11_add_module(_gpr_binding 
    src/python_gpr/bindings.cpp
)

# Compile definitions
target_compile_definitions(_gpr_binding PRIVATE 
    VERSION_INFO="${EXAMPLE_VERSION_INFO}"
    GPR_AVAILABLE=$<BOOL:${GPR_AVAILABLE}>
)

# Link libraries
if(GPR_AVAILABLE)
    # When GPR library is available, link against it
    target_link_libraries(_gpr_binding PRIVATE gpr_sdk)
    target_include_directories(_gpr_binding PRIVATE 
        ${GPR_DIR}/source/lib/common/public
        ${GPR_DIR}/source/lib/gpr_sdk/public
    )
endif()

# Set properties for the Python module
set_target_properties(_gpr_binding PROPERTIES
    CXX_VISIBILITY_PRESET "hidden"
    VISIBILITY_INLINES_HIDDEN YES
)