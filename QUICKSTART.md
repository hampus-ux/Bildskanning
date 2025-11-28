# 🚀 Quick Start Guide - Advanced Image Editor

## Snabbstart (30 sekunder)

### Steg 1: Öppna programmet
```powershell
.\run_editor.bat
```

Eller:
```powershell
python advanced_image_editor.py
```

### Steg 2: Ladda en bild
Klicka **"Load Image"** och välj din DSLR-scanning.

### Steg 3: Välj bildtyp
Högst upp i kontrollpanelen, välj:
- **Color Negative** - för färgnegativ
- **B&W Negative** - för svartvit negativ
- **Positive** - för redan utvecklade bilder

### Steg 4: Justera (automatiska defaults laddas)
Programmet laddar automatiskt optimala inställningar baserat på bildtyp!

### Steg 5: Spara
Klicka **"Save Image"** när du är nöjd.

---

## Vanliga Scenarion

### 📸 Scenario 1: Kodak Portra 400 Color Negative

```
1. Load Image → din_portra_scan.jpg
2. Image Type → "Color Negative" 
3. Film Profile → "Kodak Portra" (redan vald)
4. Justera efter behov:
   - Gamma: 1.05-1.15 (varmare)
   - Base Saturation: 1.0-1.2
5. Save Image
```

### ⚫ Scenario 2: Ilford HP5 Plus B&W Negative

```
1. Load Image → din_hp5_scan.jpg
2. Image Type → "B&W Negative"
3. Aktivera "Local Contrast Smoothing" (redan på)
4. Justera:
   - Smoothing Strength: 0.2-0.4
   - Toe/Shoulder: 0.3-0.4 (filmlik look)
5. Save Image
```

### 🖼️ Scenario 3: Redan utvecklat positivt foto

```
1. Load Image → ditt_foto.jpg
2. Image Type → "Positive"
3. Fine-tune:
   - Black/White Point (mycket små värden)
   - Gamma: 0.95-1.05
   - Final Tone Curve: "Soft" eller "Neutral"
5. Save Image
```

---

## Tips & Tricks

### ⚡ Snabba Förbättringar
- **Överexponerad?** → Öka Highlight Protection till 0.4-0.5
- **Underexponerad?** → Öka Shadow Recovery till 0.3-0.4
- **För gul/orange?** → Minska Neutral Balance Strength
- **För mättad?** → Minska Base Saturation till 0.9-1.0
- **För platt?** → Öka Midtone Contrast till 1.2-1.3

### 🎨 Kreativa Effekter
- **Vintage look**: Soft Final Curve + Base Saturation 0.8
- **Punchy colors**: Kodak Ektar profile + Base Saturation 1.3
- **Mjuk porträtt**: Portra-like curve + Shadow Smoothing 0.7
- **Klassisk svartvit**: B&W Negative + Smoothing 0.5 + Neutral curve

### 🔧 Felsökning
- **Bilden ser konstig ut?** → Klicka "Reset to Defaults"
- **Färgerna stämmer inte?** → Prova olika Film Profiles
- **För mycket brus?** → Aktivera Local Contrast Smoothing
- **Tappar detaljer?** → Minska Smoothing, öka Preserve Edges

---

## Kontroller - Snabbreferens

| Kontroll | Vad gör den? | Tips |
|----------|--------------|------|
| **Histogram Centering** | Centrerar exponering | Använd för mörka/ljusa scanningar |
| **Black/White Point** | Ställer in dynamisk range | Percentiler 0.5-2% / 98-99.5% |
| **Gamma** | Ljusstyrka (midtones) | 0.9 = mörkare, 1.1 = ljusare |
| **Toe/Shoulder** | Film-liknande kurvor | Höjre = mer filmisk look |
| **Color Balance** | Neutraliserar färgskift | Använd 0.5-0.7 för naturliga färger |
| **Smoothing** | Minskar grain/brus | Kan göra bilden suddig, använd måttligt |
| **Saturation** | Färgmättnad | 1.0-1.2 för naturligt, 1.3+ för punchy |
| **Protection** | Skyddar extremer | Öka vid clipping-problem |
| **Final Curve** | Slutlig look | Portra-like = varmt, Frontier = scannerstil |

---

## Keyboard Workflow (framtida)

_Tankar för tangentbordsgenvägar (ej implementerat än)_:
- `Ctrl+O` - Load Image
- `Ctrl+S` - Save Image  
- `Ctrl+R` - Reset to Defaults
- `Space` - Toggle preview
- `1-9` - Hoppa till respektive steg

---

## ❓ FAQ

**Q: Vilken bildtyp ska jag välja?**  
A: Om du skannat en negativ filmrulle → Color eller B&W Negative. Om det är ett redan utvecklat foto → Positive.

**Q: Varför blir färgerna konstiga på min color negative?**  
A: Färgnegativ har en orange filmbas. Programmet försöker ta bort den automatiskt, men du kan justera med Color Balance och Film Profile.

**Q: Kan jag spara mina inställningar?**  
A: Inte ännu - funktion planerad för framtida version.

**Q: Hur batch-processar jag många bilder?**  
A: Använd `example_usage.py` som mall och modifiera `batch_process_directory()` funktionen.

**Q: Programmet är långsamt?**  
A: Inaktivera "Local Contrast Smoothing" - bilateral filtering är beräkningstung.

---

## 📚 Mer Information

- **Fullständig guide**: [ADVANCED_EDITOR_GUIDE.md](ADVANCED_EDITOR_GUIDE.md)
- **Development info**: [DEVELOPMENT_SUMMARY.md](DEVELOPMENT_SUMMARY.md)
- **Programmatic usage**: [example_usage.py](example_usage.py)
- **Pipeline test**: [test_pipeline.py](test_pipeline.py)

---

**Lycka till med dina DSLR-scanningar! 📷**
