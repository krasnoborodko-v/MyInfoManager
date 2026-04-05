#!/bin/bash
# ============================================================
# MyInfoManager — Server Stop Script
# ============================================================
# Usage: ./stop-server.sh
# ============================================================

echo "========================================"
echo "   MyInfoManager - Server Shutdown"
echo "========================================"
echo ""

# Останавливаем приложение
echo "[1/2] Stopping application..."
cd ~/MyInfoManager
docker compose down
echo ""

# Останавливаем инфраструктуру
echo "[2/2] Stopping infrastructure (Nginx + PostgreSQL)..."
cd infra
docker compose down
cd ..

echo ""
echo "========================================"
echo "   MyInfoManager stopped"
echo "========================================"
