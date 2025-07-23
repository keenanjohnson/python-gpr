#include <pybind11/pybind11.h>
#include <string>

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

PYBIND11_MODULE(_core, m) {
    m.doc() = "Minimal pybind11 hello world binding";
    
    // Basic hello world function
    m.def("hello_world", &hello_world, "A simple hello world function");
    
    // Simple math function
    m.def("add", &add, "Add two integers");
    
    // String manipulation function
    m.def("greet", &greet, "Greet someone by name");
    
    // Version information
    m.attr("__version__") = py::str(VERSION_INFO);
}