# Sony ARW Support - Setup Guide

## Option 1: Install Microsoft Camera Codec Pack (Recommended)

1. Ladda ner **Microsoft Camera Codec Pack** från:
   https://www.microsoft.com/en-us/download/details.aspx?id=26829

2. Installera codec pack:
   - Kör installationsfilen
   - Starta om datorn efter installation

3. Öppna programmet och ladda ARW-filer direkt!

**Fördelar:**
- Fungerar direkt i programmet
- Snabb laddning
- Stöd för alla RAW-format (Canon, Nikon, Sony, etc.)
- Windows File Explorer visar thumbnails

## Option 2: Konvertera ARW till TIFF först

Om codec pack inte fungerar, använd konverteringsverktyget:

### Konvertera en fil:
```powershell
.venv\Scripts\python.exe convert_arw_to_tiff.py image.ARW
```

### Konvertera en mapp med ARW-filer:
```powershell
.venv\Scripts\python.exe convert_arw_to_tiff.py "F:\1. Raw\2025\November\2107\"
```

### Spara med eget namn:
```powershell
.venv\Scripts\python.exe convert_arw_to_tiff.py image.ARW output.tif
```

**Fördelar:**
- Fungerar alltid
- Ger dig TIFF-filer som är kompatibla överallt
- Bevarar full kvalitet

## Option 3: Använd Adobe Lightroom/Camera Raw

1. Öppna ARW i Lightroom eller Camera Raw
2. Exportera som TIFF (16-bit ProPhoto RGB för bästa kvalitet)
3. Ladda TIFF-filen i programmet

## Felsökning

**"Cannot open Sony ARW file" error:**
- Installera Microsoft Camera Codec Pack
- Eller använd convert_arw_to_tiff.py för batch-konvertering

**Bilden ser mörk ut:**
- ARW-filer har ofta lägre embedded preview
- Använd Color Negative mode om du scannar negativ
- Justera Black & White Point för rätt exponering

## Technical Details

Programmet försöker läsa ARW genom:
1. PIL med Windows WIC codec (kräver codec pack)
2. Embedded JPEG preview (finns i alla ARW-filer)

För full RAW-utveckling rekommenderas att konvertera till TIFF först med professionella verktyg som Lightroom, Capture One eller RawTherapee.
