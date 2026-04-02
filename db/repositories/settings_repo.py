"""
Репозиторий для операций с настройками.
"""
import sqlite3
from typing import Any, Optional


class SettingsRepository:
    """Репозиторий для работы с настройками."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Получить значение настройки.

        Args:
            key: Ключ настройки.
            default: Значение по умолчанию.

        Returns:
            Значение настройки или None.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

    def get_int(self, key: str, default: int = 0) -> int:
        """
        Получить значение настройки как int.

        Args:
            key: Ключ настройки.
            default: Значение по умолчанию.

        Returns:
            Значение настройки как int.
        """
        value = self.get(key, str(default))
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def set(self, key: str, value: str, description: Optional[str] = None) -> bool:
        """
        Установить значение настройки.

        Args:
            key: Ключ настройки.
            value: Значение настройки.
            description: Описание (для новых настроек).

        Returns:
            True, если настройка установлена.
        """
        cursor = self.conn.cursor()
        if description:
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, description)
                VALUES (?, ?, ?)
            """, (key, value, description))
        else:
            cursor.execute("""
                UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP
                WHERE key = ?
            """, (value, key))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_all(self) -> dict:
        """
        Получить все настройки.

        Returns:
            Словарь с настройками.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, value, description FROM settings")
        return {row["key"]: {"value": row["value"], "description": row["description"]} 
                for row in cursor.fetchall()}
