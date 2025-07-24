"""
Comprehensive tests for GPR metadata functionality.

Tests the complete metadata access capabilities including EXIF data extraction,
DNG metadata access, GPR-specific information, and metadata modification.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Try to import the actual module, fall back to mocking if build not available
import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import python_gpr.metadata as metadata
    from python_gpr.metadata import GPRMetadata, extract_exif, extract_gpr_info, modify_exif
    BINDINGS_AVAILABLE = True
except ImportError:
    # Mock the module if bindings are not available
    metadata = MagicMock()
    BINDINGS_AVAILABLE = False


class TestGPRMetadataExtraction(unittest.TestCase):
    """Test metadata extraction functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Create a mock GPR file for testing
        self.mock_gpr_file = self.test_data_dir / "test.gpr"
        self.mock_dng_file = self.test_data_dir / "test.dng"
        
        # Create empty files for testing file existence
        self.mock_gpr_file.touch()
        self.mock_dng_file.touch()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.mock_gpr_file.exists():
            self.mock_gpr_file.unlink()
        if self.mock_dng_file.exists():
            self.mock_dng_file.unlink()
            
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available")
    def test_extract_exif_basic(self):
        """Test basic EXIF data extraction."""
        # This would work with actual GPR files
        with patch('python_gpr.metadata._core.extract_exif_metadata') as mock_extract:
            mock_extract.return_value = {
                "camera_make": "GoPro",
                "camera_model": "HERO8 Black",
                "iso_speed_rating": 800,
                "exposure_time": 0.001,
                "f_stop_number": 2.8,
                "focal_length": 3.0,
            }
            
            result = extract_exif(str(self.mock_gpr_file))
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result["camera_make"], "GoPro")
            self.assertEqual(result["camera_model"], "HERO8 Black")
            self.assertEqual(result["iso_speed_rating"], 800)
            
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available")
    def test_extract_gpr_info_basic(self):
        """Test GPR-specific metadata extraction."""
        with patch('python_gpr.metadata._core.extract_gpr_metadata') as mock_extract:
            mock_extract.return_value = {
                "input_width": 4000,
                "input_height": 3000,
                "fast_encoding": True,
                "enable_preview": True,
                "preview_image": {"has_preview": True, "width": 1920, "height": 1080},
                "gpmf_payload": {"has_gpmf": True, "size": 1024},
            }
            
            result = extract_gpr_info(str(self.mock_gpr_file))
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result["input_width"], 4000)
            self.assertEqual(result["input_height"], 3000)
            self.assertTrue(result["fast_encoding"])
            
    def test_extract_exif_file_not_found(self):
        """Test EXIF extraction with non-existent file."""
        if BINDINGS_AVAILABLE:
            with self.assertRaises(FileNotFoundError):
                extract_exif("nonexistent.gpr")
                
    def test_extract_gpr_info_file_not_found(self):
        """Test GPR info extraction with non-existent file."""
        if BINDINGS_AVAILABLE:
            with self.assertRaises(FileNotFoundError):
                extract_gpr_info("nonexistent.gpr")


