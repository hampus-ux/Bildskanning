# Snabbstart - Bildskanning

## Installera och kör på 5 minuter

### Steg 1: Förberedelser (Linux/Ubuntu)
```bash
# Installera system-beroenden
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-tk

# Navigera till projektkatalogen
cd Bildskanning
```

### Steg 2: Installera Python-paket
```bash
pip install -r requirements.txt
```

### Steg 3: Starta programmet
```bash
python bildskanning.py
```

## Första användningen

1. **Klicka "Ladda Bild"** (eller tryck Fil → Öppna bild)
2. **Välj din negativa bild** från DSLR-skanning
3. **Klicka "Konvertera till Positiv"** 
4. **Klicka "Spara Bild"** för att spara resultatet

Klart! 🎉

## Vanliga kommandon

### Starta programmet
```bash
python bildskanning.py
```

### Programmatisk användning (utan GUI)
```bash
python example_usage.py
```

### Redigera example_usage.py för batch-konvertering
```python
# Öppna example_usage.py och ändra:
input_file = "din_negativa_bild.jpg"
output_file = "resultat_positiv.jpg"

# Kör sedan:
python example_usage.py
```

## Supported filformat

**Import (Läsa):**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tif, .tiff)
- Och de flesta andra format som PIL stöder

**Export (Spara):**
- JPEG (.jpg, .jpeg) - Kvalitet 95%
- PNG (.png) - Förlustfri
- TIFF (.tif, .tiff) - Högsta kvalitet

## Felsökning snabbguide

**Problem:** Programmet startar inte
```bash
# Kontrollera Python-version
python3 --version  # Ska vara 3.7 eller senare

# Installera om beroenden
pip install --upgrade -r requirements.txt

# Linux: Installera tkinter
sudo apt-get install python3-tk
```

**Problem:** "Ingen modul named 'PIL'"
```bash
pip install Pillow
```

**Problem:** Kan inte öppna bild
- Kontrollera att filen är en giltig bildfil
- Prova att öppna bilden i en annan bildvisare först
- Kontrollera filrättigheter

## Exempel på arbetsflöde

### Grundläggande konvertering
```
Start → Ladda Bild → Konvertera till Positiv → Spara
```

### Med justeringar
```
Start → Ladda Bild → Konvertera till Positiv → 
Justera Ljusstyrka → Applicera → 
Justera Kontrast → Applicera → 
Spara
```

## Nästa steg

- Läs hela README-filen för mer detaljer
- Läs GUIDE.md för utförlig användarvägledning
- Utforska example_usage.py för programmatisk användning
- Se UI_LAYOUT.txt för gränssnittsbeskrivning

## Support

För frågor eller problem:
1. Läs README och GUIDE.md
2. Kontrollera felsökningssektionen ovan
3. Öppna ett issue på GitHub

---

**Lycka till med din bildkonvertering!** 📸✨
