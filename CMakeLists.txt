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

# Try to find pybind11 in different ways
find_package(pybind11 QUIET CONFIG)

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
    # Fallback: try to use pybind11 as a subdirectory if available
    message(WARNING "Could not find pybind11, trying manual setup")
    
    # Get pybind11 includes and setup manually
    execute_process(
        COMMAND python3 -c "import pybind11; print(pybind11.get_include())"
        OUTPUT_VARIABLE PYBIND11_INCLUDE_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
    
    if(PYBIND11_INCLUDE_DIR)
        message(STATUS "Found pybind11 include directory: ${PYBIND11_INCLUDE_DIR}")
        
        # Create a minimal pybind11 module setup
        find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
        
        # Create the module target manually
        add_library(_core MODULE src/python_gpr/_core.cpp)
        
        # Set properties for Python module
        set_target_properties(_core PROPERTIES
            PREFIX ""
            SUFFIX ".so"
        )
        
        # Add include directories
        target_include_directories(_core PRIVATE ${PYBIND11_INCLUDE_DIR} ${Python3_INCLUDE_DIRS})
        
        # Link Python libraries
        target_link_libraries(_core PRIVATE ${Python3_LIBRARIES})
        
        # Set compile definitions
        target_compile_definitions(_core PRIVATE VERSION_INFO="${PROJECT_VERSION}")
        
        # Set C++ standard
        target_compile_features(_core PRIVATE cxx_std_11)
        
    else()
        message(FATAL_ERROR "Could not find pybind11. Please install it with: pip install pybind11")
    endif()
else()
    message(STATUS "Found pybind11: ${pybind11_DIR}")
    
    # Create pybind11 module the standard way
    pybind11_add_module(_core src/python_gpr/_core.cpp)
    
    # Set properties for the module
    target_compile_definitions(_core PRIVATE VERSION_INFO="${PROJECT_VERSION}")
endif()

# Install the module
install(TARGETS _core DESTINATION python_gpr)