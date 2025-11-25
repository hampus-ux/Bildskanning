@echo off
echo ============================================
echo Sony ARW Support Setup
echo ============================================
echo.
echo This will download dcraw.exe for reading Sony ARW files
echo.
pause

echo Downloading dcraw for Windows...
curl -L -o dcraw.exe https://www.cybercom.net/~dcoffin/dcraw/dcraw.exe

if exist dcraw.exe (
    echo.
    echo ✓ dcraw.exe downloaded successfully!
    echo.
    echo You can now load Sony ARW files in the image editor.
) else (
    echo.
    echo ✗ Download failed. 
    echo.
    echo Alternative: Install Microsoft Camera Codec Pack
    echo Download from: https://www.microsoft.com/download/details.aspx?id=26829
)

echo.
pause
