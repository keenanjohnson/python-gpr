# python-gpr

This repo is an attempt to make a python compatible binding library to expose the functionality of the gpr library (C/C++) easily in python.

https://github.com/gopro/gpr

This is also somewhat my first experiement using the github copilot agent mode, so use with a bit of caution.

## Setup

This project uses the upstream GPR library as a git submodule. To clone and set up the repository:

```bash
# Clone the repository
git clone https://github.com/keenanjohnson/python-gpr.git
cd python-gpr

# Initialize and update the submodule
git submodule update --init --recursive
```

The GPR library will be available in the `gpr/` subdirectory after running the submodule update command.
