# MyInfoManager Desktop (Electron)

Десктопное приложение для Windows/Mac/Linux.

## Запуск (разработка)

```bash
cd desktop
npm install
npm start
```

**Важно:** Бэкенд (Python FastAPI) должен быть запущен отдельно:
```bash
# В другом терминале
cd ..
uvicorn server.main:app --host 127.0.0.1 --port 8000
```

## Сборка EXE (Windows)

```bash
cd desktop
npm run build:win
```

Результат в `desktop/dist/`.

## Архитектура

```
┌──────────────────────────────────┐
│   Electron (main.js)             │
│   ┌────────────────────────────┐ │
│   │  BrowserWindow (frontend)  │ │
│   │  sidebar/build/index.html  │ │
│   │  + React приложение        │ │
│   └────────────────────────────┘ │
│                                  │
│   ┌────────────────────────────┐ │
│   │  Python Backend (spawn)    │ │
│   │  FastAPI :8000             │ │
│   │  SQLite : data/myinfo.db   │ │
│   └────────────────────────────┘ │
└──────────────────────────────────┘
```

Приложение запускает встроен Python-сервер как дочерний процесс.
Фронтенд общается с API через `http://localhost:8000`.
