"""
Обратная совместимость — перенаправляет в db.connection.

Все новые импорты должны использовать db.connection напрямую.
Этот файл оставлен для старых тестов и скриптов.
"""
from db.connection import (
    get_connection,
    create_tables,
    init_database,
    Connection,
    Cursor,
    Row,
)

# Для обратной совместимости — старый путь к SQLite БД
from pathlib import Path
DATABASE_PATH = Path(__file__).parent.parent / "data" / "myinfo.db"

__all__ = [
    'get_connection',
    'create_tables',
    'init_database',
    'Connection',
    'Cursor',
    'Row',
    'DATABASE_PATH',
]
