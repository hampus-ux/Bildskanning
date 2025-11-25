#!/usr/bin/env python3
"""
Simple ARW to TIFF converter using PIL with embedded preview
For Sony A7RIII and other cameras
"""

from PIL import Image
from pathlib import Path
import sys

def convert_arw_to_tiff(arw_path: str, output_path: str = None):
    """
    Convert ARW file to TIFF using embedded preview
    
    Args:
        arw_path: Path to ARW file
        output_path: Optional output path (defaults to same name with .tif)
    """
    arw_file = Path(arw_path)
    
    if not arw_file.exists():
        print(f"Error: File not found: {arw_path}")
        return False
    
    if output_path is None:
        output_path = arw_file.with_suffix('.tif')
    
    try:
        print(f"Loading: {arw_file.name}...")
        
        # Open ARW file
        with Image.open(arw_path) as img:
            # Try to get the largest embedded preview
            # ARW files contain multiple previews
            if hasattr(img, 'n_frames'):
                print(f"  Found {img.n_frames} embedded images")
                # Frame 0 is usually the largest preview
                img.seek(0)
            
            # Convert to RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as TIFF
            print(f"Saving: {output_path}...")
            img.save(output_path, compression='lzw')
            
            size = img.size
            print(f"✓ Converted successfully!")
            print(f"  Resolution: {size[0]}x{size[1]}")
            print(f"  Output: {output_path}")
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("\nNote: This requires Microsoft Camera Codec Pack")
        print("Download from: https://www.microsoft.com/en-us/download/details.aspx?id=26829")
        return False


def batch_convert(directory: str):
    """Convert all ARW files in a directory"""
    dir_path = Path(directory)
    arw_files = list(dir_path.glob("*.ARW")) + list(dir_path.glob("*.arw"))
    
    if not arw_files:
        print(f"No ARW files found in: {directory}")
        return
    
    print(f"Found {len(arw_files)} ARW files\n")
    
    success = 0
    failed = 0
    
    for arw_file in arw_files:
        if convert_arw_to_tiff(str(arw_file)):
            success += 1
        else:
            failed += 1
        print()
    
    print(f"\nResults: {success} converted, {failed} failed")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ARW to TIFF Converter")
        print("\nUsage:")
        print("  Single file:  python convert_arw_to_tiff.py image.ARW")
        print("  Single file:  python convert_arw_to_tiff.py image.ARW output.tif")
        print("  Batch:        python convert_arw_to_tiff.py folder/")
        print("\nNote: Requires Microsoft Camera Codec Pack installed")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if Path(input_path).is_dir():
        batch_convert(input_path)
    else:
        output = sys.argv[2] if len(sys.argv) > 2 else None
        convert_arw_to_tiff(input_path, output)
