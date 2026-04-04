# MyInfoManager — Серверное развёртывание (Docker)

Документ описывает размещение приложения на VPS в Docker-контейнерах с PostgreSQL и Nginx.

---

## Архитектура платформы

```
                    ┌─────────────────────────────────────┐
                    │         VPS (Ubuntu/Debian)         │
                    │                                     │
  Android ◄──────►  │   ┌─────────────────────────────┐   │  ◄──────► Windows
  клиенты           │   │        Nginx :80/:443        │   │            клиенты
                    │   │   Reverse Proxy + SSL         │   │
  Браузер ◄──────►  │   └──────────┬──────────────────┘   │
                    │              │                      │
                    │   ┌──────────┼──────────────────┐   │
                    │   │          │                  │   │
                    │   ▼          ▼                  ▼   │
                    │ ┌──────┐ ┌──────────┐ ┌──────────┐  │
                    │ │MyInfo│ │  Blog    │ │ Service  │  │
                    │ │Mgr   │ │WordPress │ │    N     │  │
                    │ │:8000 │ │  :8080   │ │  :9000   │  │
                    │ └──┬───┘ └────┬─────┘ └────┬─────┘  │
                    │    │         │            │         │
                    │    ▼         ▼            ▼         │
                    │  ┌─────────────────────────────┐    │
                    │  │   PostgreSQL :5432           │    │
                    │  │   myinfomanager, blog, ...   │    │
                    │  └─────────────────────────────┘    │
                    │                                     │
                    └─────────────────────────────────────┘
                           ▲              ▲
                           │ HTTPS sync   │ HTTPS sync
                    ┌──────┴──────┐ ┌────┴─────────┐
                    │  Android БД │ │ Windows БД   │
                    │  (локал.)   │ │  (локал.)    │
                    └─────────────┘ └──────────────┘
```

---

## Структура файлов

```
MyInfoManager/
├── Dockerfile                    # Multi-stage образ
├── docker-compose.yml            # Сервис MyInfoManager (standalone)
├── .env.example                  # Шаблон переменных
├── .dockerignore                 # Исключения из образа
├── DOCKER.md                     # Краткая документация
│
├── infra/                        # Инфраструктура платформы
│   ├── docker-compose.yml        # Nginx + PostgreSQL
│   ├── nginx/
│   │   ├── nginx.conf            # Основной конфиг
│   │   └── conf.d/
│   │       └── myinfomanager.conf  # Маршрутизация
│   └── postgres/
│       └── init.sql              # Создание БД и пользователей
│
├── server/                       # FastAPI бэкенд
├── db/                           # Слой БД (SQLite + PostgreSQL)
├── sidebar/                      # React фронтенд
├── sync/                         # Модуль синхронизации
└── launcher.py                   # Точка входа для Docker
```

---

## Multi-stage Dockerfile

```dockerfile
# Stage 1: Сборка фронтенда (Node.js)
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY sidebar/package.json sidebar/package-lock.json ./
RUN npm install --production=false
COPY sidebar/ .
RUN npm run build

# Stage 2: Python бэкенд + статика
FROM python:3.11-slim AS production
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY db/ ./db/
COPY server/ ./server/
COPY sync/ ./sync/
COPY launcher.py .
COPY --from=frontend-builder /frontend/build ./sidebar/build/
ENV PYTHONUNBUFFERED=1
ENV DATABASE_TYPE=postgres
EXPOSE 8000
CMD ["python", "launcher.py"]
```

**Преимущества:**
- Фронтенд собирается в отдельном stage — не тащит Node.js в production
- Итоговый образ только Python + статика (~200MB вместо ~500MB)
- `psycopg2-binary` позволяет не устанавливать libpq-dev в production

---

## Standalone запуск (один сервис со своей БД)

```bash
# 1. Конфигурация
cp .env.example .env
# Отредактировать пароли

# 2. Запуск
docker-compose up -d

# 3. Проверка
curl http://localhost:8000/health
# → {"status":"ok"}

# 4. Логи
docker-compose logs -f myinfomanager

# 5. Остановка
docker-compose down
# С удалением данных:
docker-compose down -v
```

### Что создаётся

| Контейнер | Описание | Порты |
|-----------|----------|-------|
| `myinfomanager` | Приложение FastAPI + фронтенд | 8000 |
| `myinfomanager-db` | PostgreSQL (изолированный) | 5432 (внутри сети) |

### Тома (данные сохраняются)

| Том | Назначение |
|-----|-----------|
| `postgres-data` | Файлы PostgreSQL |
| `uploads-data` | Загруженные файлы (вложения) |

---

## Полная платформа (общая инфраструктура)

### Шаг 1: Инфраструктура

```bash
cd infra
docker-compose up -d
```

Создаётся:
- **Nginx** — reverse proxy на портах 80/443
- **PostgreSQL** — общая БД для всех сервисов

### Шаг 2: Сервисы

```bash
cd ..
docker-compose up -d
```

Сервис MyInfoManager подключается к **общей** PostgreSQL через `infra/docker-compose.yml`.

### Маршрутизация

Nginx направляет запросы по доменному имени:

