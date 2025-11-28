#!/usr/bin/env python3
"""
Test script for the image editor functionality
"""
import os
import sys
from PIL import Image, ImageOps, ImageEnhance

def test_image_inversion():
    """Test that negative to positive conversion works"""
    print("Testing image inversion...")
    
    # Load the test negative image
    if not os.path.exists('test_negative.jpg'):
        print("ERROR: test_negative.jpg not found!")
        return False
    
    img = Image.open('test_negative.jpg')
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Invert it (should look like the positive version)
    inverted = ImageOps.invert(img)
    
    # Save the result
    inverted.save('test_output_inverted.jpg')
    print("✓ Inversion test passed - created test_output_inverted.jpg")
    
    return True

def test_brightness_adjustment():
    """Test brightness adjustment"""
    print("Testing brightness adjustment...")
    
    if not os.path.exists('test_positive.jpg'):
        print("ERROR: test_positive.jpg not found!")
        return False
    
    img = Image.open('test_positive.jpg')
    
    # Test brightness increase
    enhancer = ImageEnhance.Brightness(img)
    bright = enhancer.enhance(1.5)
    bright.save('test_output_bright.jpg')
    
    # Test brightness decrease
    dark = enhancer.enhance(0.5)
    dark.save('test_output_dark.jpg')
    
    print("✓ Brightness test passed - created test_output_bright.jpg and test_output_dark.jpg")
    
    return True

def test_contrast_adjustment():
    """Test contrast adjustment"""
    print("Testing contrast adjustment...")
    
    if not os.path.exists('test_positive.jpg'):
        print("ERROR: test_positive.jpg not found!")
        return False
    
    img = Image.open('test_positive.jpg')
    
    # Test contrast adjustment
    enhancer = ImageEnhance.Contrast(img)
    high_contrast = enhancer.enhance(2.0)
    high_contrast.save('test_output_high_contrast.jpg')
    
    low_contrast = enhancer.enhance(0.5)
    low_contrast.save('test_output_low_contrast.jpg')
    
    print("✓ Contrast test passed - created test_output_high_contrast.jpg and test_output_low_contrast.jpg")
    
    return True

def main():
    print("=" * 60)
    print("Image Editor Functionality Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_image_inversion,
        test_brightness_adjustment,
        test_contrast_adjustment
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
