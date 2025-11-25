# Bildskanning - Negativ till Positiv Konvertering

Ett program för att konvertera och redigera negativa bilder från DSLR-skanning till positiva bilder.

## Program

### 1. Enkel Bildredigerare (image_editor.py)
Ett enkelt MVP-program med grundläggande funktioner:
- Negativ till Positiv konvertering
- Ljusstyrka och kontrast-justeringar
- Tkinter-baserat gränssnitt

### 2. Avancerad Bildredigerare (advanced_image_editor.py) ⭐ NYTT
Professionell redigeringsmodul för DSLR-scanningar med:
- **3 bildtyper**: Color Negative, B&W Negative, Positive
- **9-stegs bearbetningspipeline**: 
  - Histogram centering
  - Black & white point scaling
  - Midtone correction (gamma)
  - Dynamic range expansion (toe/shoulder)
  - Color balance med filmprofilemulering
  - Local contrast smoothing (edge-preserving)
  - Density-modulated saturation
  - Highlight & shadow protection
  - Final tone curves (Frontier, Noritsu, Portra-like)
- **Filmprofilsemulering**: Kodak Portra, Ektar, Fuji Pro, Superia
- **PyQt6-baserat modernt gränssnitt**
- **Realtidsförhandsgranskning**

Se [ADVANCED_EDITOR_GUIDE.md](ADVANCED_EDITOR_GUIDE.md) för detaljerad dokumentation.

## Funktioner (Enkel version)

- **Importera bilder**: Stöd för vanliga bildformat (JPG, PNG, TIFF, BMP)
- **Negativ till Positiv konvertering**: Konvertera negativa bilder till positiva med ett knapptryck
- **Justeringar**: 
  - Ljusstyrka (0.5x - 2.0x)
  - Kontrast (0.5x - 2.0x)
- **Grafiskt gränssnitt**: Intuitivt och lättanvänt
- **Spara resultat**: Exportera redigerade bilder i olika format

## Installation

### Krav

- Python 3.7 eller senare
- pip (Python package manager)

### Steg

1. Klona eller ladda ner detta repository

2. Installera nödvändiga beroenden:
```bash
pip install -r requirements.txt
```

## Användning

### Enkel Redigerare
Kör programmet med:
```bash
python image_editor.py
```

### Avancerad Redigerare (Rekommenderas)
Kör den avancerade redigeraren med:
```bash
python advanced_image_editor.py
```

Eller använd snabbstartskripten:
```powershell
.\run_editor.bat
```

### Arbetsflöde (Enkel version)

1. **Ladda en bild**: Klicka på "Ladda bild" eller använd menyn Fil → Öppna bild
2. **Konvertera till positiv**: Klicka på "Konvertera till Positiv" för att invertera bilden från negativ till positiv
3. **Justera**: Använd reglagen för att justera ljusstyrka och kontrast
4. **Spara**: När du är nöjd, klicka på "Spara bild" för att exportera resultatet

### Kortkommandon

- Via menyn "Fil":
  - Öppna bild
  - Spara som
  - Avsluta

### Tips

- Du kan återställa alla justeringar genom att klicka på "Återställ"
- Bilden skalas automatiskt för att passa i fönstret
- Original-bilden påverkas aldrig - alla ändringar görs på en kopia

## Teknisk Information

### Arkitektur

Programmet är byggt med:
- **Python**: Huvudspråk
- **tkinter**: Grafiskt användargränssnitt (inkluderat i Python)
- **Pillow (PIL)**: Bildbehandling

### Filstruktur

```
Bildskanning/
├── image_editor.py      # Huvudprogrammet
├── requirements.txt     # Python-beroenden
└── README.md           # Denna fil
```

## Utveckling

### ✅ Implementerat (Advanced Editor)

Den avancerade redigeraren har nu:
- ✅ Professionell 9-stegs bearbetningspipeline
- ✅ Stöd för Color Negative, B&W Negative, och Positive
- ✅ Filmprofilsemulering (Kodak Portra, Ektar, Fuji Pro, Superia)
- ✅ Avancerad färgbalansering med filmbas-borttagning
- ✅ Dynamisk range expansion (toe/shoulder curves)
- ✅ Densitetsmodulerad mättnad
- ✅ Kantbevarande smoothing (bilateral filter)
- ✅ Högdager- och skuggskydd mot clipping
- ✅ Flera tonkurvaprofiler (Frontier, Noritsu, Portra-like)
- ✅ PyQt6-baserat modernt gränssnitt
- ✅ Realtidsförhandsgranskning

### 🔮 Framtida Förbättringar

MVP version kan utökas med:
- Batch-bearbetning med samma inställningar
- Spara/ladda förinställningar (presets)
- Histogram-visualisering
- Före/efter-jämförelsevyn
- RAW-filstöd (via rawpy)
- Selektiv maskering och lokal redigering
- Ångra/gör om-funktionalitet
- Lens profile correction
- Dust och scratch removal
- Grain emulation
- Advanced color grading tools

## 📚 Dokumentation

- **[QUICKSTART.md](QUICKSTART.md)** - Kom igång på 30 sekunder
- **[ADVANCED_EDITOR_GUIDE.md](ADVANCED_EDITOR_GUIDE.md)** - Fullständig användarguide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Teknisk arkitektur och implementation
- **[GUI_OVERVIEW.md](GUI_OVERVIEW.md)** - UI layout och interaktion
- **[COMMANDS.md](COMMANDS.md)** - Alla körkommandon och troubleshooting
- **[DEVELOPMENT_SUMMARY.md](DEVELOPMENT_SUMMARY.md)** - Utvecklingsöversikt

## 🧪 Testfiler

- `test_pipeline.py` - Testa bildbehandlingspipelinen
- `example_usage.py` - Programmatiska användningsexempel
- `test_gui.py` - GUI-tester
- `test_functionality.py` - Funktionalitetstester

## Licens

Detta projekt är fritt att använda och modifiera.

## Support

Vid problem eller frågor, öppna en issue i GitHub-repositoryt.