| Домен | Контейнер |
|-------|-----------|
| `myinfomanager.example.com` | myinfomanager:8000 |
| `blog.example.com` | blog:8080 (будущий) |

Конфиг: `infra/nginx/conf.d/myinfomanager.conf`

---

## Конфигурация

### .env файл

```env
# Тип БД
DATABASE_TYPE=postgres

# PostgreSQL (для standalone)
POSTGRES_HOST=myinfomanager-db
POSTGRES_PORT=5432
POSTGRES_DB=myinfomanager
POSTGRES_USER=myinfo
POSTGRES_PASSWORD=your_secure_password

# Порт
PORT=8000
```

### Для платформы (infra/.env)

```env
# Общий PostgreSQL
PG_USER=platform
PG_PASSWORD=platform_secret
PG_DB=platform
```

---

## Переключение БД: SQLite ↔ PostgreSQL

### Как работает

```python
# db/connection.py
def _get_db_type() -> str:
    return os.environ.get("DATABASE_TYPE", "sqlite").lower()

def get_connection(db_path=None) -> Connection:
    if _get_db_type() == "postgres":
        return _create_postgres()   # psycopg2
    else:
        return _create_sqlite(db_path)  # sqlite3
```

### Сравнение

| | SQLite | PostgreSQL |
|--|--------|------------|
| **Где** | Локальная разработка | VPS / production |
| **Хранилище** | Файл `data/myinfo.db` | Сервер PostgreSQL |
| **Конкурентность** | Один писатель | Много писателей |
| **Миграции** | `ALTER TABLE` на лету | Создаётся с нуля |
| **BLOB** | `BLOB` | `BYTEA` |
| **INSERT** | `INSERT OR IGNORE` | `ON CONFLICT DO NOTHING` |

### Различия в SQL обрабатываются автоматически

```python
# db/connection.py — _PostgresCursor.execute()
def execute(self, sql: str, parameters: tuple = ()):
    adapted_sql = sql.replace("?", "%s")  # ? → %s для psycopg2
    self._cur.execute(adapted_sql, parameters)
```

---

## Production Checklist

### 1. SSL-сертификаты

```bash
# Let's Encrypt (certbot)
certbot certonly --standalone -d myinfomanager.example.com

# Копировать в nginx
cp /etc/letsencrypt/live/myinfomanager.example.com/*.pem infra/nginx/ssl/
```

### 2. Раскомментировать HTTPS

В `infra/nginx/conf.d/myinfomanager.conf`:
```nginx
server {
    listen 443 ssl http2;
    server_name myinfomanager.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ...
}
```

### 3. Обновить пароли

```env
POSTGRES_PASSWORD=<сложный_пароль>
PG_PASSWORD=<сложный_пароль>
```

### 4. Обновить домен

```nginx
server_name myinfomanager.yourdomain.com;  # вместо example.com
```

### 5. Автозапуск

```bash
# systemd сервис для автозапуска
sudo systemctl enable docker
# Docker Compose restart policies уже настроены:
# restart: unless-stopped
```

---

## Синхронизация с клиентами

### Эндпоинт

```
POST https://myinfomanager.example.com/api/sync
```

### Как работает

1. Клиент (Android/Windows) хранит локальную копию БД
2. При изменении — отправляет дельту на сервер
3. Сервер применяет изменения, разрешает конфликты
4. Сервер возвращает обновления с момента последней синхронизации

### Стратегии разрешения конфликтов

- `local_wins` — побеждает клиентская версия
- `remote_wins` — побеждает серверная версия
- `newer_wins` — побеждает более новая по `updated_at`

Модуль синхронизации: `sync/sync_engine.py`, `sync/remote_client.py`

---

## Добавление нового сервиса

### 1. Создать папку сервиса

```
services/my-service/
├── Dockerfile
└── docker-compose.yml
```

### 2. Добавить в infra/postgres/init.sql

```sql
CREATE USER myservice WITH PASSWORD 'secret';
CREATE DATABASE myservice OWNER myservice;
GRANT ALL PRIVILEGES ON DATABASE myservice TO myservice;
```

### 3. Добавить в nginx

```nginx
# infra/nginx/conf.d/my-service.conf
server {
    listen 80;
    server_name myservice.example.com;

    location / {
        proxy_pass http://my-service:порт;
        ...
    }
}
```

### 4. Запустить

```bash
cd services/my-service
docker-compose up -d
```

---

## Команды

### Управление сервисом

```bash
# Запуск
docker-compose up -d

# Логи
docker-compose logs -f

# Перезапуск
docker-compose restart

# Остановка
docker-compose down

# Остановка с удалением данных
docker-compose down -v
```

### Управление платформой

```bash
# Инфраструктура
cd infra && docker-compose up -d

# Обновить образ
docker-compose build --no-cache
docker-compose up -d

# Посмотреть статус
docker-compose ps

# Подключиться к БД
docker exec -it myinfomanager-db psql -U myinfo -d myinfomanager

# Подключиться к контейнеру
docker exec -it myinfomanager sh
```

### Мониторинг

```bash
# Ресурсы
docker stats

# Здоровье БД
docker exec myinfomanager-db pg_isready

# Логи nginx
docker exec platform-nginx tail -f /var/log/nginx/access.log
```
