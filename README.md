# Bildskanning - Negativ till Positiv Konvertering

Ett enkelt MVP-program för att konvertera och redigera negativa bilder från DSLR-skanning till positiva bilder.

## Funktioner

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

Kör programmet med:
```bash
python image_editor.py
```

eller (på vissa system):
```bash
python3 image_editor.py
```

### Arbetsflöde

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

Detta är en MVP (Minimum Viable Product) för att testa konceptet. Framtida förbättringar kan inkludera:

- Histogram-visning
- Färgbalans-justering
- Batch-bearbetning av flera bilder
- Rotering och beskärning
- Förinställningar för vanliga filmtyper
- Ångra/gör om-funktionalitet

## Licens

Detta projekt är fritt att använda och modifiera.

## Support

Vid problem eller frågor, öppna en issue i GitHub-repositoryt.
