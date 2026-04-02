# MyInfoManager

Программа для управления информацией, которую человек использует для работы и жизни.

## Основные функции

1. **Информационные ресурсы**
   - Список ресурсов с разбивкой по категориям
   - Предварительный просмотр и переход к ресурсу
   - Создание, редактирование, удаление записей
   - Поиск ресурсов по имени

2. **Заметки** — хранение заметок и идей

3. **Задачи** — управление списком задач

4. **Календарь** — календарь событий

5. **Планировщик** — план на день

## Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
│  ┌─────────────┐  ┌─────────────────────────────────┐  │
│  │   Sidebar   │  │         Main Panel              │  │
│  │  - Ресурсы  │  │  - Просмотр/редактирование      │  │
│  │  - Заметки  │  │  - Формы создания/изменения     │  │
│  │  - Задачи   │  │  - Поиск                        │  │
│  │  - Календарь│  │                                 │  │
│  └─────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Backend (FastAPI + SQLite)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Resources  │  │    Notes    │  │    Tasks    │     │
│  │    CRUD     │  │    CRUD     │  │    CRUD     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │           SQLite Database (local)               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Sync Module                            │
│  - Синхронизация с удалённым сервером                   │
│  - Разрешение конфликтов                                │
│  - Стратегии: local_wins, remote_wins, newer_wins      │
└─────────────────────────────────────────────────────────┘
```

## Документация

Полная документация проекта доступна в папке [`docs/`](docs/):

- 📄 [**SUMMARY.md**](docs/SUMMARY.md) - Полная сводка проекта
- 📄 [**api.md**](docs/api.md) - API документация (все эндпоинты)
- 📄 [**database.md**](docs/database.md) - Структура базы данных
- 📄 [**features.md**](docs/features.md) - Список всех функций

## Структура проекта

```
MyInfoManager/
├── sidebar/                   # React фронтенд
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js      # API клиент
│   │   ├── components/
│   │   │   ├── Sidebar.js     # Боковая панель
│   │   │   └── MainPanel.js   # Основная панель
│   │   ├── hooks/
│   │   │   ├── useResources.js
│   │   │   ├── useNotes.js
│   │   │   └── useTasks.js
│   │   └── App.js
│   ├── package.json
│   └── readme.md
│
├── db/                        # Модуль базы данных
│   ├── database.py            # Подключение к SQLite
│   ├── models.py              # Модели данных
│   └── repositories/
│       ├── resource_repo.py   # CRUD для ресурсов
│       ├── note_repo.py       # CRUD для заметок
│       └── task_repo.py       # CRUD для задач
│
├── server/                    # Веб-сервер FastAPI
│   ├── main.py                # Точка входа
│   ├── schemas.py             # Pydantic схемы
│   └── api/
│       ├── resources.py       # API ресурсов
│       ├── notes.py           # API заметок
│       ├── tasks.py           # API задач
│       └── categories.py      # API категорий
│
├── sync/                      # Модуль синхронизации
│   ├── sync_engine.py         # Ядро синхронизации
│   └── remote_client.py       # HTTP клиент
│
├── tests/                     # Тесты (75 тестов)
│   ├── test_db.py             # Тесты БД (22)
│   ├── test_api.py            # Тесты API (18)
│   └── test_sync.py           # Тесты синхронизации (35)
│
├── requirements.txt           # Зависимости Python
└── readme.md                  # Этот файл
```

## База данных

### Таблицы

- `kategory_resource` (id, name) — категории ресурсов
- `resource` (id, name, kategory_id, url, description) — ресурсы
- `kategory_note` (id, name) — категории заметок
- `note` (id, name, kategory_id, note_text, data_time) — заметки
- `kategory_task` (id, name) — категории задач
- `task` (id, name, kategory_id, description, data_time) — задачи

## Быстрый старт

### 1. Запуск бэкенда

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

API документация: http://localhost:8000/docs

### 2. Запуск фронтенда

```bash
cd sidebar

# Установка зависимостей
npm install

# Запуск (порт 3000)
npm start
```

### 3. Запуск тестов

```bash
# Все тесты
pytest tests/ -v

# Тесты БД
pytest tests/test_db.py -v

# Тесты API
pytest tests/test_api.py -v

# Тесты синхронизации
pytest tests/test_sync.py -v
```

## API эндпоинты

### Ресурсы
- `GET /api/resources` — список ресурсов
- `POST /api/resources` — создать ресурс
- `GET /api/resources/{id}` — получить ресурс
- `PUT /api/resources/{id}` — обновить ресурс
- `DELETE /api/resources/{id}` — удалить ресурс
- `GET /api/resources/search?q=...` — поиск ресурсов
- `GET /api/resources/categories` — категории ресурсов

### Заметки
- `GET /api/notes` — список заметок
- `POST /api/notes` — создать заметку
- `GET /api/notes/{id}` — получить заметку
- `PUT /api/notes/{id}` — обновить заметку
- `DELETE /api/notes/{id}` — удалить заметку
- `GET /api/notes/search?q=...` — поиск заметок
- `GET /api/notes/categories` — категории заметок

### Задачи
- `GET /api/tasks` — список задач
- `POST /api/tasks` — создать задачу
- `GET /api/tasks/{id}` — получить задачу
- `PUT /api/tasks/{id}` — обновить задачу
- `DELETE /api/tasks/{id}` — удалить задачу
- `GET /api/tasks/search?q=...` — поиск задач
- `GET /api/tasks/categories` — категории задач

## Статус

✅ **Бэкенд**: реализован полностью
- База данных SQLite
- REST API (FastAPI)
- Модуль синхронизации
- 75 тестов

✅ **Фронтенд**: реализован полностью
- React приложение
- Интеграция с API
- CRUD операции для ресурсов, заметок, задач
- Поиск и фильтрация
- Формы создания/редактирования

🔄 **Синхронизация**: модуль готов, требуется сервер для полной интеграции

## Технологии

**Бэкенд:**
- Python 3.11+
- FastAPI
- SQLite
- Pydantic
- pytest

**Фронтенд:**
- React 18
- lucide-react (иконки)
- CSS3

## Лицензия

MIT
