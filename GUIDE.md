# Bildskanning Application - Användarvägledning

## Översikt över gränssnittet

Programmet har ett intuitivt gränssnitt uppdelat i två huvudområden:

### 1. Bildvisningsområde (vänster)
- Visar den aktuella bilden
- Automatisk storleksanpassning (max 600x600 pixlar)
- Behåller bildproportioner

### 2. Kontrollpanel (höger)
Innehåller följande knappar och kontroller:

#### Ladda Bild
- Öppnar en filväljare
- Stöder format: JPG, JPEG, PNG, BMP, TIFF, TIF

#### Konvertera till Positiv
- Inverterar färgerna (negativ → positiv)
- Knappen ändras till "Konvertera till Negativ" efter konvertering
- Växlar mellan negativ och positiv vy

#### Ljusstyrka
- Reglage: 0.5x till 2.0x
- Standardvärde: 1.0
- Klicka "Applicera" för att tillämpa ändringen
- Realtidsvisning av aktuellt värde

#### Kontrast
- Reglage: 0.5x till 2.0x
- Standardvärde: 1.0
- Klicka "Applicera" för att tillämpa ändringen
- Realtidsvisning av aktuellt värde

#### Återställ
- Återställer ljusstyrka och kontrast till standardvärden (1.0)
- Behåller negativ/positiv-läget

#### Spara Bild
- Sparar den aktuella bilden
- Välj format: JPG, PNG, TIFF
- Hög kvalitet (95% för JPEG)

### 3. Menyrad (överst)
**Fil-menyn:**
- Öppna bild... - Ladda en ny bild
- Spara bild... - Spara aktuell bild
- Avsluta - Stäng programmet

### 4. Statusrad (nederst)
- Visar aktuell status
- Bekräftar genomförda åtgärder
- Visar filnamn på laddade/sparade bilder

## Typiskt arbetsflöde

```
1. Starta programmet
   ↓
2. Ladda negativ bild (Ladda Bild eller Fil → Öppna bild)
   ↓
3. Konvertera till positiv (Konvertera till Positiv-knappen)
   ↓
4. Justera vid behov:
   - Dra ljusstyrkereglaget
   - Klicka "Applicera"
   - Dra kontrastreglaget
   - Klicka "Applicera"
   ↓
5. Spara resultat (Spara Bild eller Fil → Spara bild)
```

## Exempel på användning

### Scenario 1: Snabb konvertering
```
Ladda bild → Konvertera till Positiv → Spara
```

### Scenario 2: Konvertering med justeringar
```
Ladda bild → Konvertera till Positiv → 
Justera ljusstyrka (t.ex. 1.2) → Applicera →
Justera kontrast (t.ex. 1.1) → Applicera →
Spara
```

### Scenario 3: Experimentera med inställningar
```
Ladda bild → Konvertera till Positiv →
Justera ljusstyrka → Applicera →
Justera kontrast → Applicera →
(Om inte nöjd: Klicka Återställ och försök igen) →
Spara när nöjd
```

## Tips och tricks

1. **Förhandsgranskning**: Alla ändringar visas direkt i bildvisningsområdet

2. **Återställ ofta**: Använd "Återställ"-knappen för att börja om med justeringarna

3. **Spara kopior**: Spara olika versioner med olika ljusstyrka/kontrast för att jämföra

4. **Filformat**: 
   - Använd JPG för mindre filstorlek
   - Använd PNG för förlustfri komprimering
   - Använd TIFF för högsta kvalitet

5. **Batch-bearbetning**: För att konvertera många bilder, överväg att använda `example_usage.py` som mall för ett eget script

## Tekniska detaljer

### Bildbehandling
- **Negativ till positiv**: RGB-färginvertering med PIL ImageOps.invert()
- **Ljusstyrka**: PIL ImageEnhance.Brightness
- **Kontrast**: PIL ImageEnhance.Contrast

### Bildformat
- **Läsa**: JPG, JPEG, PNG, BMP, TIFF, TIF (och de flesta andra format som PIL stöder)
- **Skriva**: JPG (kvalitet 95%), PNG, TIFF

### Displaystorlek
- Bilder skalas automatiskt för visning
- Max 600x600 pixlar i gränssnittet
- Original upplösning bevaras vid sparande

## Felsökning

### Problem: "Ingen bild laddad"
- **Lösning**: Klicka på "Ladda Bild" och välj en giltig bildfil

### Problem: Bilden ser fel ut efter konvertering
- **Lösning**: 
  1. Kontrollera att originalbilden verkligen är en negativ
  2. Prova att justera ljusstyrka och kontrast
  3. Klicka "Konvertera till Negativ" för att växla tillbaka

### Problem: Kan inte spara bild
- **Lösning**: 
  1. Kontrollera att du har skrivrättigheter till målkatalogen
  2. Kontrollera att filnamnet är giltigt
  3. Försök med ett annat filformat

### Problem: Programmet startar inte
- **Lösning**:
  1. Kontrollera att Python 3.7+ är installerat
  2. Kontrollera att Pillow är installerat: `pip install -r requirements.txt`
  3. På Linux: Kontrollera att python3-tk är installerat: `sudo apt-get install python3-tk`

## Support och vidareutveckling

Detta är en MVP (Minimum Viable Product). Framtida förbättringar kan inkludera:
- Histogram-visning
- Fler justeringsmöjligheter (färgbalans, skärpa, etc.)
- Batch-bearbetning i gränssnittet
- Före/efter-jämförelse
- EXIF-databevarande
- Beskärning och rotering

För frågor eller förslag, öppna ett issue på GitHub-repositoryt.