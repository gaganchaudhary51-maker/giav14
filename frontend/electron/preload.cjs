const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("giaDesktop", Object.freeze({
  getProviderSettings: () => ipcRenderer.invoke("gia:provider-status"),
  saveProviderSettings: (settings) => ipcRenderer.invoke("gia:provider-save", settings),
  skipProviderSetup: () => ipcRenderer.invoke("gia:provider-skip"),
}));
