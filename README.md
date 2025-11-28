# Analoga (Desktop App)

A professional film negative conversion tool built with React and Electron.

## How to Run Locally

### Prerequisites
- Install [Node.js](https://nodejs.org/) (LTS version recommended).

### Setup
1. Open a terminal in this folder.
2. Run `npm install` to download dependencies.

### Running the App
- **Development Mode**: Run `npm run dev` (opens in browser) or `npm run start:desktop` (builds and launches the desktop app).
- **Production Mode**: 
  1. Run `npm run build` (Creates the `dist` folder).
  2. Run `npm run app` (Launches the standalone window).

### Creating a Standalone Executable
To create a shareable `.exe` (Windows) or `.dmg` (Mac):
1. Run `npm run make`.
2. Check the `out` folder for your installer.

## Features
- RAW/DNG/TIFF Support
- Batch Processing (Roll Analysis)
- Frontier/Noritsu Color Science
- Spot Healing Tool
- Offline Capable