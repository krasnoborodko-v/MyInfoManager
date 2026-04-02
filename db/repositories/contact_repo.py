"""
Репозиторий для работы с контактами.
"""
import json
from typing import List, Optional

from db.models import Contact, ContactGroup


class ContactRepository:
    """Репозиторий для контактов."""

    def __init__(self, conn):
        """
        Инициализировать репозиторий.

        Args:
            conn: Подключение к базе данных.
        """
        self.conn = conn

    # === Методы для групп контактов ===

    def get_groups(self) -> List[ContactGroup]:
        """
        Получить все группы контактов.

        Returns:
            Список групп.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, color, created_at
            FROM contact_group
            ORDER BY name
        """)
        return [ContactGroup.from_row(row) for row in cursor.fetchall()]

    def get_group_by_id(self, group_id: int) -> Optional[ContactGroup]:
        """
        Получить группу по ID.

        Args:
            group_id: ID группы.

        Returns:
            Группа или None, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, color, created_at
            FROM contact_group
            WHERE id = ?
        """, (group_id,))
        row = cursor.fetchone()
        return ContactGroup.from_row(row) if row else None

    def create_group(self, name: str, color: str = "#008888") -> ContactGroup:
        """
        Создать новую группу.

        Args:
            name: Название группы.
            color: Цвет группы.

        Returns:
            Созданная группа.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO contact_group (name, color)
            VALUES (?, ?)
        """, (name, color))
        self.conn.commit()
        return self.get_group_by_id(cursor.lastrowid)

    def update_group(self, group_id: int, name: Optional[str] = None, color: Optional[str] = None) -> Optional[ContactGroup]:
        """
        Обновить группу.

        Args:
            group_id: ID группы.
            name: Новое название.
            color: Новый цвет.

        Returns:
            Обновлённая группа или None.
        """
        cursor = self.conn.cursor()
        
        # Получаем текущие данные
        current = self.get_group_by_id(group_id)
        if current is None:
            return None
        
        new_name = name if name is not None else current.name
        new_color = color if color is not None else current.color
        
        cursor.execute("""
            UPDATE contact_group
            SET name = ?, color = ?
            WHERE id = ?
        """, (new_name, new_color, group_id))
        self.conn.commit()
        return self.get_group_by_id(group_id)

    def delete_group(self, group_id: int) -> bool:
        """
        Удалить группу.

        Args:
            group_id: ID группы.

        Returns:
            True, если удалена, False иначе.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM contact_group WHERE id = ?", (group_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # === Методы для контактов ===

    def get_all(self, group_id: Optional[int] = None, favorite_only: bool = False, search: Optional[str] = None) -> List[Contact]:
        """
        Получить все контакты с фильтрацией.

        Args:
            group_id: ID группы для фильтрации.
            favorite_only: Только избранные.
            search: Поисковый запрос.

        Returns:
            Список контактов.
        """
        cursor = self.conn.cursor()
        
        query = """
            SELECT c.id, c.first_name, c.last_name, c.middle_name, c.group_id,
                   c.phones, c.emails, c.address, c.company, c.position,
                   c.birth_date, c.photo, c.photo_type, c.socials, c.website,
                   c.is_favorite, c.notes, c.created_at, c.updated_at,
                   g.name as group_name
            FROM contact c
            LEFT JOIN contact_group g ON c.group_id = g.id
            WHERE 1=1
        """
        params = []
        
        if group_id is not None:
            query += " AND c.group_id = ?"
            params.append(group_id)
        
        if favorite_only:
            query += " AND c.is_favorite = 1"
        
        if search:
            query += """
                AND (
                    c.first_name LIKE ? OR
                    c.last_name LIKE ? OR
                    c.middle_name LIKE ? OR
                    c.company LIKE ? OR
                    c.phones LIKE ? OR
                    c.emails LIKE ?
                )
            """
            search_pattern = f"%{search}%"
            params.extend([search_pattern] * 6)
        
        query += " ORDER BY c.last_name, c.first_name"
        
        cursor.execute(query, params)
        return [Contact.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, contact_id: int) -> Optional[Contact]:
        """
        Получить контакт по ID.

        Args:
            contact_id: ID контакта.

        Returns:
            Контакт или None.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.id, c.first_name, c.last_name, c.middle_name, c.group_id,
                   c.phones, c.emails, c.address, c.company, c.position,
                   c.birth_date, c.photo, c.photo_type, c.socials, c.website,
                   c.is_favorite, c.notes, c.created_at, c.updated_at,
                   g.name as group_name
            FROM contact c
            LEFT JOIN contact_group g ON c.group_id = g.id
            WHERE c.id = ?
        """, (contact_id,))
        row = cursor.fetchone()
        return Contact.from_row(row) if row else None

    def create(self, contact: Contact) -> Contact:
        """
        Создать новый контакт.

        Args:
            contact: Контакт для создания.

        Returns:
            Созданный контакт с ID.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO contact (
                first_name, last_name, middle_name, group_id,
                phones, emails, address, company, position,
                birth_date, photo, photo_type, socials, website,
                is_favorite, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contact.first_name, contact.last_name, contact.middle_name, contact.group_id,
            contact.phones, contact.emails, contact.address, contact.company, contact.position,
            contact.birth_date, contact.photo, contact.photo_type, contact.socials, contact.website,
            1 if contact.is_favorite else 0, contact.notes
        ))
        self.conn.commit()
        return self.get_by_id(cursor.lastrowid)

    def update(self, contact: Contact) -> Optional[Contact]:
        """
        Обновить контакт.

        Args:
            contact: Контакт с обновлёнными данными.

        Returns:
            Обновлённый контакт или None.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE contact
            SET first_name = ?, last_name = ?, middle_name = ?, group_id = ?,
                phones = ?, emails = ?, address = ?, company = ?, position = ?,
                birth_date = ?, photo = ?, photo_type = ?, socials = ?, website = ?,
                is_favorite = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            contact.first_name, contact.last_name, contact.middle_name, contact.group_id,
            contact.phones, contact.emails, contact.address, contact.company, contact.position,
            contact.birth_date, contact.photo, contact.photo_type, contact.socials, contact.website,
            1 if contact.is_favorite else 0, contact.notes, contact.id
        ))
        self.conn.commit()
        
        if cursor.rowcount == 0:
            return None
        
        return self.get_by_id(contact.id)

    def delete(self, contact_id: int) -> bool:
        """
        Удалить контакт.

        Args:
            contact_id: ID контакта.

        Returns:
            True, если удалён, False иначе.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM contact WHERE id = ?", (contact_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def toggle_favorite(self, contact_id: int) -> Optional[Contact]:
        """
        Переключить статус избранного.

        Args:
            contact_id: ID контакта.

        Returns:
            Обновлённый контакт или None.
        """
        contact = self.get_by_id(contact_id)
        if contact is None:
            return None
        
        contact.is_favorite = not contact.is_favorite
        return self.update(contact)

    def search(self, query: str) -> List[Contact]:
        """
        Поиск контактов.

        Args:
            query: Поисковый запрос.

        Returns:
            Список найденных контактов.
        """
        return self.get_all(search=query)
