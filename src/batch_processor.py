"""
Batch Processor Module - Applies edits to groups of images.
"""
from pathlib import Path
from typing import List, Callable, Optional
from PIL import Image

from .image_group import ImageGroup, ImageGroupManager
from . import image_editor


class BatchProcessor:
    """Processes batch image operations on groups."""
    
    def __init__(self, group_manager: ImageGroupManager):
        self.group_manager = group_manager
    
    def process_group(
        self,
        group_name: str,
        operation: Callable[[Image.Image], Image.Image],
        output_dir: Path,
        prefix: str = "",
        suffix: str = "_edited"
    ) -> List[Path]:
        """
        Apply an operation to all images in a group.
        
        Args:
            group_name: Name of the group to process
            operation: Function that takes an Image and returns an Image
            output_dir: Directory to save processed images
            prefix: Prefix to add to output filenames
            suffix: Suffix to add to output filenames (before extension)
        
        Returns:
            List of paths to the processed images
        """
        group = self.group_manager.get_group(group_name)
        if not group:
            raise ValueError(f"Group '{group_name}' not found")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        processed_paths = []
        
        for image_path in group.get_images():
            try:
                with Image.open(image_path) as img:
                    processed = operation(img)
                    
                    # Generate output filename
                    stem = image_path.stem
                    ext = image_path.suffix
                    output_name = f"{prefix}{stem}{suffix}{ext}"
                    output_path = output_dir / output_name
                    
                    processed.save(output_path)
                    processed_paths.append(output_path)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
        
        return processed_paths
    
    def resize_group(
        self,
        group_name: str,
        width: int,
        height: int,
        output_dir: Path
    ) -> List[Path]:
        """Resize all images in a group to specified dimensions."""
        return self.process_group(
            group_name,
            lambda img: image_editor.resize_image(img, width, height),
            output_dir,
            suffix="_resized"
        )
    
    def resize_group_by_percentage(
        self,
        group_name: str,
        percentage: float,
        output_dir: Path
    ) -> List[Path]:
        """Resize all images in a group by percentage."""
        return self.process_group(
            group_name,
            lambda img: image_editor.resize_by_percentage(img, percentage),
            output_dir,
            suffix="_resized"
        )
    
    def rotate_group(
        self,
        group_name: str,
        degrees: float,
        output_dir: Path
    ) -> List[Path]:
        """Rotate all images in a group."""
        return self.process_group(
            group_name,
            lambda img: image_editor.rotate_image(img, degrees),
            output_dir,
            suffix="_rotated"
        )
    
    def grayscale_group(
        self,
        group_name: str,
        output_dir: Path
    ) -> List[Path]:
        """Convert all images in a group to grayscale."""
        return self.process_group(
            group_name,
            image_editor.convert_to_grayscale,
            output_dir,
            suffix="_grayscale"
        )
    
    def adjust_brightness_group(
        self,
        group_name: str,
        factor: float,
        output_dir: Path
    ) -> List[Path]:
        """Adjust brightness of all images in a group."""
        return self.process_group(
            group_name,
            lambda img: image_editor.adjust_brightness(img, factor),
            output_dir,
            suffix="_brightness"
        )
    
    def adjust_contrast_group(
        self,
        group_name: str,
        factor: float,
        output_dir: Path
    ) -> List[Path]:
        """Adjust contrast of all images in a group."""
        return self.process_group(
            group_name,
            lambda img: image_editor.adjust_contrast(img, factor),
            output_dir,
            suffix="_contrast"
        )
