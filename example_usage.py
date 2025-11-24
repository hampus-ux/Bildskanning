#!/usr/bin/env python3
"""
Example: Programmatic usage of image conversion
This demonstrates how to convert negative images to positive without the GUI.
"""

from PIL import Image, ImageOps, ImageEnhance
import os


def convert_negative_to_positive(input_path, output_path, brightness=1.0, contrast=1.0):
    """
    Convert a negative image to positive with optional adjustments.
    
    Args:
        input_path (str): Path to the negative image file
        output_path (str): Path where the positive image will be saved
        brightness (float): Brightness adjustment (1.0 = no change, >1.0 = brighter, <1.0 = darker)
        contrast (float): Contrast adjustment (1.0 = no change, >1.0 = more contrast, <1.0 = less contrast)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load the negative image
        print(f"Loading negative image: {input_path}")
        negative_image = Image.open(input_path)
        
        # Convert to RGB if needed (some images might be in different modes)
        if negative_image.mode != 'RGB':
            negative_image = negative_image.convert('RGB')
        
        # Invert the image (negative to positive)
        print("Converting negative to positive...")
        positive_image = ImageOps.invert(negative_image)
        
        # Apply brightness adjustment
        if brightness != 1.0:
            print(f"Applying brightness adjustment: {brightness}")
            enhancer = ImageEnhance.Brightness(positive_image)
            positive_image = enhancer.enhance(brightness)
        
        # Apply contrast adjustment
        if contrast != 1.0:
            print(f"Applying contrast adjustment: {contrast}")
            enhancer = ImageEnhance.Contrast(positive_image)
            positive_image = enhancer.enhance(contrast)
        
        # Save the result
        print(f"Saving positive image: {output_path}")
        positive_image.save(output_path, quality=95)
        
        print("✓ Conversion completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error during conversion: {e}")
        return False


def main():
    """Example usage."""
    # Example: Convert a negative image to positive
    input_file = "negative_scan.jpg"  # Replace with your negative image
    output_file = "positive_result.jpg"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Example input file '{input_file}' not found.")
        print("Please replace 'input_file' with the path to your negative image.")
        return
    
    # Convert with default settings
    convert_negative_to_positive(input_file, output_file)
    
    # Or convert with custom brightness and contrast
    # convert_negative_to_positive(input_file, output_file, brightness=1.2, contrast=1.1)


if __name__ == "__main__":
    main()
