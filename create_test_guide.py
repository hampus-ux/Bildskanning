#!/usr/bin/env python3
"""
Create a visual step-by-step guide for testing the application
"""
from PIL import Image, ImageDraw, ImageFont

def create_testing_guide():
    """Create a visual guide showing how to test the program"""
    
    # Create canvas
    width, height = 800, 900
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Title
    title = "Bildskanning - Så här testar du programmet"
    y = 30
    draw.text((width//2, y), title, fill='black', anchor='mm')
    
    # Steps
    steps = [
        "",
        "STEG 1: Installera beroenden",
        "  Kör i terminalen:",
        "  $ pip install -r requirements.txt",
        "  eller",
        "  $ pip3 install -r requirements.txt",
        "",
        "STEG 2: Skapa testbilder (valfritt)",
        "  $ python3 create_test_image.py",
        "  Detta skapar test_negative.jpg och test_positive.jpg",
        "",
        "STEG 3: Starta programmet",
        "  $ python image_editor.py",
        "  eller",
        "  $ python3 image_editor.py",
        "",
        "STEG 4: Använd programmet",
        "  1. Klicka på 'Ladda bild'",
        "  2. Välj en negativ bild (t.ex. test_negative.jpg)",
        "  3. Klicka på 'Konvertera till Positiv'",
        "  4. Justera ljusstyrka och kontrast med reglagen",
        "  5. Klicka på 'Spara bild' för att exportera",
        "",
        "ALTERNATIV: Använd quick_start.sh",
        "  $ ./quick_start.sh",
        "  Detta kör alla steg automatiskt!",
        "",
        "TESTA FUNKTIONALITETEN:",
        "  Kör automatiska tester:",
        "  $ python3 test_functionality.py",
    ]
    
    y = 80
    line_height = 26
    
    for step in steps:
        if step.startswith("STEG") or step.startswith("ALTERNATIV") or step.startswith("TESTA"):
            # Bold-ish effect for headers (draw twice with offset)
            draw.text((40, y), step, fill='darkblue')
            draw.text((41, y), step, fill='darkblue')
        elif step.startswith("  $"):
            # Command line
            draw.text((60, y), step, fill='darkgreen')
        else:
            draw.text((60, y), step, fill='black')
        y += line_height
    
    img.save('TESTGUIDE.jpg', quality=95)
    print("✓ Created TESTGUIDE.jpg")
    
    return img

if __name__ == "__main__":
    create_testing_guide()
