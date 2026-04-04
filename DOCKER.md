# MyInfoManager — Docker Deployment

## Структура

```
MyInfoManager/
├── Dockerfile                    # Образ приложения
├── docker-compose.yml            # Сервис (app + postgres)
├── .env.example                  # Шаблон переменных
├── .env                          # Локальные переменные (в .gitignore)
│
├── infra/                        # Инфраструктура платформы
│   ├── docker-compose.yml        # Nginx + PostgreSQL
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── conf.d/
│   │       └── myinfomanager.conf
│   └── postgres/
│       └── init.sql
│
└── Dockerfile                    # Multi-stage: Node.js build → Python
```

## Быстрый старт (standalone)

```bash
# 1. Скопировать .env
cp .env.example .env

# 2. Запустить
docker-compose up -d

# 3. Проверить
curl http://localhost:8000/health

# 4. Остановить
docker-compose down
```

## Полная платформа (infra + сервисы)

```bash
# 1. Инфраструктура
cd infra
docker-compose up -d

# 2. Сервис MyInfoManager (подключается к общей БД)
cd ..
docker-compose up -d

# 3. Nginx маршрутизирует трафик
# myinfomanager.example.com -> myinfomanager:8000
```

## Переключение БД

| Режим | DATABASE_TYPE | Описание |
|-------|--------------|----------|
| SQLite | `sqlite` | Файл `data/myinfo.db` |
| PostgreSQL | `postgres` | Внешний сервер PostgreSQL |

## Для production

1. Замените `myinfomanager.example.com` на ваш домен
2. Получите SSL-сертификаты (Let's Encrypt)
3. Обновите пароли в `.env`
4. Раскомментируйте HTTPS в nginx конфиге
