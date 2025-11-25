# 📁 Projektstruktur - Bildskanning

## Filöversikt

```
Bildskanning/
│
├── 🚀 HUVUDPROGRAM
│   ├── advanced_image_editor.py    ⭐ Avancerad redigerare (670+ rader)
│   ├── image_editor.py              📝 Enkel redigerare (273 rader)
│   └── main.py                      🖥️  CLI batch processor
│
├── 📚 DOKUMENTATION
│   ├── README.md                    📖 Huvuddokumentation
│   ├── QUICKSTART.md               🚀 Snabbstart (30 sekunder)
│   ├── ADVANCED_EDITOR_GUIDE.md    📘 Fullständig guide
│   ├── ARCHITECTURE.md             🏗️  Teknisk arkitektur
│   ├── GUI_OVERVIEW.md             🖼️  UI-layout
│   ├── COMMANDS.md                 ⌨️  Alla kommandon
│   ├── DEVELOPMENT_SUMMARY.md      📊 Utvecklingsöversikt
│   └── PROJECT_STRUCTURE.md        📁 Denna fil
│
├── 🧪 TESTER & EXEMPEL
│   ├── test_pipeline.py            ✅ Pipeline-tester
│   ├── example_usage.py            💡 Programmatiska exempel
│   ├── test_gui.py                 🖼️  GUI-tester
│   ├── test_functionality.py       🔧 Funktionalitetstester
│   ├── create_test_image.py        🎨 Skapa testbilder
│   ├── create_demo.py              🎬 Demo-skapare
│   └── create_test_guide.py        📝 Testguide-skapare
│
├── 🖼️  TESTBILDER
│   ├── test_negative.jpg           📸 Test färgnegativ
│   ├── test_positive.jpg           📷 Test positiv
│   └── TESTGUIDE.jpg              📋 Testguide
│
├── 🏃 SNABBSTARTSKRIPT
│   ├── run_editor.bat              ⚡ Windows batch (snabbast)
│   ├── run_advanced_editor.ps1     ⚡ PowerShell
│   └── quick_start.sh              ⚡ Unix/Mac
│
├── ⚙️  KONFIGURATION
│   ├── requirements.txt            📦 Python dependencies
│   ├── .gitignore                  🚫 Git ignore rules
│   └── .venv/                      🐍 Python virtual environment
│
└── 📂 SRC (TOM - legacy structure)
    └── __pycache__/                💾 Python cache
```

## Filstorlekar

| Fil | Storlek | Beskrivning |
|-----|---------|-------------|
| `advanced_image_editor.py` | ~25 KB | Komplett editor (670 rader) |
| `image_editor.py` | ~8 KB | Enkel editor (273 rader) |
| `main.py` | ~6 KB | CLI tool (161 rader) |

## Dependencies Tree

```
advanced_image_editor.py
├── PyQt6 (GUI framework)
│   ├── QtWidgets (UI components)
│   ├── QtCore (Core functionality)
│   └── QtGui (Graphics)
├── numpy (Numerical computing)
├── opencv-python (cv2) (Image processing)
│   └── numpy (dependency)
└── Pillow (PIL) (Image I/O)

image_editor.py
├── tkinter (Built-in GUI)
└── Pillow (PIL)

main.py
└── Pillow (PIL)
```

## Körningsflöde

### Advanced Editor
```
run_editor.bat
    ↓
.venv\Scripts\python.exe
    ↓
advanced_image_editor.py
    ↓
main() → QApplication
    ↓
ImageEditorWindow
    ↓
[User loads image]
    ↓
apply_edit_pipeline()
    ↓
[Display result]
```

### CLI Batch Processor
```
python main.py resize --input ./photos --output ./resized --width 800
    ↓
main.py → parse arguments
    ↓
find_images()
    ↓
BatchProcessor
    ↓
ImageEditor operations
    ↓
Save results
```

## Data Flow i Pipeline

```
DSLR Scan File (.jpg, .tif)
    ↓
PIL.Image.open()
    ↓
np.array() → uint8 RGB [0, 255]
    ↓
astype(float32) / 255 → [0, 1]
    ↓
┌─────────────────────────────┐
│ NEGATIVE INVERSION (if needed)│
├─────────────────────────────┤
│ 1. Histogram Centering      │
│ 2. Black & White Point      │
│ 3. Midtone Correction       │
│ 4. Dynamic Range            │
│ 5. Color Balance            │
│ 6. Smoothing                │
│ 7. Saturation               │
│ 8. Protection               │
│ 9. Final Tone Curve         │
└─────────────────────────────┘
    ↓
np.clip(0, 1)
    ↓
* 255 → uint8
    ↓
PIL.Image.fromarray()
    ↓
Save or Display
```

## Viktiga Kataloger

### `.venv/`
Python virtual environment med alla installerade paket:
```
.venv/
├── Lib/
│   └── site-packages/
│       ├── PIL/                  (Pillow)
│       ├── PyQt6/                (PyQt6)
│       ├── cv2/                  (OpenCV)
│       └── numpy/                (NumPy)
└── Scripts/
    ├── python.exe               (Python 3.14.0)
    └── pip.exe                  (Package manager)
```

### `src/` (Legacy)
Tom katalog - användes i tidigare version.
Kan raderas eller användas för framtida moduler.

## Git Branches

```
main (eller master)
└── copilot/create-basic-image-editor  ← Current branch
    └── copilot/fix-typo-in-documentation
```

## Rekommenderad Läsordning

### För Användare:
1. **QUICKSTART.md** - Kom igång snabbt
2. **ADVANCED_EDITOR_GUIDE.md** - Lär dig alla funktioner
3. **GUI_OVERVIEW.md** - Förstå gränssnittet
4. **COMMANDS.md** - Referens för kommandon

### För Utvecklare:
1. **README.md** - Projektöversikt
2. **ARCHITECTURE.md** - Teknisk design
3. **DEVELOPMENT_SUMMARY.md** - Vad har byggts
4. **example_usage.py** - Hur man använder API:et
5. **advanced_image_editor.py** - Källkoden

## Systemkrav

### Minimum:
- Windows 10/11
- Python 3.9+
- 4 GB RAM
- 500 MB diskutrymme

### Rekommenderat:
- Windows 11
- Python 3.12+
- 8 GB RAM
- 1 GB diskutrymme
- Dual-core processor eller bättre

### För stora bilder (> 30MP):
- 16 GB RAM
- Quad-core processor
- SSD för snabbare fil-I/O

## Filformat

### Input (stöds):
- ✅ JPEG (.jpg, .jpeg)
- ✅ PNG (.png)
- ✅ TIFF (.tif, .tiff)
- ✅ BMP (.bmp)
- ✅ WebP (.webp)

### Output (stöds):
- ✅ JPEG (bra för delning, mindre filer)
- ✅ PNG (lossless, större filer)
- ✅ TIFF (bäst för arkivering)

### Framtida stöd:
- 🔮 RAW (DNG, CR2, NEF, ARW)
- 🔮 16-bit TIFF
- 🔮 HDR/EXR

## Versionsinformation

| Komponent | Version |
|-----------|---------|
| Python | 3.14.0 |
| Pillow | 10.0.0+ |
| PyQt6 | 6.10.0 |
| OpenCV | 4.12.0 |
| NumPy | 2.3.5 |

---

**Last Updated**: 2025-11-25  
**Project**: Bildskanning  
**Author**: Hampus Brink
