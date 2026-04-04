"""
Репозиторий для операций CRUD с ресурсами.
Все методы принимают user_id для изоляции данных пользователей.
"""
from typing import List, Optional

from ..connection import Connection
from ..models import Resource, KategoryResource


class ResourceRepository:
    """Репозиторий для работы с ресурсами."""

    def __init__(self, conn: Connection):
        self.conn = conn

    def get_all(self, user_id: int, kategory_id: Optional[int] = None) -> List[Resource]:
        """Получить все ресурсы пользователя."""
        cursor = self.conn.cursor()
        if kategory_id is not None:
            cursor.execute("""
                SELECT r.id, r.name, r.kategory_id, r.url, r.description, kr.name as kategory_name
                FROM resource r
                LEFT JOIN kategory_resource kr ON r.kategory_id = kr.id
                WHERE r.kategory_id = ? AND r.user_id = ?
                ORDER BY r.name
            """, (kategory_id, user_id))
        else:
            cursor.execute("""
                SELECT r.id, r.name, r.kategory_id, r.url, r.description, kr.name as kategory_name
                FROM resource r
                LEFT JOIN kategory_resource kr ON r.kategory_id = kr.id
                WHERE r.user_id = ?
                ORDER BY r.name
            """, (user_id,))
        return [Resource.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, resource_id: int, user_id: int) -> Optional[Resource]:
        """Получить ресурс по ID (только если принадлежит пользователю)."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.id, r.name, r.kategory_id, r.url, r.description, kr.name as kategory_name
            FROM resource r
            LEFT JOIN kategory_resource kr ON r.kategory_id = kr.id
            WHERE r.id = ? AND r.user_id = ?
        """, (resource_id, user_id))
        row = cursor.fetchone()
        return Resource.from_row(row) if row else None

    def search(self, user_id: int, query: str) -> List[Resource]:
        """Поиск ресурсов по имени."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.id, r.name, r.kategory_id, r.url, r.description, kr.name as kategory_name
            FROM resource r
            LEFT JOIN kategory_resource kr ON r.kategory_id = kr.id
            WHERE r.user_id = ? AND r.name LIKE ?
            ORDER BY r.name
        """, (user_id, f"%{query}%"))
        return [Resource.from_row(row) for row in cursor.fetchall()]

    def create(self, resource: Resource, user_id: int) -> Resource:
        """Создать новый ресурс."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO resource (name, kategory_id, url, description, user_id)
            VALUES (?, ?, ?, ?, ?)
        """, (resource.name, resource.kategory_id, resource.url, resource.description, user_id))
        self.conn.commit()
        resource.id = cursor.lastrowid
        return resource

    def update(self, resource: Resource, user_id: int) -> Optional[Resource]:
        """Обновить ресурс (только если принадлежит пользователю)."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE resource
            SET name = ?, kategory_id = ?, url = ?, description = ?
            WHERE id = ? AND user_id = ?
        """, (resource.name, resource.kategory_id, resource.url, resource.description, resource.id, user_id))
        self.conn.commit()
        if cursor.rowcount == 0:
            return None
        return self.get_by_id(resource.id, user_id)

    def delete(self, resource_id: int, user_id: int) -> bool:
        """Удалить ресурс (только если принадлежит пользователю)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM resource WHERE id = ? AND user_id = ?", (resource_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def create_category(self, name: str, user_id: int) -> KategoryResource:
        """Создать категорию ресурса."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO kategory_resource (name, user_id) VALUES (?, ?)",
            (name, user_id),
        )
        self.conn.commit()
        return KategoryResource(id=cursor.lastrowid, name=name)

    def get_categories(self, user_id: int) -> List[KategoryResource]:
        """Получить все категории ресурса пользователя."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name FROM kategory_resource WHERE user_id = ? ORDER BY name",
            (user_id,),
        )
        return [KategoryResource(id=row["id"], name=row["name"]) for row in cursor.fetchall()]

    def delete_category(self, category_id: int, user_id: int) -> bool:
        """Удалить категорию ресурса."""
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM kategory_resource WHERE id = ? AND user_id = ?",
            (category_id, user_id),
        )
        self.conn.commit()
        return cursor.rowcount > 0
