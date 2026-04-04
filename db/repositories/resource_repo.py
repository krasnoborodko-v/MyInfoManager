"""
Репозиторий для операций CRUD с ресурсами.
"""
from typing import List, Optional

from ..connection import Connection
from ..models import Resource, KategoryResource


class ResourceRepository:
    """Репозиторий для работы с ресурсами."""

    def __init__(self, conn: Connection):
        self.conn = conn
    
    def get_all(self, kategory_id: Optional[int] = None) -> List[Resource]:
        """
        Получить все ресурсы, опционально фильтруя по категории.
        
        Args:
            kategory_id: ID категории для фильтрации.
        
        Returns:
            Список ресурсов.
        """
        cursor = self.conn.cursor()
        
        if kategory_id is not None:
            cursor.execute("""
                SELECT r.id, r.name, r.kategory_id, r.url, r.description, kr.name as kategory_name
                FROM resource r
                LEFT JOIN kategory_resource kr ON r.kategory_id = kr.id
                WHERE r.kategory_id = ?
                ORDER BY r.name
            """, (kategory_id,))
        else:
            cursor.execute("""
                SELECT r.id, r.name, r.kategory_id, r.url, r.description, kr.name as kategory_name
                FROM resource r
                LEFT JOIN kategory_resource kr ON r.kategory_id = kr.id
                ORDER BY r.name
            """)
        
        return [Resource.from_row(row) for row in cursor.fetchall()]
    
    def get_by_id(self, resource_id: int) -> Optional[Resource]:
        """
        Получить ресурс по ID.
        
        Args:
            resource_id: ID ресурса.
        
        Returns:
            Ресурс или None, если не найден.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.id, r.name, r.kategory_id, r.url, r.description, kr.name as kategory_name
            FROM resource r
            LEFT JOIN kategory_resource kr ON r.kategory_id = kr.id
            WHERE r.id = ?
        """, (resource_id,))
        
        row = cursor.fetchone()
        return Resource.from_row(row) if row else None
    
    def search(self, query: str) -> List[Resource]:
        """
        Поиск ресурсов по имени.
        
        Args:
            query: Строка поиска.
        
        Returns:
            Список найденных ресурсов.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.id, r.name, r.kategory_id, r.url, r.description, kr.name as kategory_name
            FROM resource r
            LEFT JOIN kategory_resource kr ON r.kategory_id = kr.id
            WHERE r.name LIKE ?
            ORDER BY r.name
        """, (f"%{query}%",))
        
        return [Resource.from_row(row) for row in cursor.fetchall()]
    
    def create(self, resource: Resource) -> Resource:
        """
        Создать новый ресурс.
        
        Args:
            resource: Ресурс для создания.
        
        Returns:
            Созданный ресурс с присвоенным ID.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO resource (name, kategory_id, url, description)
            VALUES (?, ?, ?, ?)
        """, (resource.name, resource.kategory_id, resource.url, resource.description))
        
        self.conn.commit()
        resource.id = cursor.lastrowid
        return resource
    
    def update(self, resource: Resource) -> Optional[Resource]:
        """
        Обновить существующий ресурс.
        
        Args:
            resource: Ресурс с обновлёнными данными.
        
        Returns:
            Обновлённый ресурс или None, если ресурс не найден.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE resource
            SET name = ?, kategory_id = ?, url = ?, description = ?
            WHERE id = ?
        """, (resource.name, resource.kategory_id, resource.url, resource.description, resource.id))
        
        self.conn.commit()
        
        if cursor.rowcount == 0:
            return None
        
        return self.get_by_id(resource.id)
    
    def delete(self, resource_id: int) -> bool:
        """
        Удалить ресурс по ID.
        
        Args:
            resource_id: ID ресурса для удаления.
        
        Returns:
            True, если ресурс удалён, False, если не найден.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM resource WHERE id = ?", (resource_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_categories(self) -> List[KategoryResource]:
        """
        Получить все категории ресурсов.
        
        Returns:
            Список категорий.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM kategory_resource ORDER BY name")
        return [KategoryResource.from_row(row) for row in cursor.fetchall()]
    
    def get_category_by_id(self, category_id: int) -> Optional[KategoryResource]:
        """
        Получить категорию по ID.
        
        Args:
            category_id: ID категории.
        
        Returns:
            Категория или None, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM kategory_resource WHERE id = ?", (category_id,))
        row = cursor.fetchone()
        return KategoryResource.from_row(row) if row else None
    
    def create_category(self, name: str) -> KategoryResource:
        """
        Создать новую категорию ресурсов.
        
        Args:
            name: Название категории.
        
        Returns:
            Созданная категория с присвоенным ID.
        """
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO kategory_resource (name) VALUES (?)", (name,))
        self.conn.commit()
        return KategoryResource(id=cursor.lastrowid, name=name)
    
    def delete_category(self, category_id: int) -> bool:
        """
        Удалить категорию ресурсов.
        
        Args:
            category_id: ID категории для удаления.
        
        Returns:
            True, если категория удалена, False, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM kategory_resource WHERE id = ?", (category_id,))
        self.conn.commit()
        return cursor.rowcount > 0
