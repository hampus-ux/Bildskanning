#!/bin/bash
# Quick start script for Bildskanning application

echo "========================================="
echo "Bildskanning - Quick Start Guide"
echo "========================================="
echo ""
echo "1. Installing dependencies..."
pip3 install -r requirements.txt
echo ""
echo "2. Creating test images..."
python3 create_test_image.py
echo ""
echo "3. Starting the application..."
echo ""
echo "Run the following command to start:"
echo "  python3 image_editor.py"
echo ""
echo "Or run it now? (Ctrl+C to cancel)"
sleep 3
python3 image_editor.py
