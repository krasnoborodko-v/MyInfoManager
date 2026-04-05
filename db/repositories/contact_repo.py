"""
Репозиторий для работы с контактами.
Все методы принимают user_id для изоляции данных пользователей.
"""
import json
from typing import List, Optional

from ..connection import Connection
from ..models import Contact, ContactGroup


class ContactRepository:
    """Репозиторий для контактов."""

    def __init__(self, conn: Connection):
        self.conn = conn

    # --- Группы ---

    def create_group(self, name: str, user_id: int, color: str = '#008888') -> ContactGroup:
        """Создать группу контактов."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO contact_group (name, color, user_id) VALUES (?, ?, ?) RETURNING id",
            (name, color, user_id),
        )
        self.conn.commit()
        return ContactGroup(id=cursor.lastrowid, name=name, color=color)

    def get_groups(self, user_id: int) -> List[ContactGroup]:
        """Получить все группы пользователя."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM contact_group WHERE user_id = ? ORDER BY name",
            (user_id,),
        )
        return [ContactGroup.from_row(row) for row in cursor.fetchall()]

    def update_group(self, group_id: int, user_id: int, name: Optional[str] = None, color: Optional[str] = None) -> Optional[ContactGroup]:
        """Обновить группу."""
        group = self.get_group_by_id(group_id, user_id)
        if not group:
            return None
        if name is not None:
            group.name = name
        if color is not None:
            group.color = color
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE contact_group SET name = ?, color = ? WHERE id = ? AND user_id = ?",
            (group.name, group.color, group_id, user_id),
        )
        self.conn.commit()
        return group

    def get_group_by_id(self, group_id: int, user_id: int) -> Optional[ContactGroup]:
        """Получить группу по ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contact_group WHERE id = ? AND user_id = ?", (group_id, user_id))
        row = cursor.fetchone()
        return ContactGroup.from_row(row) if row else None

    def delete_group(self, group_id: int, user_id: int) -> bool:
        """Удалить группу."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM contact_group WHERE id = ? AND user_id = ?", (group_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0

    # --- Контакты ---

    def create(self, contact: Contact, user_id: int) -> Contact:
        """Создать контакт."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO contact (first_name, last_name, middle_name, group_id, user_id,
                phones, emails, address, company, position, birth_date, photo, photo_type,
                socials, website, is_favorite, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """, (contact.first_name, contact.last_name, contact.middle_name, contact.group_id, user_id,
              contact.phones, contact.emails, contact.address, contact.company, contact.position,
              contact.birth_date, contact.photo, contact.photo_type,
              contact.socials, contact.website, int(contact.is_favorite or False), contact.notes))
        self.conn.commit()
        contact.id = cursor.lastrowid
        return contact

    def get_all(self, user_id: int, group_id: Optional[int] = None, favorite: bool = False, search: Optional[str] = None) -> List[Contact]:
        """Получить все контакты пользователя."""
        cursor = self.conn.cursor()
        query = """
            SELECT c.*, g.name as group_name
            FROM contact c
            LEFT JOIN contact_group g ON c.group_id = g.id
            WHERE c.user_id = ?
        """
        params: list = [user_id]

        if group_id is not None:
            query += " AND c.group_id = ?"
            params.append(group_id)
        if favorite:
            query += " AND c.is_favorite = 1"
        if search:
            query += " AND (c.first_name LIKE ? OR c.last_name LIKE ? OR c.company LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

        query += " ORDER BY c.last_name, c.first_name"
        cursor.execute(query, tuple(params))
        return [Contact.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, contact_id: int, user_id: int) -> Optional[Contact]:
        """Получить контакт по ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.*, g.name as group_name
            FROM contact c
            LEFT JOIN contact_group g ON c.group_id = g.id
            WHERE c.id = ? AND c.user_id = ?
        """, (contact_id, user_id))
        row = cursor.fetchone()
        return Contact.from_row(row) if row else None

    def update(self, contact: Contact, user_id: int) -> Optional[Contact]:
        """Обновить контакт."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE contact SET first_name=?, last_name=?, middle_name=?, group_id=?,
                phones=?, emails=?, address=?, company=?, position=?, birth_date=?,
                photo=?, photo_type=?, socials=?, website=?, is_favorite=?, notes=?
            WHERE id = ? AND user_id = ?
        """, (contact.first_name, contact.last_name, contact.middle_name, contact.group_id,
              contact.phones, contact.emails, contact.address, contact.company, contact.position,
              contact.birth_date, contact.photo, contact.photo_type,
              contact.socials, contact.website, int(contact.is_favorite or False), contact.notes,
              contact.id, user_id))
        self.conn.commit()
        if cursor.rowcount == 0:
            return None
        return self.get_by_id(contact.id, user_id)

    def delete(self, contact_id: int, user_id: int) -> bool:
        """Удалить контакт."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM contact WHERE id = ? AND user_id = ?", (contact_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def toggle_favorite(self, contact_id: int, user_id: int) -> Optional[Contact]:
        """Переключить избранное."""
        contact = self.get_by_id(contact_id, user_id)
        if not contact:
            return None
        contact.is_favorite = not contact.is_favorite
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE contact SET is_favorite = ? WHERE id = ? AND user_id = ?",
            (int(contact.is_favorite), contact_id, user_id),
        )
        self.conn.commit()
        return contact

    def upload_photo(self, contact_id: int, user_id: int, photo_data: bytes, photo_type: str) -> Optional[Contact]:
        """Загрузить фото контакта."""
        contact = self.get_by_id(contact_id, user_id)
        if not contact:
            return None
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE contact SET photo = ?, photo_type = ? WHERE id = ? AND user_id = ?",
            (photo_data, photo_type, contact_id, user_id),
        )
        self.conn.commit()
        return self.get_by_id(contact_id, user_id)

    def delete_photo(self, contact_id: int, user_id: int) -> Optional[Contact]:
        """Удалить фото контакта."""
        contact = self.get_by_id(contact_id, user_id)
        if not contact:
            return None
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE contact SET photo = NULL, photo_type = NULL WHERE id = ? AND user_id = ?",
            (contact_id, user_id),
        )
        self.conn.commit()
        return self.get_by_id(contact_id, user_id)
