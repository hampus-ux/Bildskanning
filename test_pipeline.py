#!/usr/bin/env python3
"""
Demo script to test the advanced image editor pipeline without GUI
"""

import numpy as np
from PIL import Image
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from advanced_image_editor import (
    AutoEditParams, 
    ImageType, 
    apply_edit_pipeline,
    FilmProfile,
    ToneCurveProfile
)


def create_test_image(width=800, height=600):
    """Create a test gradient image"""
    # Create a gradient from dark to light
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Horizontal gradient
    for x in range(width):
        value = int(255 * x / width)
        img[:, x, :] = value
    
    return img


def test_color_negative_pipeline():
    """Test the color negative pipeline"""
    print("\n=== Testing Color Negative Pipeline ===")
    
    # Create test image
    test_img = create_test_image()
    
    # Get default params for color negative
    params = AutoEditParams.for_color_negative()
    
    # Process
    result = apply_edit_pipeline(test_img, params)
    
    print(f"✓ Input shape: {test_img.shape}")
    print(f"✓ Output shape: {result.shape}")
    print(f"✓ Input range: {test_img.min()}-{test_img.max()}")
    print(f"✓ Output range: {result.min()}-{result.max()}")
    print(f"✓ Film profile: {params.film_profile.value}")
    print(f"✓ Tone curve: {params.final_curve_profile.value}")
    
    return result


def test_bw_negative_pipeline():
    """Test the B&W negative pipeline"""
    print("\n=== Testing B&W Negative Pipeline ===")
    
    # Create test image
    test_img = create_test_image()
    
    # Get default params for B&W negative
    params = AutoEditParams.for_bw_negative()
    
    # Process
    result = apply_edit_pipeline(test_img, params)
    
    print(f"✓ Input shape: {test_img.shape}")
    print(f"✓ Output shape: {result.shape}")
    print(f"✓ Color balance enabled: {params.enable_color_balance}")
    print(f"✓ Saturation enabled: {params.enable_saturation}")
    print(f"✓ Smoothing enabled: {params.enable_smoothing}")
    
    return result


def test_positive_pipeline():
    """Test the positive image pipeline"""
    print("\n=== Testing Positive Image Pipeline ===")
    
    # Create test image
    test_img = create_test_image()
    
    # Get default params for positive
    params = AutoEditParams.for_positive()
    
    # Process
    result = apply_edit_pipeline(test_img, params)
    
    print(f"✓ Input shape: {test_img.shape}")
    print(f"✓ Output shape: {result.shape}")
    print(f"✓ Histogram centering: {params.enable_histogram_centering}")
    print(f"✓ Dynamic range: {params.enable_dynamic_range}")
    
    return result


def test_custom_params():
    """Test with custom parameters"""
    print("\n=== Testing Custom Parameters ===")
    
    test_img = create_test_image()
    
    # Create custom params
    params = AutoEditParams(
        image_type=ImageType.COLOR_NEGATIVE,
        enable_histogram_centering=True,
        target_midpoint=0.55,
        enable_bw_point=True,
        black_point_percentile=2.0,
        white_point_percentile=98.0,
        enable_midtone=True,
        gamma=1.2,
        enable_dynamic_range=True,
        toe_strength=0.5,
        shoulder_strength=0.4,
        enable_color_balance=True,
        film_profile=FilmProfile.KODAK_EKTAR,
        enable_saturation=True,
        base_saturation=1.3,
        enable_final_curve=True,
        final_curve_profile=ToneCurveProfile.PORTRA_LIKE
    )
    
    result = apply_edit_pipeline(test_img, params)
    
    print(f"✓ Custom gamma: {params.gamma}")
    print(f"✓ Custom saturation: {params.base_saturation}")
    print(f"✓ Custom film: {params.film_profile.value}")
    
    return result


def main():
    """Run all tests"""
    print("Advanced Image Editor - Pipeline Tests")
    print("=" * 50)
    
    try:
        # Test all three image types
        color_result = test_color_negative_pipeline()
        bw_result = test_bw_negative_pipeline()
        positive_result = test_positive_pipeline()
        custom_result = test_custom_params()
        
        print("\n" + "=" * 50)
        print("✅ All pipeline tests completed successfully!")
        print("=" * 50)
        print("\nThe GUI can be launched with:")
        print("  python advanced_image_editor.py")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
