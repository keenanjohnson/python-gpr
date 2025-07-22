"""
Tests for python-gpr package

This module contains unit tests for the python-gpr bindings.
Currently tests the stub implementation and will be expanded
as actual GPR functionality is implemented.
"""

import pytest
import python_gpr as gpr


class TestStubImplementation:
    """Test the stub implementation before GPR library integration."""
    
    def test_package_imports(self):
        """Test that the package imports correctly."""
        assert hasattr(gpr, '__version__')
        assert hasattr(gpr, '__author__')
        assert hasattr(gpr, '__license__')
        
    def test_version_info(self):
        """Test version information."""
        assert gpr.__version__ == "0.1.0"
        assert gpr.__author__ == "Keenan Johnson"
        assert gpr.__license__ == "MIT OR Apache-2.0"
        
    def test_function_availability(self):
        """Test that main functions are available."""
        assert hasattr(gpr, 'convert_gpr_to_dng')
        assert hasattr(gpr, 'convert_dng_to_gpr')
        assert hasattr(gpr, 'convert_gpr_to_raw')
        assert hasattr(gpr, 'get_image_info')
        
    def test_stub_functions_raise_import_error(self):
        """Test that stub functions raise ImportError when native extension not available."""
        with pytest.raises(ImportError, match="Native GPR extension not available"):
            gpr.convert_gpr_to_dng("test.gpr", "test.dng")
            
        with pytest.raises(ImportError, match="Native GPR extension not available"):
            gpr.convert_dng_to_gpr("test.dng", "test.gpr")
            
        with pytest.raises(ImportError, match="Native GPR extension not available"):
            gpr.convert_gpr_to_raw("test.gpr", "test.raw")
            
        with pytest.raises(ImportError, match="Native GPR extension not available"):
            gpr.get_image_info("test.gpr")


class TestAPISignatures:
    """Test that function signatures match the expected API."""
    
    def test_convert_gpr_to_dng_signature(self):
        """Test convert_gpr_to_dng function signature."""
        import inspect
        sig = inspect.signature(gpr.convert_gpr_to_dng)
        params = list(sig.parameters.keys())
        assert params == ['input_path', 'output_path', 'parameters']
        
    def test_convert_dng_to_gpr_signature(self):
        """Test convert_dng_to_gpr function signature."""
        import inspect
        sig = inspect.signature(gpr.convert_dng_to_gpr)
        params = list(sig.parameters.keys())
        assert params == ['input_path', 'output_path', 'parameters']
        
    def test_convert_gpr_to_raw_signature(self):
        """Test convert_gpr_to_raw function signature."""
        import inspect
        sig = inspect.signature(gpr.convert_gpr_to_raw)
        params = list(sig.parameters.keys())
        assert params == ['input_path', 'output_path']
        
    def test_get_image_info_signature(self):
        """Test get_image_info function signature."""
        import inspect
        sig = inspect.signature(gpr.get_image_info)
        params = list(sig.parameters.keys())
        assert params == ['file_path']


class TestParameterValidation:
    """Test parameter validation and error handling."""
    
    def test_convert_functions_require_string_paths(self):
        """Test that conversion functions validate string paths."""
        # These should raise ImportError currently since native extension not available
        with pytest.raises(ImportError, match="Native GPR extension not available"):
            gpr.convert_gpr_to_dng("input.gpr", "output.dng")
            
        # Invalid types should still raise TypeError before reaching ImportError
        with pytest.raises(TypeError):
            gpr.convert_gpr_to_dng(123, "output.dng")
            
        with pytest.raises(TypeError):
            gpr.convert_gpr_to_dng("input.gpr", 456)


# Integration tests will be added here once GPR library is integrated
class TestGPRIntegration:
    """Tests for actual GPR library integration (when available)."""
    
    @pytest.mark.skip(reason="GPR library not yet integrated")
    def test_actual_conversion(self):
        """Test actual file conversion when GPR library is available."""
        # This will be implemented once GPR library is integrated
        pass
        
    @pytest.mark.skip(reason="GPR library not yet integrated") 
    def test_gpr_image_class(self):
        """Test GPRImage class when GPR library is available."""
        # This will be implemented once GPR library is integrated
        pass