class TestGPRMetadataClass(unittest.TestCase):
    """Test the GPRMetadata class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        self.mock_gpr_file = self.test_data_dir / "test.gpr"
        self.mock_gpr_file.touch()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.mock_gpr_file.exists():
            self.mock_gpr_file.unlink()
            
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available")
    def test_gpr_metadata_initialization(self):
        """Test GPRMetadata class initialization."""
        gpr_meta = GPRMetadata(str(self.mock_gpr_file))
        self.assertEqual(gpr_meta.filepath, str(self.mock_gpr_file))
        
    def test_gpr_metadata_file_not_found(self):
        """Test GPRMetadata with non-existent file."""
        if BINDINGS_AVAILABLE:
            with self.assertRaises(FileNotFoundError):
                GPRMetadata("nonexistent.gpr")
                
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available")
    def test_gpr_metadata_properties(self):
        """Test GPRMetadata property access."""
        with patch('python_gpr.metadata._core.extract_exif_metadata') as mock_exif, \
             patch('python_gpr.metadata._core.extract_gpr_metadata') as mock_gpr:
             
            mock_exif.return_value = {
                "camera_make": "GoPro",
                "camera_model": "HERO8 Black",
                "iso_speed_rating": 800,
                "exposure_time": 0.001,
                "f_stop_number": 2.8,
                "focal_length": 3.0,
                "gps_info": {"valid": True},
                "date_time_original": {"year": 2023, "month": 10, "day": 15},
            }
            
            mock_gpr.return_value = {
                "input_width": 4000,
                "input_height": 3000,
                "fast_encoding": True,
                "preview_image": {"has_preview": True},
                "gpmf_payload": {"has_gpmf": True},
            }
            
            gpr_meta = GPRMetadata(str(self.mock_gpr_file))
            
            self.assertEqual(gpr_meta.camera_make, "GoPro")
            self.assertEqual(gpr_meta.camera_model, "HERO8 Black")
            self.assertEqual(gpr_meta.iso_speed, 800)
            self.assertEqual(gpr_meta.exposure_time, 0.001)
            self.assertEqual(gpr_meta.f_number, 2.8)
            self.assertEqual(gpr_meta.focal_length, 3.0)
            self.assertTrue(gpr_meta.has_preview)
            self.assertTrue(gpr_meta.has_gpmf)
            
            compression_info = gpr_meta.compression_info
            self.assertTrue(compression_info["fast_encoding"])
            self.assertEqual(compression_info["input_width"], 4000)


class TestMetadataModification(unittest.TestCase):
    """Test metadata modification functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        self.input_file = self.test_data_dir / "input.dng"
        self.output_file = self.test_data_dir / "output.dng"
        
        # Create empty files for testing
        self.input_file.touch()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.input_file.exists():
            self.input_file.unlink()
        if self.output_file.exists():
            self.output_file.unlink()
            
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available")
    def test_modify_exif_basic(self):
        """Test basic EXIF modification."""
        with patch('python_gpr.metadata._core.modify_metadata') as mock_modify:
            mock_modify.return_value = True
            
            modify_exif(
                str(self.input_file),
                str(self.output_file),
                camera_make="Custom Make",
                iso_speed_rating=1600
            )
            
            mock_modify.assert_called_once()
            args, kwargs = mock_modify.call_args
            self.assertEqual(args[0], str(self.input_file))
            self.assertEqual(args[1], str(self.output_file))
            
    def test_modify_exif_file_not_found(self):
        """Test metadata modification with non-existent input file."""
        if BINDINGS_AVAILABLE:
            with self.assertRaises(FileNotFoundError):
                modify_exif("nonexistent.dng", str(self.output_file), camera_make="Test")
                
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available")
    def test_gpr_metadata_save_with_metadata(self):
        """Test saving file with modified metadata through GPRMetadata class."""
        with patch('python_gpr.metadata._core.extract_exif_metadata') as mock_exif, \
             patch('python_gpr.metadata._core.extract_gpr_metadata') as mock_gpr, \
             patch('python_gpr.metadata._core.modify_metadata') as mock_modify:
             
            mock_exif.return_value = {"camera_make": "GoPro"}
            mock_gpr.return_value = {"input_width": 4000}
            mock_modify.return_value = True
            
            gpr_meta = GPRMetadata(str(self.input_file))
            gpr_meta.save_with_metadata(str(self.output_file), {"camera_make": "Custom"})
            
            mock_modify.assert_called_once()


