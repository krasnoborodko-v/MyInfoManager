"""
API эндпоинты для управления настройками.
"""
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Form

from db.database import get_connection
from db.repositories.settings_repo import SettingsRepository


router = APIRouter(prefix="/api/settings", tags=["settings"])


def get_repo():
    """Получить репозиторий настроек."""
    conn = get_connection()
    return SettingsRepository(conn)


@router.get("", response_model=None)
def get_all_settings() -> Dict[str, Any]:
    """Получить все настройки."""
    repo = get_repo()
    return repo.get_all()


@router.get("/{key}")
def get_setting(key: str):
    """Получить настройку по ключу."""
    repo = get_repo()
    value = repo.get(key)
    
    if value is None:
        raise HTTPException(status_code=404, detail="Настройка не найдена")
    
    return {"key": key, "value": value}


@router.put("/{key}", response_model=None)
def update_setting(key: str, value: str = Form(..., description="Значение настройки")):
    """Обновить настройку."""
    repo = get_repo()

    # Проверка допустимых ключей
    allowed_keys = ['audio_limit', 'image_quality', 'theme', 'sync_enabled', 'notifications_enabled']
    if key not in allowed_keys:
        raise HTTPException(status_code=400, detail="Недопустимый ключ настройки")

    # Валидация значения
    if key == 'audio_limit':
        try:
            val = int(value)
            if val < 1 or val > 100:
                raise ValueError()
        except ValueError:
            raise HTTPException(status_code=400, detail="audio_limit должно быть от 1 до 100")

    elif key == 'image_quality':
        try:
            val = int(value)
            if val < 1 or val > 100:
                raise ValueError()
        except ValueError:
            raise HTTPException(status_code=400, detail="image_quality должно быть от 1 до 100")
    
    elif key in ['sync_enabled', 'notifications_enabled']:
        # Булевы значения
        if value not in ['true', 'false', '1', '0']:
            raise HTTPException(status_code=400, detail="Ожидается true/false")

    repo.set(key, value)
    return {"key": key, "value": value}
