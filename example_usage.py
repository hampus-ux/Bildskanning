#!/usr/bin/env python3
"""
Example: How to use the Advanced Image Editor programmatically
"""

from advanced_image_editor import (
    AutoEditParams, 
    ImageType, 
    FilmProfile,
    ToneCurveProfile,
    apply_edit_pipeline
)
from PIL import Image
import numpy as np
from pathlib import Path


def process_color_negative(input_path: str, output_path: str):
    """Process a color negative scan"""
    # Load image
    pil_img = Image.open(input_path)
    if pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')
    img_array = np.array(pil_img)
    
    # Get default parameters for color negatives
    params = AutoEditParams.for_color_negative()
    
    # Optional: customize parameters
    params.film_profile = FilmProfile.KODAK_PORTRA
    params.base_saturation = 1.15
    params.gamma = 1.12
    
    # Process
    result = apply_edit_pipeline(img_array, params)
    
    # Save
    Image.fromarray(result).save(output_path)
    print(f"✓ Saved to {output_path}")


def process_bw_negative(input_path: str, output_path: str):
    """Process a B&W negative scan"""
    # Load image
    pil_img = Image.open(input_path).convert('RGB')
    img_array = np.array(pil_img)
    
    # Get default parameters for B&W negatives
    params = AutoEditParams.for_bw_negative()
    
    # Optional: customize
    params.smoothing_strength = 0.4
    params.midtone_contrast = 1.15
    
    # Process
    result = apply_edit_pipeline(img_array, params)
    
    # Save
    Image.fromarray(result).save(output_path)
    print(f"✓ Saved to {output_path}")


def process_positive_with_custom_settings(input_path: str, output_path: str):
    """Process a positive image with custom settings"""
    # Load
    pil_img = Image.open(input_path).convert('RGB')
    img_array = np.array(pil_img)
    
    # Start with positive defaults
    params = AutoEditParams.for_positive()
    
    # Customize for this specific image
    params.enable_midtone = True
    params.gamma = 0.95  # Slightly darken
    params.enable_saturation = True
    params.base_saturation = 1.1
    params.enable_final_curve = True
    params.final_curve_profile = ToneCurveProfile.SOFT
    
    # Process
    result = apply_edit_pipeline(img_array, params)
    
    # Save
    Image.fromarray(result).save(output_path)
    print(f"✓ Saved to {output_path}")


def batch_process_directory(input_dir: str, output_dir: str, image_type: ImageType):
    """Process all images in a directory"""
    from pathlib import Path
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Get appropriate defaults
    if image_type == ImageType.COLOR_NEGATIVE:
        params = AutoEditParams.for_color_negative()
    elif image_type == ImageType.BW_NEGATIVE:
        params = AutoEditParams.for_bw_negative()
    else:
        params = AutoEditParams.for_positive()
    
    # Process all images
    image_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}
    image_files = [f for f in input_path.iterdir() 
                   if f.suffix.lower() in image_extensions]
    
    print(f"Processing {len(image_files)} images as {image_type.value}...")
    
    for img_file in image_files:
        print(f"Processing {img_file.name}...", end=" ")
        
        # Load
        pil_img = Image.open(img_file)
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')
        img_array = np.array(pil_img)
        
        # Process
        result = apply_edit_pipeline(img_array, params)
        
        # Save
        output_file = output_path / f"processed_{img_file.name}"
        Image.fromarray(result).save(output_file)
        print(f"✓ → {output_file.name}")
    
    print(f"\n✅ Processed {len(image_files)} images")


# Example usage
if __name__ == "__main__":
    print("Advanced Image Editor - Programmatic Usage Examples")
    print("=" * 60)
    
    # Check if test images exist
    if Path("test_negative.jpg").exists():
        print("\n1. Processing color negative...")
        process_color_negative("test_negative.jpg", "output_color.jpg")
    
    if Path("test_positive.jpg").exists():
        print("\n2. Processing positive image...")
        process_positive_with_custom_settings("test_positive.jpg", "output_positive.jpg")
    
    print("\n" + "=" * 60)
    print("For GUI interface, run:")
    print("  python advanced_image_editor.py")
    print("=" * 60)