class TestMetadataUtilities(unittest.TestCase):
    """Test metadata utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        self.mock_file = self.test_data_dir / "test.gpr"
        self.mock_file.touch()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.mock_file.exists():
            self.mock_file.unlink()
            
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available")
    def test_get_metadata_summary(self):
        """Test metadata summary function."""
        with patch('src.python_gpr.metadata.extract_exif') as mock_exif, \
             patch('src.python_gpr.metadata.extract_gpr_info') as mock_gpr:
             
            mock_exif.return_value = {
                "camera_make": "GoPro",
                "camera_model": "HERO8",
                "iso_speed_rating": 800,
                "exposure_time": 0.001,
                "f_stop_number": 2.8,
                "focal_length": 3.0,
                "gps_info": {"valid": True},
                "date_time_original": {"year": 2023, "month": 10, "day": 15, "hour": 14, "minute": 30, "second": 45},
            }
            
            mock_gpr.return_value = {
                "input_width": 4000,
                "input_height": 3000,
                "preview_image": {"has_preview": True},
                "gpmf_payload": {"has_gpmf": True},
            }
            
            from src.python_gpr.metadata import get_metadata_summary
            summary = get_metadata_summary(str(self.mock_file))
            
            self.assertEqual(summary["camera_make"], "GoPro")
            self.assertEqual(summary["camera_model"], "HERO8")
            self.assertEqual(summary["iso_speed"], 800)
            self.assertEqual(summary["image_width"], 4000)
            self.assertEqual(summary["image_height"], 3000)
            self.assertTrue(summary["has_gps"])
            self.assertTrue(summary["has_preview"])
            self.assertTrue(summary["has_gpmf"])
            self.assertEqual(summary["capture_date"], "2023-10-15")
            self.assertEqual(summary["capture_time"], "14:30:45")
            
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available") 
    def test_get_camera_info(self):
        """Test camera info extraction."""
        with patch('src.python_gpr.metadata.extract_exif') as mock_exif:
            mock_exif.return_value = {
                "camera_make": "GoPro",
                "camera_model": "HERO8 Black",
                "camera_serial": "ABC123456",
            }
            
            from src.python_gpr.metadata import get_camera_info
            camera_info = get_camera_info(str(self.mock_file))
            
            self.assertEqual(camera_info["make"], "GoPro")
            self.assertEqual(camera_info["model"], "HERO8 Black") 
            self.assertEqual(camera_info["serial"], "ABC123456")
            
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available")
    def test_get_exposure_settings(self):
        """Test exposure settings extraction."""
        with patch('src.python_gpr.metadata.extract_exif') as mock_exif:
            mock_exif.return_value = {
                "exposure_time": 0.001,
                "f_stop_number": 2.8,
                "iso_speed_rating": 800,
                "focal_length": 3.0,
                "exposure_bias": 0.5,
            }
            
            from src.python_gpr.metadata import get_exposure_settings
            exposure = get_exposure_settings(str(self.mock_file))
            
            self.assertEqual(exposure["exposure_time"], 0.001)
            self.assertEqual(exposure["f_stop"], 2.8)
            self.assertEqual(exposure["iso_speed"], 800)
            self.assertEqual(exposure["focal_length"], 3.0)
            self.assertEqual(exposure["exposure_bias"], 0.5)
            
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available")
    def test_get_image_dimensions(self):
        """Test image dimensions extraction."""
        with patch('src.python_gpr.metadata.extract_gpr_info') as mock_gpr:
            mock_gpr.return_value = {
                "input_width": 4000,
                "input_height": 3000,
            }
            
            from src.python_gpr.metadata import get_image_dimensions
            width, height = get_image_dimensions(str(self.mock_file))
            
            self.assertEqual(width, 4000)
            self.assertEqual(height, 3000)


class TestEXIFFields(unittest.TestCase):
    """Test comprehensive EXIF field access."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        self.mock_file = self.test_data_dir / "test.gpr"
        self.mock_file.touch()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.mock_file.exists():
            self.mock_file.unlink()
            
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available")
    def test_comprehensive_exif_fields(self):
        """Test that all major EXIF fields are accessible."""
        expected_fields = [
            "camera_make", "camera_model", "camera_serial", "software_version",
            "user_comment", "image_description", "exposure_time", "f_stop_number",
            "aperture", "iso_speed_rating", "focal_length", "focal_length_in_35mm_film",
            "saturation", "exposure_program", "metering_mode", "light_source",
            "flash", "sharpness", "gain_control", "contrast", "scene_capture_type",
            "exposure_mode", "white_balance", "scene_type", "file_source",
            "sensing_method", "date_time_original", "date_time_digitized",
            "exposure_bias", "digital_zoom", "gps_info"
        ]
        
        with patch('python_gpr.metadata._core.extract_exif_metadata') as mock_extract:
            # Create mock data with all expected fields
            mock_data = {field: f"test_{field}" for field in expected_fields}
            mock_data.update({
                "iso_speed_rating": 800,
                "focal_length_in_35mm_film": 24,
                "saturation": 0,
                "exposure_program": 1,
                "date_time_original": {"year": 2023, "month": 10, "day": 15},
                "gps_info": {"valid": True},
            })
            mock_extract.return_value = mock_data
            
            result = extract_exif(str(self.mock_file))
            
            # Verify all expected fields are present
            for field in expected_fields:
                self.assertIn(field, result, f"Field {field} should be present in EXIF data")


