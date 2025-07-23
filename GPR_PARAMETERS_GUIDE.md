# GPR Parameters Guide

The `GPRParameters` class provides a Pythonic dictionary-like interface for configuring GPR (General Purpose Raw) encoding and decoding operations.

## Basic Usage

```python
from python_gpr.conversion import GPRParameters

# Create with default values
params = GPRParameters()

# Create with specific parameters
params = GPRParameters(
    input_width=1920,
    input_height=1080,
    fast_encoding=True,
    quality=10
)
```

## Dictionary-like Interface

The `GPRParameters` class supports standard dictionary operations:

```python
# Set parameters using dictionary syntax
params['input_width'] = 1920
params['input_height'] = 1080
params['fast_encoding'] = True

# Get parameters
width = params['input_width']
is_fast = params['fast_encoding']

# Check if parameter exists
if 'quality' in params:
    print(f"Quality: {params['quality']}")

# Iterate over parameters
for key in params:
    print(f"{key}: {params[key]}")

# Get all parameters as dict
param_dict = params.to_dict()
```

## Available Parameters

### Core GPR Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_width` | int | 0 | Width of input source in pixels |
| `input_height` | int | 0 | Height of input source in pixels |
| `input_pitch` | int | 0 | Pitch of input source in pixels |
| `fast_encoding` | bool | False | Enable fast encoding mode for quicker processing |
| `compute_md5sum` | bool | False | Compute MD5 checksum during processing |
| `enable_preview` | bool | False | Enable preview image generation |

### Legacy Parameters (for backwards compatibility)

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `quality` | int | 12 | 1-12 | Legacy quality parameter |
| `subband_count` | int | 4 | 1-8 | Legacy subband count parameter |
| `progressive` | bool | False | - | Legacy progressive encoding parameter |

## Parameter Validation

The class provides comprehensive validation:

### Type Validation
```python
params = GPRParameters()

# This works
params['input_width'] = 1920  # int
params['fast_encoding'] = True  # bool

# This raises TypeError
params['input_width'] = "1920"  # string instead of int
params['fast_encoding'] = "true"  # string instead of bool
```

### Value Validation
```python
params = GPRParameters()

# Valid ranges
params['quality'] = 8  # 1-12 is valid
params['subband_count'] = 4  # 1-8 is valid
params['input_width'] = 1920  # >= 0 is valid

# Invalid ranges raise ValueError
params['quality'] = 15  # > 12, raises ValueError
params['subband_count'] = 0  # < 1, raises ValueError  
params['input_width'] = -100  # < 0, raises ValueError
```

### Invalid Parameter Names
```python
# This raises KeyError
params['invalid_parameter'] = 42
```

## Advanced Usage

### Parameter Information
```python
# Get information about a specific parameter
info = GPRParameters.get_parameter_info('quality')
print(f"Type: {info['type']}, Default: {info['default']}")

# Get information about all parameters
all_params = GPRParameters.get_all_parameters()
for name, info in all_params.items():
    print(f"{name}: {info['type'].__name__} (default: {info['default']})")
```

### Copying and Updating
```python
# Create a copy
params1 = GPRParameters(quality=10, input_width=1920)
params2 = params1.copy()

# Update from another object or dictionary
params2.update({'quality': 8, 'fast_encoding': True})

# Update from another GPRParameters object
params3 = GPRParameters(input_height=1080)
params2.update(params3)
```

### Dictionary Methods
```python
params = GPRParameters(quality=10, input_width=1920)

# Standard dictionary methods
keys = list(params.keys())
values = list(params.values())
items = list(params.items())

# Get with default
quality = params.get('quality', 12)
invalid = params.get('invalid_param', 'default_value')

# Length
num_params = len(params)
```

## Backwards Compatibility

The class maintains backwards compatibility with property access:

```python
params = GPRParameters()

# Property access (legacy style)
params.quality = 10
params.subband_count = 6
params.progressive = True

# Mixed usage works
params['fast_encoding'] = True
print(f"Quality: {params.quality}, Fast: {params['fast_encoding']}")
```

## Integration with Conversion Functions

```python
from python_gpr.conversion import convert_gpr_to_dng, GPRParameters

# Create custom parameters
params = GPRParameters(
    input_width=1920,
    input_height=1080,
    fast_encoding=True,
    enable_preview=False
)

# Use with conversion functions
convert_gpr_to_dng('input.gpr', 'output.dng', parameters=params)
```

## Error Handling

The class provides clear error messages for common mistakes:

```python
try:
    params = GPRParameters(invalid_param=42)
except KeyError as e:
    print(f"Invalid parameter: {e}")

try:
    params['quality'] = "high"
except TypeError as e:
    print(f"Type error: {e}")

try:
    params['quality'] = 15
except ValueError as e:
    print(f"Value error: {e}")
```