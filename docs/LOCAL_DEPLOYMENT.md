# MyInfoManager — Локальное развёртывание

Документ описывает варианты запуска приложения на локальной Windows-машине без Docker.

---

## Архитектура

```
┌──────────────────────────────────────┐
│         FastAPI (порт 8000)          │
│                                      │
│  ┌────────────┐  ┌────────────────┐  │
│  │  API /api/*│  │  Статика (/)   │  │
│  │  CRUD      │  │  sidebar/build/│  │
│  └────────────┘  └────────────────┘  │
│                                      │
│  ┌────────────────────────────────┐  │
│  │  SQLite (data/myinfo.db)       │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

Бэкенд и фронтенд работают на **одном порту** — FastAPI отдаёт API и статику React-приложения.

---

## Вариант 1: Через Python (разработка)

### Требования

- Python 3.11+
- Node.js (для сборки фронтенда, если `sidebar/build/` отсутствует)

### Файлы

| Файл | Назначение |
|------|-----------|
| `start.bat` | Создаёт venv, ставит зависимости, запускает сервер, открывает браузер |
| `stop.bat` | Останавливает сервер |

### Использование

```cmd
start.bat   →  запуск
stop.bat    →  остановка
Ctrl+C      →  остановка (в окне start.bat)
```

### Что делает start.bat

1. Проверяет наличие Python
2. Создаёт `venv/` если нет
3. Устанавливает зависимости из `requirements.txt`
4. Собирает фронтенд (`npm run build`) если `sidebar/build/` отсутствует
5. Запускает uvicorn в отдельном окне
6. Открывает `http://localhost:8000` в браузере

### Ручной запуск (альтернатива батникам)

```bash
# Терминал 1 — бэкенд
uvicorn server.main:app --reload --host 127.0.0.1 --port 8000

# Терминал 2 — фронтенд (режим разработки с hot-reload)
cd sidebar
npm start
```

В режиме разработки фронтенд на порту 3000 проксирует API на порт 8000 через переменную `REACT_APP_API_URL`.

---

## Вариант 2: EXE через PyInstaller (готовое приложение)

### Требования

- Только Python 3.11+ для сборки. На целевом компьютере Python **не нужен**.

### Файлы

| Файл | Назначение |
|------|-----------|
| `launcher.py` | Точка входа — запускает uvicorn, открывает браузер |
| `MyInfoManager.spec` | Конфигурация PyInstaller |
| `start-exe.bat` | Обёртка для запуска готового EXE |

### Сборка EXE

```bash
pip install pyinstaller
pyinstaller MyInfoManager.spec --clean
```

Результат в `dist/MyInfoManager/`:
```
dist/MyInfoManager/
├── MyInfoManager.exe    ← исполняемый файл
├── _internal/           ← все зависимости, DLL, статика
│   ├── sidebar/build/   ← фронтенд
│   ├── server/          ← бэкенд
│   └── ...              ← Python, библиотеки
```

### Распространение

Достаточно скопировать папку `dist/MyInfoManager/` целиком на любой Windows-компьютер. Python не требуется.

### Запуск

```cmd
start-exe.bat        →  из корня проекта
# или
MyInfoManager.exe    →  из dist/MyInfoManager/
```

### Что происходит при запуске

1. Приложение определяет режим (PyInstaller через `sys._MEIPASS`)
2. Находит статику внутри распакованного архива
3. Запускает uvicorn на `127.0.0.1:8000`
4. Через 2 секунды открывает браузер
5. При `Ctrl+C` — корректно останавливается

---

## Конфигурация БД

### Локальный режим (по умолчанию)

```env
DATABASE_TYPE=sqlite
```

База данных: `data/myinfo.db` (SQLite файл).

### Переключение на PostgreSQL (локально)

```env
DATABASE_TYPE=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=myinfomanager
POSTGRES_USER=myinfo
POSTGRES_PASSWORD=myinfo_secret
```

---

## Ключевые изменения в коде

### 1. Единый сервер (API + статика)

`server/main.py` — FastAPI раздаёт статику из `sidebar/build/` через catch-all роут после всех API эндпоинтов:

```python
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    file_path = STATIC_DIR / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(STATIC_DIR / "index.html")
```

### 2. Абстрактный слой БД

`db/connection.py` — единый интерфейс для SQLite и PostgreSQL:

- `Connection` — абстрактное соединение
- `Cursor` — абстрактный курсор
- `Row` — абстрактная строка результата
- `get_connection()` — фабрика (возвращает нужный тип по `DATABASE_TYPE`)
- `create_tables()` — одинаковый SQL для обоих БД (`?` автоматически конвертируется в `%s` для PostgreSQL)

Все репозитории используют `Connection` вместо `sqlite3.Connection`.

### 3. API клиент фронтенда

`sidebar/src/api/client.js` — `API_BASE_URL = ''` (относительный путь), так как фронтенд и API на одном порту.

Для разработки с раздельными серверами:
```bash
REACT_APP_API_URL=http://localhost:8000 npm start
```

---

## Структура файлов (локальное развёртывание)

```
MyInfoManager/
├── start.bat              ← запуск через Python
├── stop.bat               ← остановка сервера
├── start-exe.bat          ← запуск EXE
├── launcher.py            ← точка входа для EXE
├── MyInfoManager.spec     ← конфиг PyInstaller
├── requirements.txt       ← Python-зависимости
├── .env                   ← переменные окружения
│
├── server/                ← FastAPI бэкенд
│   ├── main.py            ← точка входа (API + статика)
│   ├── schemas.py
│   └── api/
│
├── db/                    ← слой БД
│   ├── connection.py      ← абстрактный слой (SQLite/PostgreSQL)
│   ├── database.py        ← обратная совместимость
│   ├── models.py
│   └── repositories/      ← CRUD операции
│
├── sidebar/               ← React фронтенд
│   ├── src/
│   └── build/             ← собранная статика
│
├── data/
│   └── myinfo.db          ← SQLite база
│
└── dist/MyInfoManager/    ← готовый EXE (после сборки)
    ├── MyInfoManager.exe
    └── _internal/
```

---

## Тесты

```bash
pytest tests/test_db.py -v     # 31 тест БД
pytest tests/test_api.py -v    # 26 тестов API
pytest tests/test_sync.py -v   # 35 тестов синхронизации
```

> **Примечание:** Тесты используют общую БД `data/myinfo.db`. При повторных запусках возможны конфликты UNIQUE constraint из-за накопленных данных. Для чистой проверки удалите `data/myinfo.db` перед запуском.
