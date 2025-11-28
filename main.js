const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const fsp = fs.promises;

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
// Disabled to avoid dependency issues during development
// if (require('electron-squirrel-startup')) {
//   app.quit();
// }

function createWindow() {
  console.log('Creating window...');
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 1280,
    height: 900,
    backgroundColor: '#09090b',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false, // Allow loading local resources easily
      preload: path.join(__dirname, 'preload.js')
    },
    autoHideMenuBar: true, // Cleaner look
  });

  console.log('Window created');

  // Check if we are running in dev mode with an environment variable, or fall back to build
  const startUrl = process.env.ELECTRON_START_URL;

  if (startUrl) {
    console.log('Loading URL:', startUrl);
    mainWindow.loadURL(startUrl);
  } else {
    // In production or local desktop run, load the built file
    // This requires 'npm run build' to have been run first
    const indexPath = path.join(__dirname, 'dist/index.html');
    console.log('Loading file:', indexPath);
    mainWindow.loadFile(indexPath).catch(e => {
        console.error('Failed to load index.html. Did you run "npm run build"?', e);
    });
  }

  // Open DevTools for debugging
  // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
  console.log('App is ready!');
  
  // IPC handler for opening directory dialog
  ipcMain.handle('dialog:openDirectory', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory', 'createDirectory']
    });
    
    if (result.canceled) {
      return null;
    } else {
      return result.filePaths[0];
    }
  });

  // Create directory if missing (recursive)
  ipcMain.handle('file:createDirectory', async (_event, dirPath) => {
    try {
      await fsp.mkdir(dirPath, { recursive: true });
      return { ok: true };
    } catch (e) {
      return { ok: false, error: String(e) };
    }
  });

  // Save raw bytes to a file path
  ipcMain.handle('file:saveBytes', async (_event, filePath, bytes) => {
    try {
      const buf = Buffer.from(bytes);
      await fsp.writeFile(filePath, buf);
      return { ok: true };
    } catch (e) {
      return { ok: false, error: String(e) };
    }
  });
  
  createWindow();

  app.on('activate', () => {
    console.log('App activated');
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  console.log('All windows closed');
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Error handling
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});