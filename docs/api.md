# API документация MyInfoManager

**Базовый URL:** `http://localhost:8000`  
**Документация Swagger:** http://localhost:8000/docs

---

## Оглавление

1. [Ресурсы](#ресурсы)
2. [Заметки](#заметки)
3. [Задачи](#задачи)
4. [Вложения](#вложения)
5. [Папки](#папки)
6. [Теги](#теги)
7. [Настройки](#настройки)
8. [Категории](#категории)

---

## Ресурсы

### Получить все ресурсы

```http
GET /api/resources
```

**Параметры:**
- `kategory_id` (optional) - фильтр по категории

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "GitHub",
    "kategory_id": 2,
    "url": "https://github.com",
    "description": "Репозитории кода",
    "kategory_name": "Обучение"
  }
]
```

### Создать ресурс

```http
POST /api/resources
```

**Тело запроса:**
```json
{
  "name": "Stack Overflow",
  "kategory_id": 2,
  "url": "https://stackoverflow.com",
  "description": "Вопросы и ответы"
}
```

### Обновить ресурс

```http
PUT /api/resources/{id}
```

### Удалить ресурс

```http
DELETE /api/resources/{id}
```

### Поиск ресурсов

```http
GET /api/resources/search?q={query}
```

---

## Заметки

### Получить все заметки

```http
GET /api/notes
```

**Параметры:**
- `kategory_id` (optional) - фильтр по категории
- `folder_id` (optional) - фильтр по папке

### Создать заметку

```http
POST /api/notes
```

**Тело запроса:**
```json
{
  "name": "Рецепт борща",
  "kategory_id": 1,
  "folder_id": 5,
  "note_text": "Ингредиенты: свёкла, капуста, мясо...",
  "data_time": "2026-03-30T14:30:00"
}
```

### Обновить заметку

```http
PUT /api/notes/{id}
```

### Удалить заметку

```http
DELETE /api/notes/{id}
```

### Переместить заметку в папку

```http
PATCH /api/notes/{id}/folder
```

**Тело запроса:**
```json
{
  "folder_id": 5
}
```

### Поиск заметок

```http
GET /api/notes/search?q={query}
```

---

## Задачи

### Получить все задачи

```http
GET /api/tasks
```

**Параметры:**
- `kategory_id` (optional) - фильтр по категории

### Создать задачу

```http
POST /api/tasks
```

**Тело запроса:**
```json
{
  "name": "Сделать отчёт",
  "kategory_id": 1,
  "description": "Подготовить ежемесячный отчёт",
  "data_time": "2026-03-31T18:00:00"
}
```

### Обновить задачу

```http
PUT /api/tasks/{id}
```

### Удалить задачу

```http
DELETE /api/tasks/{id}
```

### Поиск задач

```http
GET /api/tasks/search?q={query}
```

---

## Вложения

### Получить вложения заметки

```http
GET /api/attachments/note/{note_id}
```

**Ответ:**
```json
[
  {
    "id": 1,
    "note_id": 5,
    "file_type": "image/png",
    "file_size": 1483249,
    "note": "Скриншот ошибки",
    "created_at": "2026-03-30T10:15:00"
  }
]
```

### Загрузить вложение

```http
POST /api/attachments/note/{note_id}
```

**Формат:** `multipart/form-data`

**Параметры:**
- `file` - файл (изображение или аудио)
- `note` (optional) - примечание к вложению

**Поддерживаемые типы:**
- Изображения: `image/jpeg`, `image/png`, `image/gif`, `image/webp`, `image/svg+xml`
- Аудио: `audio/mpeg`, `audio/mp3`, `audio/wav`, `audio/ogg`, `audio/webm`

**Ограничения:**
- Максимальный размер: 10MB

### Получить файл для просмотра

```http
GET /api/attachments/{id}?download=true
```

**Ответ:** Base64 данные файла (для отображения в браузере)

### Обновить примечание к вложению

```http
PUT /api/attachments/{id}/note
```

**Тело запроса:**
```json
{
  "note": "Новое примечание"
}
```

### Удалить вложение

```http
DELETE /api/attachments/{id}
```

---

## Папки

### Получить все папки

```http
GET /api/folders
```

**Параметры:**
- `category_id` (optional) - фильтр по категории
- `tree` (optional) - вернуть в виде дерева (`true`/`false`)

**Ответ (дерево):**
```json
[
  {
    "id": 1,
    "name": "Программирование",
    "parent_id": null,
    "note_category_id": 2,
    "children": [
      {
        "id": 2,
        "name": "Python",
        "parent_id": 1
      }
    ]
  }
]
```

### Создать папку

```http
POST /api/folders
```

**Тело запроса:**
```json
{
  "name": "Python",
  "parent_id": 1,
  "note_category_id": 2
}
```

### Обновить папку

```http
PUT /api/folders/{id}
```

### Удалить папку

```http
DELETE /api/folders/{id}
```

---

## Теги

### Получить все теги

```http
GET /api/tags
```

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "Важное",
    "color": "#ff0000",
    "created_at": "2026-03-30T10:00:00"
  }
]
```

### Создать тег

```http
POST /api/tags
```

**Тело запроса:**
```json
{
  "name": "Срочное",
  "color": "#ff6600"
}
```

### Обновить тег

```http
PUT /api/tags/{id}
```

### Удалить тег

```http
DELETE /api/tags/{id}
```

### Получить теги заметки

```http
GET /api/notes/{note_id}/tags
```

### Добавить тег к заметке

```http
POST /api/notes/{note_id}/tags
```

**Тело запроса:**
```json
{
  "tag_id": 1
}
```

### Удалить тег из заметки

```http
DELETE /api/notes/{note_id}/tags/{tag_id}
```

### Установить все теги для заметки

```http
PUT /api/notes/{note_id}/tags
```

**Тело запроса:**
```json
{
  "tag_ids": [1, 2, 3]
}
```

---

## Настройки

### Получить все настройки

```http
GET /api/settings
```

**Ответ:**
```json
{
  "audio_limit": {
    "value": "5",
    "description": "Максимальное количество аудиофайлов в заметке"
  },
  "image_quality": {
    "value": "80",
    "description": "Качество сжатия изображений (0-100)"
  },
  "theme": {
    "value": "dark",
    "description": "Тема оформления"
  },
  "sync_enabled": {
    "value": "true",
    "description": "Синхронизация"
  },
  "notifications_enabled": {
    "value": "true",
    "description": "Уведомления"
  }
}
```

### Получить настройку

```http
GET /api/settings/{key}
```

### Обновить настройку

```http
PUT /api/settings/{key}
```

**Тело запроса:**
```json
{
  "value": "10"
}
```

**Допустимые ключи:**
- `audio_limit` - целое число (1-100)
- `image_quality` - целое число (1-100)
- `theme` - строка
- `sync_enabled` - `true`/`false`
- `notifications_enabled` - `true`/`false`

---

## Категории

### Категории ресурсов

```http
GET /api/resources/categories
POST /api/resources/categories?name={name}
DELETE /api/resources/categories/{id}
```

### Категории заметок

```http
GET /api/notes/categories
POST /api/notes/categories?name={name}
DELETE /api/notes/categories/{id}
```

### Категории задач

```http
GET /api/tasks/categories
POST /api/tasks/categories?name={name}
DELETE /api/tasks/categories/{id}
```

### Все категории (общий эндпоинт)

```http
GET /api/categories/resources
GET /api/categories/notes
GET /api/categories/tasks
```

---

## Коды ответов

| Код | Описание |
|-----|----------|
| 200 | Успешно |
| 201 | Создано |
| 204 | Удалено (без содержимого) |
| 400 | Ошибка валидации |
| 404 | Не найдено |
| 500 | Внутренняя ошибка сервера |

---

## Аутентификация

В текущей версии аутентификация не реализована. Все эндпоинты доступны без токенов.

---

## Лимиты

| Параметр | Значение |
|----------|----------|
| Размер файла | 10MB |
| Название ресурса | 200 символов |
| Название заметки | 200 символов |
| Название категории | 100 символов |
| URL | 500 символов |

---

*Документация автоматически генерируется через Swagger UI: http://localhost:8000/docs*
