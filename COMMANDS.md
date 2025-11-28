# 🎯 Alla Körkommandon - Bildskanning

## Huvudprogram

### Avancerad Bildredigerare (GUI med PyQt6)
```powershell
# Windows snabbstart
.\run_editor.bat

# Eller direkt med Python
python advanced_image_editor.py

# Med fullständig sökväg
& "C:/Users/Hampus Brink/Documents/GitHub/Bildskanning/.venv/Scripts/python.exe" advanced_image_editor.py
```

### Enkel Bildredigerare (GUI med Tkinter)
```powershell
python image_editor.py
```

### Batch CLI (kommandorad utan GUI)
```powershell
# Resize images
python main.py resize --input ./photos --output ./resized --width 800 --height 600

# Resize by percentage
python main.py resize --input ./photos --output ./resized --percentage 50

# Rotate images
python main.py rotate --input ./photos --output ./rotated --degrees 90

# Convert to grayscale
python main.py grayscale --input ./photos --output ./gray

# Adjust brightness
python main.py brightness --input ./photos --output ./bright --factor 1.5

# Adjust contrast
python main.py contrast --input ./photos --output ./contrast --factor 1.3
```

## Test och Demo

### Testa Pipeline
```powershell
# Kör pipeline-tester
python test_pipeline.py
```

### Programmatisk Användning
```powershell
# Exempel på hur man använder modulen i egen kod
python example_usage.py
```

### Testa GUI
```powershell
# Testa Tkinter GUI
python test_gui.py
```

### Funktionalitetstester
```powershell
# Testa funktionalitet
python test_functionality.py
```

## Skapa Testdata

### Skapa Testbilder
```powershell
python create_test_image.py
```

### Skapa Demo
```powershell
python create_demo.py
```

### Skapa Testguide
```powershell
python create_test_guide.py
```

## Installation & Setup

### Installera Dependencies
```powershell
# Installera alla paket från requirements.txt
pip install -r requirements.txt

# Eller med virtual environment
.venv\Scripts\pip.exe install -r requirements.txt
```

### Installera Specifika Paket
```powershell
# Pillow (för båda editors)
pip install Pillow

# PyQt6 (för advanced editor)
pip install PyQt6

# OpenCV (för advanced editor)
pip install opencv-python

# NumPy (för advanced editor)
pip install numpy
```

### Skapa Virtual Environment
```powershell
# Skapa venv
python -m venv .venv

# Aktivera venv
.venv\Scripts\Activate.ps1

# Installera dependencies
pip install -r requirements.txt
```

## Python Environment Info

### Kontrollera Python Version
```powershell
python --version
```

### Kontrollera Installerade Paket
```powershell
pip list
```

### Kontrollera Specifikt Paket
```powershell
pip show Pillow
pip show PyQt6
pip show opencv-python
```

## Debugging

### Kör med Verbose Output
```powershell
python -v advanced_image_editor.py
```

### Kontrollera Import
```powershell
python -c "import cv2; import PyQt6; import numpy; print('OK')"
```

### Testa cv2 Funktionalitet
```powershell
python -c "import cv2; print(cv2.__version__)"
```

### Testa PyQt6
```powershell
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

## Git Operations

### Status
```powershell
git status
```

### Add Changes
```powershell
git add advanced_image_editor.py
git add requirements.txt
git add *.md
```

### Commit
```powershell
git commit -m "Add advanced image editor with professional pipeline"
```

### Push
```powershell
git push origin copilot/create-basic-image-editor
```

## Snabbkommandon Sammanfattning

| Kommando | Beskrivning |
|----------|-------------|
| `.\run_editor.bat` | Kör advanced editor (snabbaste) |
| `python advanced_image_editor.py` | Kör advanced editor |
| `python image_editor.py` | Kör enkel editor |
| `python main.py --help` | Visa CLI hjälp |
| `python test_pipeline.py` | Testa pipeline |
| `python example_usage.py` | Programmatiskt exempel |
| `pip install -r requirements.txt` | Installera alla dependencies |

## Vanliga Problem & Lösningar

### Problem: "ModuleNotFoundError: No module named 'cv2'"
```powershell
# Lösning:
pip install opencv-python
```

### Problem: "ModuleNotFoundError: No module named 'PyQt6'"
```powershell
# Lösning:
pip install PyQt6
```

### Problem: NumPy compilation error
```powershell
# Lösning: Använd precompiled wheel
pip install opencv-python --no-deps
```

### Problem: GUI öppnas inte
```powershell
# Kontrollera att PyQt6 är installerat korrekt
python -c "from PyQt6.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); print('OK')"
```

### Problem: Bilden processas långsamt
```
# Lösning: Inaktivera "Local Contrast Smoothing" i GUI
# Det är den mest beräkningsintensiva operationen
```

## Miljöinformation

**Python Version**: 3.14.0  
**Virtual Environment**: `.venv`  
**Python Path**: `C:/Users/Hampus Brink/Documents/GitHub/Bildskanning/.venv/Scripts/python.exe`

## Länkar till Dokumentation

- [README.md](README.md) - Huvuddokumentation
- [QUICKSTART.md](QUICKSTART.md) - Snabbstartsguide
- [ADVANCED_EDITOR_GUIDE.md](ADVANCED_EDITOR_GUIDE.md) - Detaljerad användarguide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Teknisk arkitektur
- [DEVELOPMENT_SUMMARY.md](DEVELOPMENT_SUMMARY.md) - Utvecklingssammanfattning

---

**Pro tip**: Lägg till `.\run_editor.bat` i din PATH eller skapa en genväg på skrivbordet för ännu snabbare access! 🚀
