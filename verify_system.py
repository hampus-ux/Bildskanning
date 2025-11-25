#!/usr/bin/env python3
"""
Verification script - Check that all components are working
"""

import sys
import os
from pathlib import Path

print("=" * 70)
print("BILDSKANNING - SYSTEM VERIFICATION")
print("=" * 70)

# Check Python version
print(f"\n✓ Python version: {sys.version.split()[0]}")

# Check required modules
print("\n📦 Checking required modules...")
required_modules = {
    'PIL': 'Pillow',
    'PyQt6': 'PyQt6',
    'cv2': 'opencv-python',
    'numpy': 'numpy'
}

all_ok = True
for module, package in required_modules.items():
    try:
        __import__(module)
        print(f"  ✅ {package}")
    except ImportError:
        print(f"  ❌ {package} - NOT INSTALLED")
        all_ok = False

# Check main files
print("\n📄 Checking main program files...")
main_files = [
    'advanced_image_editor.py',
    'image_editor.py',
    'requirements.txt'
]

for file in main_files:
    if Path(file).exists():
        size = Path(file).stat().st_size
        print(f"  ✅ {file} ({size:,} bytes)")
    else:
        print(f"  ❌ {file} - MISSING")
        all_ok = False

# Check documentation
print("\n📚 Checking documentation files...")
doc_files = [
    'README.md',
    'QUICKSTART.md',
    'ADVANCED_EDITOR_GUIDE.md',
    'ARCHITECTURE.md',
    'GUI_OVERVIEW.md',
    'COMMANDS.md',
    'DEVELOPMENT_SUMMARY.md',
    'PROJECT_STRUCTURE.md'
]

for file in doc_files:
    if Path(file).exists():
        print(f"  ✅ {file}")
    else:
        print(f"  ⚠️  {file} - Missing (optional)")

# Check test files
print("\n🧪 Checking test files...")
test_files = [
    'test_pipeline.py',
    'example_usage.py'
]

for file in test_files:
    if Path(file).exists():
        print(f"  ✅ {file}")
    else:
        print(f"  ⚠️  {file} - Missing (optional)")

# Check launch scripts
print("\n🏃 Checking launch scripts...")
launch_files = [
    'run_editor.bat',
    'run_advanced_editor.ps1'
]

for file in launch_files:
    if Path(file).exists():
        print(f"  ✅ {file}")
    else:
        print(f"  ⚠️  {file} - Missing (optional)")

# Test import advanced editor
print("\n🔧 Testing advanced_image_editor import...")
try:
    from advanced_image_editor import (
        AutoEditParams,
        ImageType,
        FilmProfile,
        ToneCurveProfile,
        apply_edit_pipeline
    )
    print("  ✅ All imports successful")
    
    # Test creating params
    params_color = AutoEditParams.for_color_negative()
    params_bw = AutoEditParams.for_bw_negative()
    params_pos = AutoEditParams.for_positive()
    print(f"  ✅ Color Negative params: {params_color.film_profile.value}")
    print(f"  ✅ B&W Negative params: color_balance={params_bw.enable_color_balance}")
    print(f"  ✅ Positive params: histogram_centering={params_pos.enable_histogram_centering}")
    
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    all_ok = False

# Final verdict
print("\n" + "=" * 70)
if all_ok:
    print("✅ ALL SYSTEMS GO!")
    print("=" * 70)
    print("\n🚀 Ready to launch:")
    print("   python advanced_image_editor.py")
    print("   or")
    print("   .\\run_editor.bat")
else:
    print("⚠️  SOME ISSUES FOUND")
    print("=" * 70)
    print("\n🔧 Please install missing dependencies:")
    print("   pip install -r requirements.txt")

print("\n")
