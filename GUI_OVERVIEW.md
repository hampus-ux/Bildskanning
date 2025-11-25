# Advanced Image Editor - GUI Overview

## Fönsterlayout

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ Advanced Image Editor - DSLR Scan Processing                          [_][□][X]│
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌──────────────────────────────────┬────────────────────────────────────┐   │
│  │ [Load Image]  [Save Image]       │ Image Type: [Color Negative ▼]    │   │
│  ├──────────────────────────────────┤ [Apply to Current] [Reset Defaults]│   │
│  │                                  ├────────────────────────────────────┤   │
│  │                                  │ ╔═══════════════════════════════╗ │   │
│  │                                  │ ║ ☑ 1. Histogram Centering      ║ │   │
│  │                                  │ ╠═══════════════════════════════╣ │   │
│  │         IMAGE PREVIEW            │ ║ Target Midpoint:              ║ │   │
│  │                                  │ ║ [━━━━━━●━━━━] 0.50            ║ │   │
│  │         (600 x 400+)             │ ║                               ║ │   │
│  │                                  │ ║ Detection Method:             ║ │   │
│  │    Displays processed image      │ ║ [median ▼]                    ║ │   │
│  │    Updates in real-time          │ ╚═══════════════════════════════╝ │   │
│  │                                  │                                    │   │
│  │                                  │ ╔═══════════════════════════════╗ │   │
│  │                                  │ ║ ☑ 2. Black & White Point      ║ │   │
│  │                                  │ ╠═══════════════════════════════╣ │   │
│  │                                  │ ║ Black Point Percentile:       ║ │   │
│  │                                  │ ║ [━●━━━━━━━━] 0.50             ║ │   │
│  │                                  │ ║                               ║ │   │
│  │                                  │ ║ White Point Percentile:       ║ │   │
│  │                                  │ ║ [━━━━━━━━━●] 99.50            ║ │   │
│  │                                  │ ║                               ║ │   │
│  │                                  │ ║ Shadow Bias:                  ║ │   │
│  │                                  │ ║ [━━━━━●━━━━] 0.00             ║ │ ▲ │
│  │                                  │ ║                               ║ │ █ │
│  │                                  │ ║ Highlight Bias:               ║ │ █ │
│  │                                  │ ║ [━━━━━●━━━━] 0.00             ║ │ S │
│  │                                  │ ╚═══════════════════════════════╝ │ C │
│  │                                  │                                    │ R │
│  │                                  │ ╔═══════════════════════════════╗ │ O │
│  │                                  │ ║ ☑ 3. Midtone Correction       ║ │ L │
│  │                                  │ ╠═══════════════════════════════╣ │ L │
│  │                                  │ ║ Gamma:                        ║ │   │
│  │                                  │ ║ [━━━━━●━━━━] 1.00             ║ │ B │
│  │                                  │ ║                               ║ │ A │
│  │                                  │ ║ Midtone Target:               ║ │ R │
│  │                                  │ ║ [━━━━━●━━━━] 0.50             ║ │   │
│  │                                  │ ║                               ║ │   │
│  │                                  │ ║ Restore Strength:             ║ │   │
│  │                                  │ ║ [●━━━━━━━━━] 0.00             ║ │   │
│  │                                  │ ╚═══════════════════════════════╝ │   │
│  │                                  │                                    │   │
│  │                                  │ ... (6 more groups below) ...     │ ▼ │
│  │                                  │                                    │   │
│  └──────────────────────────────────┴────────────────────────────────────┘   │
│  Status: Loaded: my_scan.jpg - Processing complete - Color Negative          │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Kontrollpanel - Alla 9 Grupper

### 1️⃣ Histogram Centering
```
☑ 1. Histogram Centering
├─ Target Midpoint:        [slider] 0.00 - 1.00
└─ Detection Method:       [dropdown] mean | median
```

### 2️⃣ Black & White Point
```
☑ 2. Black & White Point
├─ Black Point Percentile: [slider] 0.00 - 5.00
├─ White Point Percentile: [slider] 95.00 - 100.00
├─ Shadow Bias:            [slider] -0.20 - 0.20
└─ Highlight Bias:         [slider] -0.20 - 0.20
```

### 3️⃣ Midtone Correction
```
☑ 3. Midtone Correction (Gamma)
├─ Gamma:                  [slider] 0.50 - 2.00
├─ Midtone Target:         [slider] 0.00 - 1.00
└─ Restore Strength:       [slider] 0.00 - 1.00
```

### 4️⃣ Dynamic Range Expansion
```
☑ 4. Dynamic Range (Toe/Shoulder)
├─ Toe Strength:           [slider] 0.00 - 1.00
├─ Shoulder Strength:      [slider] 0.00 - 1.00
└─ Midtone Contrast:       [slider] 0.50 - 2.00
```

### 5️⃣ Color Balance
```
☑ 5. Color Balance
├─ Neutral Balance Strength: [slider] 0.00 - 1.00
└─ Film Profile:            [dropdown]
    ├─ Neutral
    ├─ Kodak Portra
    ├─ Kodak Ektar
    ├─ Fuji Pro
    └─ Fuji Superia
```
**Note**: Automatiskt inaktiverad för B&W Negative

### 6️⃣ Local Contrast Smoothing
```
☑ 6. Local Contrast Smoothing
├─ Smoothing Strength:     [slider] 0.00 - 1.00
├─ Shadow Smoothing:       [slider] 0.00 - 1.00
├─ Highlight Smoothing:    [slider] 0.00 - 1.00
└─ Preserve Edges:         [slider] 0.00 - 1.00
```
**Warning**: Kan vara LÅNGSAM på stora bilder!

