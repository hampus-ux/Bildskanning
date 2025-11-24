"""Tests for image group module."""
import pytest
from pathlib import Path
from src.image_group import ImageGroup, ImageGroupManager


class TestImageGroup:
    """Tests for ImageGroup class."""
    
    def test_create_group(self):
        """Test creating a group."""
        group = ImageGroup(name="test")
        assert group.name == "test"
        assert group.count() == 0
    
    def test_add_image(self):
        """Test adding images to a group."""
        group = ImageGroup(name="test")
        path = Path("/tmp/test.jpg")
        group.add_image(path)
        assert group.count() == 1
        assert path in group.get_images()
    
    def test_add_duplicate_image(self):
        """Test that duplicate images are not added."""
        group = ImageGroup(name="test")
        path = Path("/tmp/test.jpg")
        group.add_image(path)
        group.add_image(path)
        assert group.count() == 1
    
    def test_remove_image(self):
        """Test removing an image from a group."""
        group = ImageGroup(name="test")
        path = Path("/tmp/test.jpg")
        group.add_image(path)
        assert group.remove_image(path) is True
        assert group.count() == 0
    
    def test_remove_nonexistent_image(self):
        """Test removing an image that doesn't exist."""
        group = ImageGroup(name="test")
        path = Path("/tmp/test.jpg")
        assert group.remove_image(path) is False


class TestImageGroupManager:
    """Tests for ImageGroupManager class."""
    
    def test_create_group(self):
        """Test creating a group via manager."""
        manager = ImageGroupManager()
        group = manager.create_group("test")
        assert group.name == "test"
        assert "test" in manager.list_groups()
    
    def test_create_duplicate_group(self):
        """Test that creating duplicate group raises error."""
        manager = ImageGroupManager()
        manager.create_group("test")
        with pytest.raises(ValueError):
            manager.create_group("test")
    
    def test_get_group(self):
        """Test getting a group by name."""
        manager = ImageGroupManager()
        manager.create_group("test")
        group = manager.get_group("test")
        assert group is not None
        assert group.name == "test"
    
    def test_get_nonexistent_group(self):
        """Test getting a group that doesn't exist."""
        manager = ImageGroupManager()
        group = manager.get_group("nonexistent")
        assert group is None
    
    def test_delete_group(self):
        """Test deleting a group."""
        manager = ImageGroupManager()
        manager.create_group("test")
        assert manager.delete_group("test") is True
        assert "test" not in manager.list_groups()
    
    def test_delete_nonexistent_group(self):
        """Test deleting a group that doesn't exist."""
        manager = ImageGroupManager()
        assert manager.delete_group("nonexistent") is False
    
    def test_list_groups(self):
        """Test listing all groups."""
        manager = ImageGroupManager()
        manager.create_group("group1")
        manager.create_group("group2")
        groups = manager.list_groups()
        assert "group1" in groups
        assert "group2" in groups
