"""
Репозиторий для операций CRUD с вложениями.
"""
from typing import List, Optional

from ..connection import Connection
from ..models import Attachment


class AttachmentRepository:
    """Репозиторий для работы с вложениями."""

    def __init__(self, conn: Connection):
        self.conn = conn

    def get_by_note_id(self, note_id: int, user_id: int) -> List[Attachment]:
        """Получить вложения заметки."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.* FROM attachment a
            INNER JOIN note n ON a.note_id = n.id
            WHERE a.note_id = ? AND n.user_id = ?
            ORDER BY a.created_at
        """, (note_id, user_id))
        return [Attachment.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, attachment_id: int, user_id: int) -> Optional[Attachment]:
        """Получить вложение по ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.* FROM attachment a
            INNER JOIN note n ON a.note_id = n.id
            WHERE a.id = ? AND n.user_id = ?
        """, (attachment_id, user_id))
        row = cursor.fetchone()
        return Attachment.from_row(row) if row else None

    def create(self, attachment: Attachment, user_id: int) -> Attachment:
        """Создать вложение."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO attachment (note_id, file_type, file_data, file_size, note, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id
        """, (attachment.note_id, attachment.file_type, attachment.file_data, attachment.file_size, attachment.note, user_id))
        self.conn.commit()
        attachment.id = cursor.lastrowid
        return attachment

    def update_note(self, attachment_id: int, note: str, user_id: int) -> Optional[Attachment]:
        """Обновить примечание к вложению."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE attachment SET note = ? WHERE id = ?
            AND note_id IN (SELECT id FROM note WHERE user_id = ?)
        """, (note, attachment_id, user_id))
        self.conn.commit()
        if cursor.rowcount == 0:
            return None
        return self.get_by_id(attachment_id, user_id)

    def delete(self, attachment_id: int, user_id: int) -> bool:
        """Удалить вложение."""
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM attachment WHERE id = ?
            AND note_id IN (SELECT id FROM note WHERE user_id = ?)
        """, (attachment_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_file_data(self, attachment_id: int, user_id: int) -> Optional[bytes]:
        """Получить бинарные данные файла."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.file_data FROM attachment a
            INNER JOIN note n ON a.note_id = n.id
            WHERE a.id = ? AND n.user_id = ?
        """, (attachment_id, user_id))
        row = cursor.fetchone()
        return row["file_data"] if row else None
