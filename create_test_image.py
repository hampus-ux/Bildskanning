#!/usr/bin/env python3
"""
Create a test negative image for testing the image editor
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple test image with some colors and text
width, height = 400, 300
image = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(image)

# Draw some colored rectangles
draw.rectangle([50, 50, 150, 150], fill='red')
draw.rectangle([200, 50, 300, 150], fill='blue')
draw.rectangle([125, 150, 225, 250], fill='green')

# Add text
try:
    # Try to use a default font, but don't fail if it doesn't exist
    draw.text((150, 20), "Test Image", fill='black')
except:
    pass

# Save as positive
positive_path = 'test_positive.jpg'
image.save(positive_path)
print(f"Created positive test image: {positive_path}")

# Create negative version
from PIL import ImageOps
negative = ImageOps.invert(image)
negative_path = 'test_negative.jpg'
negative.save(negative_path)
print(f"Created negative test image: {negative_path}")

print("\nYou can now test the image editor with these images!")
