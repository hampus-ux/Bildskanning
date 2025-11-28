const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openDirectoryDialog: () => ipcRenderer.invoke('dialog:openDirectory'),
  createDirectory: (dirPath) => ipcRenderer.invoke('file:createDirectory', dirPath),
  saveBytes: (filePath, bytes) => ipcRenderer.invoke('file:saveBytes', filePath, bytes),
});
