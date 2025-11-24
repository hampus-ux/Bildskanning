"""
Image Group Module - Manages groups of images for batch processing.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Callable


@dataclass
class ImageGroup:
    """Represents a group of images that can be processed together."""
    name: str
    image_paths: List[Path] = field(default_factory=list)
    
    def add_image(self, path: Path) -> None:
        """Add an image path to the group."""
        if path not in self.image_paths:
            self.image_paths.append(path)
    
    def remove_image(self, path: Path) -> bool:
        """Remove an image path from the group. Returns True if removed."""
        if path in self.image_paths:
            self.image_paths.remove(path)
            return True
        return False
    
    def get_images(self) -> List[Path]:
        """Get all image paths in this group."""
        return self.image_paths.copy()
    
    def count(self) -> int:
        """Get the number of images in this group."""
        return len(self.image_paths)


class ImageGroupManager:
    """Manages multiple image groups."""
    
    def __init__(self):
        self._groups: Dict[str, ImageGroup] = {}
    
    def create_group(self, name: str) -> ImageGroup:
        """Create a new image group."""
        if name in self._groups:
            raise ValueError(f"Group '{name}' already exists")
        group = ImageGroup(name=name)
        self._groups[name] = group
        return group
    
    def get_group(self, name: str) -> Optional[ImageGroup]:
        """Get a group by name."""
        return self._groups.get(name)
    
    def delete_group(self, name: str) -> bool:
        """Delete a group. Returns True if deleted."""
        if name in self._groups:
            del self._groups[name]
            return True
        return False
    
    def list_groups(self) -> List[str]:
        """List all group names."""
        return list(self._groups.keys())
    
    def get_all_groups(self) -> List[ImageGroup]:
        """Get all groups."""
        return list(self._groups.values())
