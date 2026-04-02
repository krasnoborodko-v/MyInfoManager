# MyInfoManager - Сводка проекта

**Дата последнего обновления:** 30 марта 2026  
**Статус:** ✅ Бэкенд и фронтенд полностью готовы

---

## 📋 Оглавление

1. [Архитектура](#архитектура)
2. [Структура проекта](#структура-проекта)
3. [Реализованные функции](#реализованные-функции)
4. [API эндпоинты](#api-эндпоинты)
5. [Структура базы данных](#структура-базы-данных)
6. [Технологический стек](#технологический-стек)
7. [Запуск проекта](#запуск-проекта)
8. [Известные проблемы](#известные-проблемы)
9. [Планы на будущее](#планы-на-будущее)

---

## Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
│  ┌─────────────┐  ┌─────────────────────────────────┐  │
│  │   Sidebar   │  │         Main Panel              │  │
│  │  - Ресурсы  │  │  - Просмотр/редактирование      │  │
│  │  - Заметки  │  │  - Формы создания/изменения     │  │
│  │  - Задачи   │  │  - Поиск                        │  │
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

---

## Структура проекта

```
MyInfoManager/
├── sidebar/                   # React фронтенд
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js      # API клиент
│   │   ├── components/
│   │   │   ├── Sidebar.js     # Боковая панель
│   │   │   ├── MainPanel.js   # Основная панель
│   │   │   └── AudioRecorder.js # Запись аудио
│   │   ├── hooks/
│   │   │   ├── useResources.js
│   │   │   ├── useNotes.js
│   │   │   ├── useTasks.js
│   │   │   ├── useSettings.js
│   │   │   └── useFoldersTags.js
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
│       ├── task_repo.py       # CRUD для задач
│       ├── attachment_repo.py # CRUD для вложений
│       ├── folder_repo.py     # CRUD для папок
│       ├── tag_repo.py        # CRUD для тегов
│       └── settings_repo.py   # CRUD для настроек
│
├── server/                    # Веб-сервер FastAPI
│   ├── main.py                # Точка входа
│   ├── schemas.py             # Pydantic схемы
│   └── api/
│       ├── resources.py       # API ресурсов
│       ├── notes.py           # API заметок
│       ├── tasks.py           # API задач
│       ├── categories.py      # API категорий
│       ├── attachments.py     # API вложений
│       ├── folders_tags.py    # API папок и тегов
│       └── settings.py        # API настроек
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
├── docs/                      # Документация
│   ├── SUMMARY.md             # Этот файл
│   ├── api.md                 # API документация
│   ├── database.md            # Структура БД
│   └── features.md            # Список функций
│
├── requirements.txt           # Зависимости Python
└── readme.md                  # Главный README
```

---

## Реализованные функции

### ✅ Ресурсы
- [x] Список ресурсов с категориями
- [x] Создание/редактирование/удаление
- [x] Поиск по имени
- [x] Переход по URL
- [x] Предварительный просмотр

### ✅ Заметки
- [x] Список заметок с категориями
- [x] Создание/редактирование/удаление
- [x] Поиск по имени и тексту
- [x] **Папки** (иерархическая структура)
- [x] **Теги** (цветные метки, многие-ко-многим)
- [x] **Вложения:**
  - [x] Изображения (галерея 200x200, увеличение 600x600)
  - [x] Аудио (встроенный плеер)
  - [x] **Запись с микрофона** 🎤
  - [x] Примечания к вложениям
- [x] **Перемещение между папками** (правый клик)

### ✅ Задачи
- [x] Список задач с категориями
- [x] Создание/редактирование/удаление
- [x] Поиск по имени и описанию
- [x] Срок выполнения
- [x] Чекбоксы выполнения

### ✅ Календарь
- [x] Просмотр месяца
- [x] Подсветка текущего дня

### ✅ Планировщик
- [x] План на день

### ✅ Настройки
- [x] Лимит аудио в заметке (1-100)
- [x] Синхронизация (вкл/выкл)
- [x] Уведомления (вкл/выкл)
- [x] Статус сервера

### ✅ Синхронизация
- [x] Модуль синхронизации (ядро)
- [x] Сравнение версий по timestamp
- [x] Разрешение конфликтов (4 стратегии)
- [x] Слияние данных

---

## API эндпоинты

### Ресурсы
```
GET    /api/resources              # Список ресурсов
POST   /api/resources              # Создать ресурс
GET    /api/resources/{id}         # Получить ресурс
PUT    /api/resources/{id}         # Обновить ресурс
DELETE /api/resources/{id}         # Удалить ресурс
GET    /api/resources/search?q=... # Поиск ресурсов
GET    /api/resources/categories   # Категории ресурсов
POST   /api/resources/categories   # Создать категорию
```

### Заметки
```
GET    /api/notes                  # Список заметок
POST   /api/notes                  # Создать заметку
GET    /api/notes/{id}             # Получить заметку
PUT    /api/notes/{id}             # Обновить заметку
DELETE /api/notes/{id}             # Удалить заметку
GET    /api/notes/search?q=...     # Поиск заметок
PATCH  /api/notes/{id}/folder      # Переместить в папку
```

### Задачи
```
GET    /api/tasks                  # Список задач
POST   /api/tasks                  # Создать задачу
GET    /api/tasks/{id}             # Получить задачу
PUT    /api/tasks/{id}             # Обновить задачу
DELETE /api/tasks/{id}             # Удалить задачу
GET    /api/tasks/search?q=...     # Поиск задач
```

### Вложения
```
GET    /api/attachments/note/{note_id}  # Вложения заметки
GET    /api/attachments/{id}            # Скачать файл
GET    /api/attachments/{id}?download=true  # Файл для просмотра
POST   /api/attachments/note/{note_id}  # Загрузить вложение
PUT    /api/attachments/{id}/note       # Обновить примечание
DELETE /api/attachments/{id}            # Удалить вложение
```

### Папки и теги
```
GET    /api/folders                # Список папок
POST   /api/folders                # Создать папку
PUT    /api/folders/{id}           # Обновить папку
DELETE /api/folders/{id}           # Удалить папку
GET    /api/tags                   # Список тегов
POST   /api/tags                   # Создать тег
PUT    /api/tags/{id}              # Обновить тег
DELETE /api/tags/{id}              # Удалить тег
GET    /api/notes/{note_id}/tags   # Теги заметки
POST   /api/notes/{note_id}/tags   # Добавить тег
DELETE /api/notes/{note_id}/tags/{tag_id}  # Удалить тег
```

### Настройки
```
GET    /api/settings               # Все настройки
GET    /api/settings/{key}         # Получить настройку
PUT    /api/settings/{key}         # Обновить настройку
```

---

## Структура базы данных

### Таблицы

#### `kategory_resource` - Категории ресурсов
```sql
CREATE TABLE kategory_resource (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
```

#### `resource` - Ресурсы
```sql
CREATE TABLE resource (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    kategory_id INTEGER,
    url TEXT,
    description TEXT,
    FOREIGN KEY (kategory_id) REFERENCES kategory_resource(id)
)
```

#### `kategory_note` - Категории заметок
```sql
CREATE TABLE kategory_note (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
```

#### `note` - Заметки
```sql
CREATE TABLE note (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    kategory_id INTEGER,
    folder_id INTEGER,
    note_text TEXT,
    data_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kategory_id) REFERENCES kategory_note(id),
    FOREIGN KEY (folder_id) REFERENCES folder(id)
)
```

#### `folder` - Папки
```sql
CREATE TABLE folder (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    note_category_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES folder(id),
    FOREIGN KEY (note_category_id) REFERENCES kategory_note(id)
)
```

#### `tag` - Теги
```sql
CREATE TABLE tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#008888',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

#### `note_tag` - Связь заметок и тегов
```sql
CREATE TABLE note_tag (
    note_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (note_id, tag_id),
    FOREIGN KEY (note_id) REFERENCES note(id),
    FOREIGN KEY (tag_id) REFERENCES tag(id)
)
```

#### `kategory_task` - Категории задач
```sql
CREATE TABLE kategory_task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
```

#### `task` - Задачи
```sql
CREATE TABLE task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    kategory_id INTEGER,
    description TEXT,
    data_time DATETIME,
    FOREIGN KEY (kategory_id) REFERENCES kategory_task(id)
)
```

#### `attachment` - Вложения
```sql
CREATE TABLE attachment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    file_data BLOB NOT NULL,
    file_size INTEGER,
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES note(id)
)
```

#### `settings` - Настройки
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

---

## Технологический стек

### Бэкенд
- **Python 3.11+**
- **FastAPI** - веб-фреймворк
- **SQLite** - база данных
- **Pydantic** - валидация данных
- **pytest** - тестирование

### Фронтенд
- **React 18**
- **lucide-react** - иконки
- **CSS3** - стилизация

### Зависимости (requirements.txt)
```
pytest>=7.0.0
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
python-multipart>=0.0.6
requests>=2.31.0
httpx>=0.24.0
```

---

## Запуск проекта

### 1. Установка зависимостей

```bash
# Бэкенд
cd MyInfoManager
pip install -r requirements.txt

# Фронтенд
cd sidebar
npm install
```

### 2. Запуск сервера

```bash
cd MyInfoManager
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

API документация: http://localhost:8000/docs

### 3. Запуск фронтенда

```bash
cd sidebar
npm start
```

Приложение: http://localhost:3000

### 4. Запуск тестов

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

---

## Известные проблемы

### ⚠️ Ограничения

1. **Вложения в БД**
   - Файлы хранятся в SQLite (BLOB)
   - При большом количестве файлов БД может стать большой
   - Рекомендуется: файлы >10MB хранить отдельно

2. **Синхронизация**
   - Модуль готов, но удалённый сервер не реализован
   - Требуется сервер для полной синхронизации

3. **Производительность**
   - При 1000+ заметок может замедляться поиск
   - Рекомендуется добавить индексы

### 🐛 Баги

- Нет известных критических багов

---

## Планы на будущее

### Приоритет 1 (ближайшие задачи)
- [ ] **Экспорт в PDF** - экспорт заметок с форматированием
- [ ] **Поиск по тегам** - фильтрация заметок по выбранным тегам
- [ ] **Избранные заметки** - быстрый доступ к важным

### Приоритет 2
- [ ] **Цветные метки для заметок** - быстрая категоризация
- [ ] **История изменений** - отслеживание редактирования
- [ ] **Экспорт/импорт данных** - резервное копирование

### Приоритет 3
- [ ] **Приоритеты для задач** - срочность/важность
- [ ] **Повторяющиеся задачи** - ежедневные/еженедельные
- [ ] **Напоминания** - уведомления о задачах

### Долгосрочные планы
- [ ] **Мобильное приложение** - React Native
- [ ] **Веб-сервер синхронизации** - для обмена между устройствами
- [ ] **Плагины** - расширение функциональности

---

## Контакты и поддержка

**Документация создана:** 30 марта 2026  
**Версия проекта:** 1.0.0  
**Статус:** ✅ Готов к использованию

---

*Этот документ автоматически генерируется и обновляется при изменении проекта.*
