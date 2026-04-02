# Структура базы данных MyInfoManager

**СУБД:** SQLite  
**Файл БД:** `data/myinfo.db`

---

## Обзор

База данных состоит из **12 таблиц**:
- 3 таблицы категорий
- 3 таблицы основных сущностей
- 1 таблица папок
- 1 таблица тегов
- 1 таблица связей заметок и тегов
- 1 таблица вложений
- 1 таблица настроек

---

## Диаграмма связей

```
kategory_resource ──┐
                    ├── resource
kategory_note ──────┼── note ──┬── folder
                    │          ├── attachment
kategory_task ──────┴── task   └── note_tag ── tag

settings (независимая)
```

---

## Таблицы

### kategory_resource

Категории для ресурсов.

```sql
CREATE TABLE kategory_resource (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
```

**Поля:**
- `id` - уникальный идентификатор
- `name` - название категории (уникальное)

---

### resource

Информационные ресурсы (ссылки).

```sql
CREATE TABLE resource (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    kategory_id INTEGER,
    url TEXT,
    description TEXT,
    FOREIGN KEY (kategory_id) REFERENCES kategory_resource(id) ON DELETE SET NULL
)
```

**Поля:**
- `id` - уникальный идентификатор
- `name` - название ресурса
- `kategory_id` - ссылка на категорию
- `url` - URL ресурса
- `description` - описание

---

### kategory_note

Категории для заметок.

```sql
CREATE TABLE kategory_note (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
```

**Поля:**
- `id` - уникальный идентификатор
- `name` - название категории (уникальное)

---

### folder

Папки для заметок (иерархическая структура).

```sql
CREATE TABLE folder (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    note_category_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES folder(id) ON DELETE CASCADE,
    FOREIGN KEY (note_category_id) REFERENCES kategory_note(id) ON DELETE CASCADE
)
```

**Поля:**
- `id` - уникальный идентификатор
- `name` - название папки
- `parent_id` - ссылка на родительскую папку (для иерархии)
- `note_category_id` - ссылка на категорию заметок
- `created_at` - дата создания

**Индексы:**
- `idx_folder_parent` - для быстрого поиска по parent_id
- `idx_folder_category` - для быстрого поиска по note_category_id

---

### note

Заметки.

```sql
CREATE TABLE note (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    kategory_id INTEGER,
    folder_id INTEGER,
    note_text TEXT,
    data_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kategory_id) REFERENCES kategory_note(id) ON DELETE SET NULL,
    FOREIGN KEY (folder_id) REFERENCES folder(id) ON DELETE SET NULL
)
```

**Поля:**
- `id` - уникальный идентификатор
- `name` - название заметки
- `kategory_id` - ссылка на категорию
- `folder_id` - ссылка на папку
- `note_text` - текст заметки
- `data_time` - дата создания/изменения

---

### tag

Теги для заметок.

```sql
CREATE TABLE tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#008888',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

**Поля:**
- `id` - уникальный идентификатор
- `name` - название тега (уникальное)
- `color` - цвет тега (hex)
- `created_at` - дата создания

---

### note_tag

Связь заметок и тегов (многие-ко-многим).

```sql
CREATE TABLE note_tag (
    note_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (note_id, tag_id),
    FOREIGN KEY (note_id) REFERENCES note(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE CASCADE
)
```

**Поля:**
- `note_id` - ссылка на заметку
- `tag_id` - ссылка на тег
- `created_at` - дата привязки

**Индексы:**
- `idx_note_tag_note` - для быстрого поиска по note_id
- `idx_note_tag_tag` - для быстрого поиска по tag_id

---

### kategory_task

Категории для задач.

```sql
CREATE TABLE kategory_task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
```

**Поля:**
- `id` - уникальный идентификатор
- `name` - название категории (уникальное)

---

### task

Задачи.

```sql
CREATE TABLE task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    kategory_id INTEGER,
    description TEXT,
    data_time DATETIME,
    FOREIGN KEY (kategory_id) REFERENCES kategory_task(id) ON DELETE SET NULL
)
```

**Поля:**
- `id` - уникальный идентификатор
- `name` - название задачи
- `kategory_id` - ссылка на категорию
- `description` - описание задачи
- `data_time` - срок выполнения

---

### attachment

Вложения (изображения, аудио).

```sql
CREATE TABLE attachment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    file_data BLOB NOT NULL,
    file_size INTEGER,
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES note(id) ON DELETE CASCADE
)
```

**Поля:**
- `id` - уникальный идентификатор
- `note_id` - ссылка на заметку
- `file_type` - MIME тип файла (image/png, audio/mp3)
- `file_data` - бинарные данные файла (BLOB)
- `file_size` - размер файла в байтах
- `note` - примечание к вложению
- `created_at` - дата загрузки

**Индексы:**
- `idx_attachment_note_id` - для быстрого поиска по note_id

---

### settings

Настройки приложения.

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

**Поля:**
- `key` - ключ настройки (уникальный)
- `value` - значение настройки
- `description` - описание настройки
- `updated_at` - дата последнего изменения

**Настройки по умолчанию:**
```sql
INSERT INTO settings (key, value, description) VALUES
    ('audio_limit', '5', 'Максимальное количество аудиофайлов в заметке'),
    ('image_quality', '80', 'Качество сжатия изображений (0-100)'),
    ('theme', 'dark', 'Тема оформления'),
    ('sync_enabled', 'true', 'Синхронизация'),
    ('notifications_enabled', 'true', 'Уведомления');
