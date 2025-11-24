"""Tests for image editor functions."""
import pytest
from PIL import Image
from src import image_editor


@pytest.fixture
def sample_image():
    """Create a simple test image."""
    return Image.new("RGB", (100, 100), color="red")


class TestImageEditor:
    """Tests for image editor module."""
    
    def test_resize_image(self, sample_image):
        """Test resizing an image."""
        result = image_editor.resize_image(sample_image, 50, 50)
        assert result.size == (50, 50)
    
    def test_resize_by_percentage(self, sample_image):
        """Test resizing by percentage."""
        result = image_editor.resize_by_percentage(sample_image, 50)
        assert result.size == (50, 50)
    
    def test_rotate_image(self, sample_image):
        """Test rotating an image."""
        result = image_editor.rotate_image(sample_image, 90)
        # After 90 degree rotation with expand, dimensions swap
        assert result.size == (100, 100)
    
    def test_crop_image(self, sample_image):
        """Test cropping an image."""
        result = image_editor.crop_image(sample_image, 10, 10, 60, 60)
        assert result.size == (50, 50)
    
    def test_adjust_brightness(self, sample_image):
        """Test brightness adjustment."""
        result = image_editor.adjust_brightness(sample_image, 1.5)
        assert result.size == sample_image.size
    
    def test_adjust_contrast(self, sample_image):
        """Test contrast adjustment."""
        result = image_editor.adjust_contrast(sample_image, 1.5)
        assert result.size == sample_image.size
    
    def test_convert_to_grayscale(self, sample_image):
        """Test grayscale conversion."""
        result = image_editor.convert_to_grayscale(sample_image)
        assert result.size == sample_image.size
        assert result.mode == "RGB"
    
    def test_flip_horizontal(self, sample_image):
        """Test horizontal flip."""
        result = image_editor.flip_horizontal(sample_image)
        assert result.size == sample_image.size
    
    def test_flip_vertical(self, sample_image):
        """Test vertical flip."""
        result = image_editor.flip_vertical(sample_image)
        assert result.size == sample_image.size
