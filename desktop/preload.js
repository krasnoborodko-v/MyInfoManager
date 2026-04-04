// Preload script — мост между Electron и renderer
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Можно добавить IPC вызовы если понадобятся
  platform: process.platform,
});