```

---

## Отношения между таблицами

### Один-ко-многим

| Родитель | Потомок | Связь |
|----------|---------|-------|
| kategory_resource | resource | Одна категория → много ресурсов |
| kategory_note | note | Одна категория → много заметок |
| kategory_note | folder | Одна категория → много папок |
| kategory_task | task | Одна категория → много задач |
| folder | folder | Одна папка → много подпапок (иерархия) |
| folder | note | Одна папка → много заметок |
| note | attachment | Одна заметка → много вложений |
| note | note_tag | Одна заметка → много связей с тегами |
| tag | note_tag | Один тег → много связей с заметками |

### Многие-ко-многим

| Таблица 1 | Таблица 2 | Связующая таблица |
|-----------|-----------|-------------------|
| note | tag | note_tag |

---

## Каскадное удаление

| Таблица | При удалении |
|---------|-------------|
| folder | Все подпапки удаляются (CASCADE) |
| note | Все вложения удаляются (CASCADE) |
| note | Все связи с тегами удаляются (CASCADE) |
| tag | Все связи с заметками удаляются (CASCADE) |
| kategory_* | Связанные сущности: kategory_id = NULL (SET NULL) |

---

## Примеры запросов

### Получить все заметки с тегами

```sql
SELECT n.*, GROUP_CONCAT(t.name) as tags
FROM note n
LEFT JOIN note_tag nt ON n.id = nt.note_id
LEFT JOIN tag t ON nt.tag_id = t.id
GROUP BY n.id;
```

### Получить все папки с количеством заметок

```sql
SELECT f.*, COUNT(n.id) as note_count
FROM folder f
LEFT JOIN note n ON f.id = n.folder_id
GROUP BY f.id;
```

### Получить все вложения заметки

```sql
SELECT * FROM attachment
WHERE note_id = 5
ORDER BY created_at DESC;
```

### Получить теги для заметки

```sql
SELECT t.*
FROM tag t
JOIN note_tag nt ON t.id = nt.tag_id
WHERE nt.note_id = 5;
```

### Получить иерархию папок

```sql
WITH RECURSIVE folder_tree AS (
    SELECT id, name, parent_id, note_category_id, 0 as level
    FROM folder
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT f.id, f.name, f.parent_id, f.note_category_id, ft.level + 1
    FROM folder f
    JOIN folder_tree ft ON f.parent_id = ft.id
)
SELECT * FROM folder_tree
ORDER BY level, name;
```

---

## Миграции

### Добавление поля folder_id в note

```sql
ALTER TABLE note ADD COLUMN folder_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_note_folder ON note(folder_id);
```

### Добавление поля note в attachment

```sql
ALTER TABLE attachment ADD COLUMN note TEXT;
```

---

## Резервное копирование

### Экспорт БД

```bash
sqlite3 data/myinfo.db ".backup 'backup.db'"
```

### Импорт БД

```bash
sqlite3 data/myinfo.db ".restore backup.db"
```

### Экспорт в SQL

```bash
sqlite3 data/myinfo.db ".dump" > backup.sql
```

---

## Оптимизация

### Индексы

```sql
CREATE INDEX IF NOT EXISTS idx_attachment_note_id ON attachment(note_id);
CREATE INDEX IF NOT EXISTS idx_folder_parent ON folder(parent_id);
CREATE INDEX IF NOT EXISTS idx_folder_category ON folder(note_category_id);
CREATE INDEX IF NOT EXISTS idx_note_tag_note ON note_tag(note_id);
CREATE INDEX IF NOT EXISTS idx_note_tag_tag ON note_tag(tag_id);
```

### Очистка

```sql
VACUUM;
ANALYZE;
```

---

*Документация обновлена: 30 марта 2026*
