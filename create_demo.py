#!/usr/bin/env python3
"""
Create a visual demonstration of the application's functionality
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import os

def create_demo_composite():
    """Create a composite image showing the workflow"""
    
    # Load test images
    negative = Image.open('test_negative.jpg')
    positive = Image.open('test_positive.jpg')
    
    # Create demonstration images
    # 1. Original negative
    # 2. Converted to positive
    # 3. Brightness adjusted
    # 4. Contrast adjusted
    
    # Convert negative to positive
    converted = ImageOps.invert(negative.convert('RGB'))
    
    # Brightness adjusted version
    enhancer = ImageEnhance.Brightness(converted)
    brightened = enhancer.enhance(1.5)
    
    # Contrast adjusted version
    enhancer = ImageEnhance.Contrast(converted)
    high_contrast = enhancer.enhance(1.8)
    
    # Create a composite image showing all steps
    width, height = negative.size
    margin = 20
    text_height = 40
    
    # Create canvas
    composite_width = (width + margin) * 4 + margin
    composite_height = height + text_height + margin * 2
    composite = Image.new('RGB', (composite_width, composite_height), 'white')
    
    # Paste images
    images = [
        (negative, "1. Negativ bild (original)"),
        (converted, "2. Konverterad till positiv"),
        (brightened, "3. Ljusstyrka +50%"),
        (high_contrast, "4. Kontrast +80%")
    ]
    
    draw = ImageDraw.Draw(composite)
    
    for i, (img, label) in enumerate(images):
        x = margin + i * (width + margin)
        y = margin + text_height
        composite.paste(img, (x, y))
        
        # Add label
        # Use default font since custom fonts might not be available
        draw.text((x + width//2, margin + 10), label, fill='black', anchor='mm')
    
    # Save composite
    composite.save('demo_workflow.jpg', quality=95)
    print("Created demo_workflow.jpg")
    
    return composite

def create_feature_showcase():
    """Create an image showcasing key features"""
    
    # Create a text-based feature list image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Title
    title = "Bildskanning - MVP Funktioner"
    y = 50
    draw.text((width//2, y), title, fill='black', anchor='mm')
    
    # Features
    features = [
        "",
        "✓ Grafiskt användargränssnitt (GUI)",
        "✓ Importera bilder (JPG, PNG, TIFF, BMP)",
        "✓ Konvertera negativ till positiv",
        "✓ Justera ljusstyrka (0.5x - 2.0x)",
        "✓ Justera kontrast (0.5x - 2.0x)",
        "✓ Visa bild i realtid",
        "✓ Återställ alla justeringar",
        "✓ Spara resultat",
        "",
        "Teknik:",
        "• Python 3",
        "• tkinter (GUI)",
        "• Pillow (bildbehandling)",
        "",
        "Användning: python3 image_editor.py"
    ]
    
    y = 120
    line_height = 30
    
    for feature in features:
        if feature:
            draw.text((80, y), feature, fill='black')
        y += line_height
    
    img.save('feature_showcase.jpg', quality=95)
    print("Created feature_showcase.jpg")
    
    return img

def main():
    print("Creating demonstration images...")
    print()
    
    create_demo_composite()
    create_feature_showcase()
    
    print()
    print("✓ Demonstration images created successfully!")
    print()
    print("Created files:")
    print("  - demo_workflow.jpg: Shows the image processing workflow")
    print("  - feature_showcase.jpg: Lists all features")

if __name__ == "__main__":
    main()
