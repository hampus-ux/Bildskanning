"""
Image Editor Module - Core image manipulation functions.
"""
from PIL import Image
from typing import Tuple, Optional


def resize_image(image: Image.Image, width: int, height: int) -> Image.Image:
    """Resize an image to the specified dimensions."""
    return image.resize((width, height), Image.Resampling.LANCZOS)


def resize_by_percentage(image: Image.Image, percentage: float) -> Image.Image:
    """Resize an image by a percentage (e.g., 50 for 50%)."""
    new_width = int(image.width * percentage / 100)
    new_height = int(image.height * percentage / 100)
    return resize_image(image, new_width, new_height)


def rotate_image(image: Image.Image, degrees: float) -> Image.Image:
    """Rotate an image by the specified degrees."""
    return image.rotate(degrees, expand=True)


def crop_image(
    image: Image.Image, left: int, top: int, right: int, bottom: int
) -> Image.Image:
    """Crop an image to the specified box coordinates."""
    return image.crop((left, top, right, bottom))


def adjust_brightness(image: Image.Image, factor: float) -> Image.Image:
    """
    Adjust image brightness.
    factor < 1.0 = darker, factor > 1.0 = brighter
    """
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def adjust_contrast(image: Image.Image, factor: float) -> Image.Image:
    """
    Adjust image contrast.
    factor < 1.0 = less contrast, factor > 1.0 = more contrast
    """
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def convert_to_grayscale(image: Image.Image) -> Image.Image:
    """Convert an image to grayscale."""
    return image.convert("L").convert("RGB")


def flip_horizontal(image: Image.Image) -> Image.Image:
    """Flip an image horizontally."""
    return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def flip_vertical(image: Image.Image) -> Image.Image:
    """Flip an image vertically."""
    return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
