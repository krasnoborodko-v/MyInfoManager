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

    def get_by_note_id(self, note_id: int) -> List[Attachment]:
        """
        Получить все вложения для заметки.

        Args:
            note_id: ID заметки.

        Returns:
            Список вложений.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, note_id, file_type, file_data, file_size, note, created_at
            FROM attachment
            WHERE note_id = ?
            ORDER BY created_at
        """, (note_id,))

        return [Attachment.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """
        Получить вложение по ID.

        Args:
            attachment_id: ID вложения.

        Returns:
            Вложение или None, если не найдено.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, note_id, file_type, file_data, file_size, note, created_at
            FROM attachment
            WHERE id = ?
        """, (attachment_id,))

        row = cursor.fetchone()
        return Attachment.from_row(row) if row else None

    def create(self, attachment: Attachment) -> Attachment:
        """
        Создать вложение.

        Args:
            attachment: Вложение для создания.

        Returns:
            Созданное вложение с присвоенным ID.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO attachment (note_id, file_type, file_data, file_size, note)
            VALUES (?, ?, ?, ?, ?)
        """, (
            attachment.note_id,
            attachment.file_type,
            attachment.file_data,
            attachment.file_size,
            attachment.note
        ))

        self.conn.commit()
        attachment.id = cursor.lastrowid
        return attachment

    def update(self, attachment: Attachment) -> Optional[Attachment]:
        """
        Обновить вложение (примечание).

        Args:
            attachment: Вложение с обновлёнными данными.

        Returns:
            Обновлённое вложение или None, если не найдено.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE attachment
            SET note = ?
            WHERE id = ?
        """, (attachment.note, attachment.id))

        self.conn.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_by_id(attachment.id)

    def delete(self, attachment_id: int) -> bool:
        """
        Удалить вложение.

        Args:
            attachment_id: ID вложения для удаления.

        Returns:
            True, если вложение удалено, False, если не найдено.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM attachment WHERE id = ?", (attachment_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_by_note_id(self, note_id: int) -> int:
        """
        Удалить все вложения заметки.

        Args:
            note_id: ID заметки.

        Returns:
            Количество удалённых вложений.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM attachment WHERE note_id = ?", (note_id,))
        self.conn.commit()
        return cursor.rowcount
