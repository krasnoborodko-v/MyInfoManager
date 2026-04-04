# Авторизация в MyInfoManager

Полная документация по системе аутентификации и авторизации.

---

## Обзор

MyInfoManager использует **JWT (JSON Web Tokens)** для аутентификации. Каждый пользователь видит **только свои данные**. API защищено middleware, проверяющим токен.

### Схема работы

```
┌──────────┐  POST /auth/login   ┌───────────┐
│ Клиент   │ ──────────────────► │  Сервер   │
│ (веб/    │                     │ FastAPI   │
│  моб/    │ ◄────────────────── │           │
│  десктоп)│   {access_token,    └───────────┘
│          │    refresh_token}
│          │
│          │  GET /api/resources
│          │  Header: Authorization: Bearer <access_token>
│          │ ──────────────────────────────────►
│          │
│          │ ◄──────────────────────────────────
│          │  [{id: 1, name: "Мои данные"...}]
│          │  (только данные владельца токена)
└──────────┘
```

---

## Архитектура

### Компоненты

| Компонент | Файл | Назначение |
|-----------|------|-----------|
| **Модели БД** | `db/models.py` | Классы `User` |
| **Схема БД** | `db/connection.py` | Таблица `user` + FK `user_id` |
| **Схемы API** | `server/schemas.py` | Pydantic: `UserCreate`, `Token`, `TokenData` |
| **Auth роутер** | `server/api/auth.py` | Эндпоинты `/auth/*` |
| **Auth утилиты** | `server/auth.py` | Хеш паролей, создание/проверка JWT |
| **Middleware** | `server/main.py` | Зависимость `get_current_user` |

### Библиотеки

| Библиотека | Версия | Зачем |
|------------|--------|-------|
| `python-jose[cryptography]` | >= 3.3 | Создание и проверка JWT |
| `passlib[bcrypt]` | >= 1.7 | Хеширование паролей (bcrypt) |
| `python-multipart` | >= 0.0.6 | Формы логина (уже есть) |

---

## База данных

### Таблица `user`

```sql
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    full_name TEXT DEFAULT '',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL | Уникальный ID |
| `email` | TEXT UNIQUE | Логин (уникальный) |
| `hashed_password` | TEXT | bcrypt-хеш пароля |
| `full_name` | TEXT | Отображаемое имя |
| `is_active` | BOOLEAN | Флаг активности |
| `created_at` | TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | Дата обновления |

### Изменения в таблицах данных

**Все таблицы данных** получают поле `user_id`:

```sql
ALTER TABLE resource    ADD COLUMN user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE;
ALTER TABLE note        ADD COLUMN user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE;
ALTER TABLE task        ADD COLUMN user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE;
ALTER TABLE contact     ADD COLUMN user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE;
ALTER TABLE attachment  ADD COLUMN user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE;
ALTER TABLE folder      ADD COLUMN user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE;
ALTER TABLE tag         ADD COLUMN user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE;
ALTER TABLE kategory_resource ADD COLUMN user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE;
ALTER TABLE kategory_note     ADD COLUMN user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE;
ALTER TABLE kategory_task     ADD COLUMN user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE;
ALTER TABLE contact_group     ADD COLUMN user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE;
```

**Таблицы БЕЗ `user_id`** (системные, общие для всех):
- `note_tag` — связь заметки с тегами (заметка уже имеет user_id)
- `subtask` — подзадачи (родительская задача уже имеет user_id)
- `settings` — глобальные настройки (пока общие)

---

## JWT токены

### Структура

```json
{
  "sub": "user@example.com",
  "user_id": 1,
  "exp": 1712345678,
  "type": "access"
}
```

| Поле | Значение |
|------|----------|
| `sub` | Email пользователя (subject) |
| `user_id` | Числовой ID из БД |
| `exp` | Время истечения (Unix timestamp) |
| `type` | Тип токена: `access` или `refresh` |

### Параметры

| Параметр | Значение | Описание |
|----------|----------|----------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Время жизни access-токена |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Время жизни refresh-токена |
| `SECRET_KEY` | Генерируется при старте | Секрет для подписи JWT |
| `ALGORITHM` | HS256 | Алгоритм подписи |

### Секретный ключ

При старте сервер генерирует случайный `SECRET_KEY`. Это значит, что **при перезапуске все токены становятся невалидными**. Для production нужно задать фиксированный ключ через переменную окружения.

```bash
# .env
SECRET_KEY=your_super_secret_key_at_least_32_characters
```

---

## API эндпоинты

### POST /auth/register

Регистрация нового пользователя.

**Запрос:**
```json
{
  "email": "user@example.com",
  "password": "MyPassword123!",
  "full_name": "Иван Иванов"
}
```

**Ответ 201:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Иван Иванов",
  "is_active": true,
  "created_at": "2026-04-04T10:00:00"
}
```