### 7️⃣ Saturation Adjustment
```
☑ 7. Saturation Adjustment
├─ Base Saturation:        [slider] 0.00 - 2.00
├─ Density Modulation:     [slider] 0.00 - 1.00
└─ Shadow Color Boost:     [slider] 0.00 - 0.50
```
**Note**: Automatiskt inaktiverad för B&W Negative

### 8️⃣ Highlight & Shadow Protection
```
☑ 8. Highlight & Shadow Protection
├─ Highlight Protection:   [slider] 0.00 - 1.00
└─ Shadow Recovery:        [slider] 0.00 - 1.00
```

### 9️⃣ Final Tone Curve
```
☑ 9. Final Tone Curve
└─ Curve Profile:          [dropdown]
    ├─ Neutral
    ├─ Frontier
    ├─ Noritsu
    ├─ Portra-like
    └─ Soft
```

## Interaktion

### Ladda Bild
1. Klicka **"Load Image"**
2. Välj fil: `.jpg`, `.png`, `.tif`, `.bmp`
3. Bilden laddas och processas automatiskt

### Ändra Bildtyp
1. Välj från **"Image Type"** dropdown
2. Defaults laddas automatiskt:
   - Color Negative → Kodak Portra settings
   - B&W Negative → Smoothing aktiverad, färg inaktiverad
   - Positive → Mjuka inställningar

### Justera Parametrar
- **Checkboxar**: Aktivera/inaktivera helt steg
- **Sliders**: Finjustera värden
- **Dropdowns**: Välj profiler/metoder
- Bilden uppdateras **automatiskt** vid varje ändring

### Spara Resultat
1. Klicka **"Save Image"**
2. Välj format: `.jpg`, `.png`, `.tif`
3. Välj plats och filnamn
4. Färdig!

### Återställ
Klicka **"Reset to Defaults"** för att återställa alla parametrar till defaults för vald bildtyp.

## Keyboard Shortcuts (Planerade)

_Inte implementerade än, men planerade för framtida version:_

| Tangent | Funktion |
|---------|----------|
| `Ctrl+O` | Load Image |
| `Ctrl+S` | Save Image |
| `Ctrl+R` | Reset to Defaults |
| `Ctrl+Z` | Undo (future) |
| `Ctrl+Y` | Redo (future) |
| `Space` | Toggle Before/After (future) |
| `1-9` | Jump to step 1-9 |
| `Ctrl+1` | Color Negative mode |
| `Ctrl+2` | B&W Negative mode |
| `Ctrl+3` | Positive mode |

## UI States

### Initial State
```
Image Type: Color Negative
All groups: Checked (enabled)
All sliders: Default values
Preview: Empty (gray background)
Status: "Load an image to start"
```

### After Loading Color Negative
```
Image Type: Color Negative
Preview: Shows inverted + processed image
Color Balance: Enabled
Saturation: Enabled
Status: "Loaded: filename.jpg - Processing complete - Color Negative"
```

### After Switching to B&W Negative
```
Image Type: B&W Negative
Preview: Shows grayscale inverted image
Color Balance: DISABLED (grayed out)
Saturation: DISABLED (grayed out)
Smoothing: Enabled
Status: "Processing complete - B&W Negative"
```

### After Switching to Positive
```
Image Type: Positive
Preview: Shows original (non-inverted) with enhancements
Histogram Centering: DISABLED
Dynamic Range: DISABLED
Other controls: Available with lower defaults
Status: "Processing complete - Positive"
```

## Performance Indicators

### Fast (< 100ms)
- Load image
- Change dropdown
- Most sliders
- Reset to defaults

### Medium (100-500ms)
- Processing without smoothing
- Changing image type
- Applying protection

### Slow (> 500ms)
- **Local Contrast Smoothing** enabled
- Large images (> 20MP)
- Multiple operations at once

### Progress Feedback
Status bar updates:
- "Loading..."
- "Processing..."
- "Processing complete - [Image Type]"
- "Saved: filename.jpg"

## Screen Real Estate

### Recommended Window Size
- Minimum: 1400 x 900 px
- Recommended: 1600 x 1000 px
- Optimal: 1920 x 1080 px (Full HD)

### Panel Proportions
- Left (Preview): 60% width
- Right (Controls): 40% width
- Controls: Scrollable (always accessible)

## Color Scheme

```
Background:   #2b2b2b (dark gray)
Preview border: #cccccc (light gray)
Status bar:   #f0f0f0 (off-white)
Text:         Default system
Sliders:      PyQt6 Fusion style
```

## Font Sizes

```
Labels:       Default (10pt)
Status:       Default (10pt)
Group titles: Bold, 11pt
Values:       Monospace, 9pt
```

---

## Exempel på Slutresultat

### Input: Color Negative Scan
```
[Orange-tinted, inverted image from DSLR]
```

### After Processing:
```
[Natural colors, proper exposure, film-like characteristics]
```

### Settings Used:
- Image Type: Color Negative
- Film Profile: Kodak Portra
- Gamma: 1.1
- Base Saturation: 1.15
- Highlight Protection: 0.3
- Final Curve: Portra-like

---

**För fullständig guide, se [ADVANCED_EDITOR_GUIDE.md](ADVANCED_EDITOR_GUIDE.md)**
