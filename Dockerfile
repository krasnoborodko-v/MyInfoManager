# ============================================================
# MyInfoManager — Dockerfile
# ============================================================
# Multi-stage: Stage 1 — сборка фронтенда
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

COPY sidebar/package.json sidebar/package-lock.json ./
RUN npm install --production=false

COPY sidebar/ .
RUN npm run build

# ============================================================
# Stage 2 — Python бэкенд + статика
FROM python:3.11-slim AS production

WORKDIR /app

# Python-зависимости (psycopg2-binary уже в requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем backend-код
COPY db/ ./db/
COPY server/ ./server/
COPY sync/ ./sync/
COPY launcher.py .

# Копируем собранную статику из Stage 1
COPY --from=frontend-builder /frontend/build ./sidebar/build/

# Создаём директорию для данных (SQLite если понадобится)
RUN mkdir -p /app/data

ENV PYTHONUNBUFFERED=1
ENV DATABASE_TYPE=postgres

EXPOSE 8000

# Запуск через launcher
CMD ["python", "launcher.py"]
