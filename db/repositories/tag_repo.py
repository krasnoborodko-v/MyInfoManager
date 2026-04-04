"""
Репозиторий для операций с тегами.
"""
from typing import List, Optional

from ..connection import Connection
from ..models import Tag


class TagRepository:
    """Репозиторий для работы с тегами."""

    def __init__(self, conn: Connection):
        self.conn = conn

    def get_all(self, user_id: int) -> List[Tag]:
        """Получить все теги пользователя."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tag WHERE user_id = ? ORDER BY name", (user_id,))
        return [Tag.from_row(row) for row in cursor.fetchall()]

    def create(self, tag: Tag, user_id: int) -> Tag:
        """Создать тег."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tag (name, color, user_id) VALUES (?, ?, ?)",
            (tag.name, tag.color or '#008888', user_id),
        )
        self.conn.commit()
        tag.id = cursor.lastrowid
        return tag

    def update(self, tag: Tag, user_id: int) -> Optional[Tag]:
        """Обновить тег."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE tag SET name = ?, color = ? WHERE id = ? AND user_id = ?",
            (tag.name, tag.color, tag.id, user_id),
        )
        self.conn.commit()
        if cursor.rowcount == 0:
            return None
        return self.get_by_id(tag.id, user_id)

    def get_by_id(self, tag_id: int, user_id: int) -> Optional[Tag]:
        """Получить тег по ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tag WHERE id = ? AND user_id = ?", (tag_id, user_id))
        row = cursor.fetchone()
        return Tag.from_row(row) if row else None

    def delete(self, tag_id: int, user_id: int) -> bool:
        """Удалить тег."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tag WHERE id = ? AND user_id = ?", (tag_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0

    # --- Связи тегов с заметками ---

    def get_for_note(self, note_id: int, user_id: int) -> List[Tag]:
        """Получить теги заметки."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.* FROM tag t
            INNER JOIN note_tag nt ON t.id = nt.tag_id
            INNER JOIN note n ON nt.note_id = n.id
            WHERE nt.note_id = ? AND n.user_id = ?
            ORDER BY t.name
        """, (note_id, user_id))
        return [Tag.from_row(row) for row in cursor.fetchall()]

    def add_tag_to_note(self, note_id: int, tag_id: int, user_id: int) -> bool:
        """Добавить тег к заметке."""
        tag = self.get_by_id(tag_id, user_id)
        if not tag:
            return False
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO note_tag (note_id, tag_id) VALUES (?, ?)",
            (note_id, tag_id),
        )
        self.conn.commit()
        return True

    def remove_tag_from_note(self, note_id: int, tag_id: int, user_id: int) -> bool:
        """Удалить тег из заметки."""
        tag = self.get_by_id(tag_id, user_id)
        if not tag:
            return False
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM note_tag WHERE note_id = ? AND tag_id = ?", (note_id, tag_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def set_tags_for_note(self, note_id: int, tag_ids: List[int], user_id: int) -> None:
        """Установить теги для заметки (заменить все)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM note_tag WHERE note_id = ?", (note_id,))
        for tid in tag_ids:
            tag = self.get_by_id(tid, user_id)
            if tag:
                cursor.execute(
                    "INSERT OR IGNORE INTO note_tag (note_id, tag_id) VALUES (?, ?)",
                    (note_id, tid),
                )
        self.conn.commit()
