# Advanced Image Editor - Användningsguide

## Översikt

Den avancerade bildredigeraren är en professionell modul för bearbetning av DSLR-scanningar av:
- **Färgnegativ** (Color Negatives)
- **Svartvita negativ** (B&W Negatives)  
- **Positiva bilder** (Already developed photos)

## Att Köra Programmet

```powershell
python advanced_image_editor.py
```

## Funktioner

### Bildtyper

Programmet hanterar tre olika bildtyper med separata bearbetningspipelines:

1. **Color Negative**
   - Automatisk negativ-till-positiv konvertering
   - Filmbas färgborttagning (orange mask)
   - Färgbalansering optimerad för färgfilm
   - Filmprofilsemulering (Kodak Portra, Fuji, etc.)

2. **Black & White Negative**
   - Gråskalekonvertering
   - Negativ-till-positiv inversión
   - Ingen färgbalansering (inaktiverad automatiskt)
   - Optimerad för svartvit film

3. **Positive**
   - Ingen inversión
   - Mjukare histogram-anpassning
   - Valfri färgbalansering
   - Enklare bearbetning

### Bearbetningspipeline (9 steg)

#### 1. Histogram Centering
Centrerar exponeringen innan övriga justeringar.
- **Target Midpoint**: Var histogram-mitten ska ligga (0-1)
- **Detection Method**: mean eller median

#### 2. Black & White Point
Ställer in svart- och vitpunkter baserat på percentiler.
- **Black Point Percentile**: Percentil för svartpunkt (0-5%)
- **White Point Percentile**: Percentil för vitpunkt (95-100%)
- **Shadow Bias**: Justering av skuggor
- **Highlight Bias**: Justering av högdagrar

#### 3. Midtone Correction (Gamma)
Justerar ljusstyrka utan att påverka änpunkterna.
- **Gamma**: Gamma-värde (0.5-2.0)
- **Midtone Target**: Målvärde för mellantonerna
- **Restore Strength**: Hur starkt mellantonerna ska återställas

#### 4. Dynamic Range Expansion
Emulerar filmliknande rolloff i högdagrar och skuggor.
- **Toe Strength**: Styrka i skuggkurvan
- **Shoulder Strength**: Styrka i högdagerkurvan
- **Midtone Contrast**: Kontrast i mellantonerna

#### 5. Color Balance
Färgbalansering och filmprofilemulering (endast färgbilder).
- **Neutral Balance Strength**: Styrka för neutral gråbalansering
- **Film Profile**: Välj filmemulering
  - Neutral
  - Kodak Portra (varma toner)
  - Kodak Ektar (mättade färger)
  - Fuji Pro (kalla toner)
  - Fuji Superia (grön shift)

#### 6. Local Contrast Smoothing
Minskar hård mikrokontrast samtidigt som kanter bevaras.
- **Smoothing Strength**: Hur mycket smoothing ska appliceras
- **Shadow Smoothing**: Extra smoothing i skuggor
- **Highlight Smoothing**: Extra smoothing i högdagrar
- **Preserve Edges**: Kantbevarande styrka

#### 7. Saturation Adjustment
Applicerar mättnad baserat på densitet (färgfilmstil).
- **Base Saturation**: Basmättnad
- **Density Modulation**: Modulering baserat på densitet
- **Shadow Color Boost**: Förstärkning av färg i skuggor

#### 8. Highlight & Shadow Protection
Undviker clipping och återhämtar detaljer i extremerna.
- **Highlight Protection**: Skyddar högdagrar från clipping
- **Shadow Recovery**: Återhämtar detaljer i skuggor

#### 9. Final Tone Curve
Applicerar slutlig look.
- **Curve Profile**: Välj tonal profil
  - Neutral (rak kurva)
  - Frontier (Fuji Frontier scanner-stil)
  - Noritsu (Noritsu scanner-stil)
  - Portra-like (mjuka skuggor och högdagrar)
  - Soft (låg kontrast)

## Arbetsflöde

1. **Ladda en bild** - Klicka "Load Image" och välj din DSLR-scanning
2. **Välj bildtyp** - Color Negative, B&W Negative, eller Positive
3. **Justera parametrar** - Använd reglage i högerpanelen
4. **Förhandsgranska** - Bilden uppdateras i realtid
5. **Spara** - Klicka "Save Image" när du är nöjd

## Tips

- **Color Negatives**: Börja med Kodak Portra-profilen för varma, mjuka toner
- **B&W Negatives**: Aktivera Local Contrast Smoothing för jämnare toner
- **Positive Images**: Använd lägre värden för alla parametrar
- **Highlight Protection**: Öka vid överexponerade områden
- **Shadow Recovery**: Öka för underexponerade bilder

## Teknisk Implementation

### Stack
- **PyQt6**: GUI framework
- **NumPy**: Numerisk beräkning
- **OpenCV (cv2)**: Bildbehandling
- **Pillow (PIL)**: Bildladdning och sparning

### Pipeline
Alla bilder konverteras till float32 [0, 1] för bearbetning och sedan tillbaka till uint8 [0, 255] för sparning.

### Modulär Design
- `AutoEditParams`: Parameterklass med tre fabriksmetoder
- `apply_edit_pipeline()`: Huvudpipeline-funktion
- `ImageEditorWindow`: PyQt6-baserad UI

## Förbättringar från Ursprungligt Program

Den nya modulen erbjuder:
- ✅ Professionell 9-stegs bearbetningspipeline
- ✅ Stöd för tre olika bildtyper med anpassade pipelines
- ✅ Filmprofilemulering (Kodak, Fuji)
- ✅ Avancerad färgbalansering och filmbas-borttagning
- ✅ Dynamisk områdesexpansion med toe/shoulder-kurvor
- ✅ Densitetsmodulerad mättnad (filmliknande)
- ✅ Kantbevarande smoothing
- ✅ Högdagrar- och skuggskydd
- ✅ Flera tonkurvaprofiler
- ✅ Modern PyQt6-baserat gränssnitt
- ✅ Realtidsförhandsgranskning

## Framtida Utbyggnad

Potentiella förbättringar:
- Batch-bearbetning av flera bilder
- Förinställningar (presets) som kan sparas/laddas
- Histogram-visualisering
- Före/efter-jämförelse
- RAW-filstöd
- Avancerad maskering för selektiv redigering