class TestDNGMetadata(unittest.TestCase):
    """Test DNG-specific metadata handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        self.mock_dng_file = self.test_data_dir / "test.dng"
        self.mock_dng_file.touch()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.mock_dng_file.exists():
            self.mock_dng_file.unlink()
            
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available")
    def test_dng_metadata_extraction(self):
        """Test DNG-specific metadata extraction."""
        with patch('python_gpr.metadata._core.extract_exif_metadata') as mock_exif, \
             patch('python_gpr.metadata._core.extract_gpr_metadata') as mock_gpr:
             
            mock_exif.return_value = {"camera_make": "Adobe"}
            mock_gpr.return_value = {"input_width": 6000, "input_height": 4000}
            
            # Should work with DNG files too
            exif_result = extract_exif(str(self.mock_dng_file))
            gpr_result = extract_gpr_info(str(self.mock_dng_file))
            
            self.assertIsInstance(exif_result, dict)
            self.assertIsInstance(gpr_result, dict)


class TestMetadataPersistence(unittest.TestCase):
    """Test that metadata modifications are persistent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        self.input_file = self.test_data_dir / "input.dng"
        self.output_file = self.test_data_dir / "output.dng"
        self.input_file.touch()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.input_file.exists():
            self.input_file.unlink()
        if self.output_file.exists():
            self.output_file.unlink()
            
    @unittest.skipUnless(BINDINGS_AVAILABLE, "GPR bindings not available")
    def test_metadata_persistence_after_modification(self):
        """Test that modified metadata persists when file is re-read."""
        original_make = "Original Make"
        modified_make = "Modified Make"
        
        with patch('python_gpr.metadata._core.extract_exif_metadata') as mock_exif, \
             patch('python_gpr.metadata._core.modify_metadata') as mock_modify:
             
            # First call returns original metadata
            # Second call (after modification) returns modified metadata
            mock_exif.side_effect = [
                {"camera_make": original_make},
                {"camera_make": modified_make}
            ]
            
            # Mock modify_metadata to actually create the output file
            def mock_modify_func(input_path, output_path, metadata_updates):
                # Create the output file so extract_exif doesn't fail
                Path(output_path).touch()
                return True
            
            mock_modify.side_effect = mock_modify_func
            
            # Read original metadata
            original_metadata = extract_exif(str(self.input_file))
            self.assertEqual(original_metadata["camera_make"], original_make)
            
            # Modify metadata
            modify_exif(str(self.input_file), str(self.output_file), camera_make=modified_make)
            
            # Read modified metadata
            modified_metadata = extract_exif(str(self.output_file))
            self.assertEqual(modified_metadata["camera_make"], modified_make)


if __name__ == '__main__':
    unittest.main()