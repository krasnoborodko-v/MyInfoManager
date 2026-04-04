const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let backendProcess;

// Запуск бэкенда (Python FastAPI)
function startBackend() {
  return new Promise((resolve, reject) => {
    const isDev = !app.isPackaged;
    const backendDir = isDev
      ? path.join(__dirname, '..')
      : path.join(process.resourcesPath);

    // В production нужно установить Python и зависимости отдельно
    // Для разработки — используем системный Python
    backendProcess = spawn('python', [
      '-m', 'uvicorn', 'server.main:app',
      '--host', '127.0.0.1',
      '--port', '8000',
      '--log-level', 'error'
    ], {
      cwd: backendDir,
      stdio: 'ignore',
      windowsHide: true
    });

    backendProcess.on('error', (err) => {
      console.error('Backend failed to start:', err);
      reject(err);
    });

    // Ждём пока сервер запустится
    setTimeout(resolve, 3000);
  });
}

function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    title: 'MyInfoManager',
    icon: path.join(__dirname, 'icon.png')
  });

  // Убираем стандартное меню
  Menu.setApplicationMenu(null);

  // Загружаем фронтенд
  const isDev = !app.isPackaged;
  if (isDev) {
    // В разработке — локальный build
    mainWindow.loadFile(path.join(__dirname, '..', 'sidebar', 'build', 'index.html'));
  } else {
    // В production — из extraResources
    mainWindow.loadFile(path.join(process.resourcesPath, 'frontend', 'index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  try {
    await startBackend();
  } catch (e) {
    console.error('Could not start backend:', e);
  }

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  stopBackend();
});
