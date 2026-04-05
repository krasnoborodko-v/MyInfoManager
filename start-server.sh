#!/bin/bash
# ============================================================
# MyInfoManager — Server Startup Script
# ============================================================
# Usage: ./start-server.sh
# ============================================================

set -e

echo "========================================"
echo "   MyInfoManager - Server Startup"
echo "========================================"
echo ""

# Переходим в директорию проекта
cd ~/MyInfoManager || { echo "[ERROR] Directory ~/MyInfoManager not found"; exit 1; }

# 1. Обновляем код
echo "[1/4] Pulling latest code..."
git pull
echo ""

# 2. Запускаем инфраструктуру (Nginx + shared PostgreSQL)
echo "[2/4] Starting infrastructure (Nginx + PostgreSQL)..."
cd infra

# Убеждаемся что внешняя сеть существует
docker network create platform-net 2>/dev/null || true

docker compose up -d
cd ..
echo ""

# 3. Собираем и запускаем приложение
echo "[3/4] Building and starting application..."
docker compose up -d --build
echo ""

# 4. Проверяем статус
echo "[4/4] Checking status..."
echo ""
echo "--- Application ---"
docker compose ps
echo ""
echo "--- Infrastructure ---"
cd infra && docker compose ps
cd ..

echo ""
echo "========================================"
echo "   MyInfoManager is running!"
echo "   Open: https://myinfo.local"
echo "========================================"
echo ""
echo "Useful commands:"
echo "  docker compose logs -f          # View app logs"
echo "  docker compose down             # Stop application"
echo "  cd infra && docker compose down # Stop infrastructure"
echo ""