**Ответ 400 (email занят):**
```json
{
  "detail": "User with this email already exists"
}
```

### POST /auth/login

Вход в систему.

**Запрос:**
```json
{
  "email": "user@example.com",
  "password": "MyPassword123!"
}
```

**Ответ 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Иван Иванов"
  }
}
```

**Ответ 401 (неверный пароль):**
```json
{
  "detail": "Incorrect email or password"
}
```

### POST /auth/refresh

Обновление access-токена.

**Запрос:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Ответ 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### GET /auth/me

Информация о текущем пользователе.

**Запрос:**
```
GET /auth/me
Authorization: Bearer <access_token>
```

**Ответ 200:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Иван Иванов",
  "is_active": true,
  "created_at": "2026-04-04T10:00:00"
}
```

---

## Использование в API

### Зависимость `get_current_user`

Все защищённые эндпоинты используют эту зависимость:

```python
from server.auth import get_current_user
from db.models import User

@router.get("/api/resources")
def get_resources(
    current_user: User = Depends(get_current_user),
    # ...
):
    # current_user.id — ID залогиненного пользователя
    # Все запросы фильтруются по этому ID
    repo = ResourceRepository(conn)
    return repo.get_all(user_id=current_user.id)
```

### Что происходит при запросе

1. Клиент отправляет `Authorization: Bearer <token>`
2. `get_current_user` расшифровывает JWT через `SECRET_KEY`
3. Извлекает `user_id` из payload
4. Ищет пользователя в БД
5. Если найден и активен — возвращает объект `User`
6. Если токен просрочен/неверен — возвращает HTTP 401

### Ошибки

| Код | Причина |
|-----|---------|
| 401 | Нет токена / неверный формат |
| 401 | Токен просрочен |
| 401 | Неверная подпись |
| 401 | Пользователь не найден |
| 403 | Пользователь деактивирован (`is_active=false`) |

---

## Хеширование паролей

Используется **bcrypt** через `passlib`:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# При регистрации
hashed = pwd_context.hash("MyPassword123!")
# → "$2b$12$abc123..."

# При входе
is_valid = pwd_context.verify("MyPassword123!", hashed)
# → True/False
```

**Никогда** не храните пароли в открытом виде.

---

## Миграции (SQLite → PostgreSQL)

Для **SQLite** колонки добавляются через `ALTER TABLE`:

```python
if db_type == "sqlite":
    cursor.execute("PRAGMA table_info(resource)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'user_id' not in columns:
        cursor.execute("ALTER TABLE resource ADD COLUMN user_id INTEGER")
```

Для **PostgreSQL** колонки создаются сразу в `CREATE TABLE` — миграция не нужна при первом развёртывании.

---

## Для существующих данных

При добавлении `user_id` в существующую БД:

1. Все старые записи получат `user_id = NULL`
2. Можно назначить их первому пользователю:
   ```sql
   UPDATE resource SET user_id = 1 WHERE user_id IS NULL;
   UPDATE note SET user_id = 1 WHERE user_id IS NULL;
   -- и т.д.
   ```

---

## Синхронизация

Модуль `sync/` использует тот же механизм авторизации:

```
POST /api/sync
Authorization: Bearer <token>
Body: { changes: [...] }
```

Сервер извлекает `user_id` из токена и синхронизирует **только данные этого пользователя**.

---

## Безопасность

| Мера | Реализация |
|------|-----------|
| Пароли | bcrypt, соль 12 раундов |
| Токены | HS256, срок 30 мин |
| Refresh | Отдельный токен, 7 дней |
| HTTPS | Обязательно для production |
| Rate limiting | Рекомендуется добавить на Nginx |
| CORS | Настроен на `*` (сузить для production) |
