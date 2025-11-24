#!/usr/bin/env python3
"""
Bildskanning - Batch Image Editor CLI
A tool for editing many images simultaneously in different groups.
"""
import argparse
from pathlib import Path
import sys

from src.image_group import ImageGroupManager
from src.batch_processor import BatchProcessor


def find_images(directory: Path, recursive: bool = False) -> list:
    """Find all image files in a directory."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    images = []
    
    if recursive:
        for ext in image_extensions:
            images.extend(directory.rglob(f"*{ext}"))
            images.extend(directory.rglob(f"*{ext.upper()}"))
    else:
        for ext in image_extensions:
            images.extend(directory.glob(f"*{ext}"))
            images.extend(directory.glob(f"*{ext.upper()}"))
    
    return sorted(set(images))


def main():
    parser = argparse.ArgumentParser(
        description="Bildskanning - Batch Image Editor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Resize all images in a folder to 800x600
  python main.py resize --input ./photos --output ./resized --width 800 --height 600

  # Resize by percentage
  python main.py resize --input ./photos --output ./resized --percentage 50

  # Rotate all images by 90 degrees
  python main.py rotate --input ./photos --output ./rotated --degrees 90

  # Convert to grayscale
  python main.py grayscale --input ./photos --output ./gray

  # Adjust brightness (1.5 = 50% brighter)
  python main.py brightness --input ./photos --output ./bright --factor 1.5

  # Adjust contrast
  python main.py contrast --input ./photos --output ./contrast --factor 1.3
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Resize command
    resize_parser = subparsers.add_parser("resize", help="Resize images")
    resize_parser.add_argument("--input", "-i", type=Path, required=True, help="Input directory")
    resize_parser.add_argument("--output", "-o", type=Path, required=True, help="Output directory")
    resize_parser.add_argument("--width", "-w", type=int, help="Target width in pixels")
    resize_parser.add_argument("--height", "-H", type=int, help="Target height in pixels")
    resize_parser.add_argument("--percentage", "-p", type=float, help="Resize by percentage")
    resize_parser.add_argument("--recursive", "-r", action="store_true", help="Search subdirectories")
    
    # Rotate command
    rotate_parser = subparsers.add_parser("rotate", help="Rotate images")
    rotate_parser.add_argument("--input", "-i", type=Path, required=True, help="Input directory")
    rotate_parser.add_argument("--output", "-o", type=Path, required=True, help="Output directory")
    rotate_parser.add_argument("--degrees", "-d", type=float, required=True, help="Rotation degrees")
    rotate_parser.add_argument("--recursive", "-r", action="store_true", help="Search subdirectories")
    
    # Grayscale command
    gray_parser = subparsers.add_parser("grayscale", help="Convert to grayscale")
    gray_parser.add_argument("--input", "-i", type=Path, required=True, help="Input directory")
    gray_parser.add_argument("--output", "-o", type=Path, required=True, help="Output directory")
    gray_parser.add_argument("--recursive", "-r", action="store_true", help="Search subdirectories")
    
    # Brightness command
    bright_parser = subparsers.add_parser("brightness", help="Adjust brightness")
    bright_parser.add_argument("--input", "-i", type=Path, required=True, help="Input directory")
    bright_parser.add_argument("--output", "-o", type=Path, required=True, help="Output directory")
    bright_parser.add_argument("--factor", "-f", type=float, required=True, 
                               help="Brightness factor (< 1 darker, > 1 brighter)")
    bright_parser.add_argument("--recursive", "-r", action="store_true", help="Search subdirectories")
    
    # Contrast command
    contrast_parser = subparsers.add_parser("contrast", help="Adjust contrast")
    contrast_parser.add_argument("--input", "-i", type=Path, required=True, help="Input directory")
    contrast_parser.add_argument("--output", "-o", type=Path, required=True, help="Output directory")
    contrast_parser.add_argument("--factor", "-f", type=float, required=True,
                                 help="Contrast factor (< 1 less contrast, > 1 more contrast)")
    contrast_parser.add_argument("--recursive", "-r", action="store_true", help="Search subdirectories")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Find images
    if not args.input.exists():
        print(f"Error: Input directory '{args.input}' does not exist")
        return 1
    
    images = find_images(args.input, getattr(args, 'recursive', False))
    if not images:
        print(f"No images found in '{args.input}'")
        return 1
    
    print(f"Found {len(images)} images")
    
    # Set up group manager and batch processor
    manager = ImageGroupManager()
    group = manager.create_group("batch")
    for img_path in images:
        group.add_image(img_path)
    
    processor = BatchProcessor(manager)
    
    # Execute command
    try:
        if args.command == "resize":
            if args.percentage:
                results = processor.resize_group_by_percentage("batch", args.percentage, args.output)
            elif args.width and args.height:
                results = processor.resize_group("batch", args.width, args.height, args.output)
            else:
                print("Error: Specify either --percentage or both --width and --height")
                return 1
        
        elif args.command == "rotate":
            results = processor.rotate_group("batch", args.degrees, args.output)
        
        elif args.command == "grayscale":
            results = processor.grayscale_group("batch", args.output)
        
        elif args.command == "brightness":
            results = processor.adjust_brightness_group("batch", args.factor, args.output)
        
        elif args.command == "contrast":
            results = processor.adjust_contrast_group("batch", args.factor, args.output)
        
        if len(results) > 0:
            print(f"Successfully processed {len(results)} images")
            print(f"Output saved to: {args.output}")
        else:
            print("No images were processed successfully")
            return 1
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
