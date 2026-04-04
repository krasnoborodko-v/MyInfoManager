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

    def get_all(self) -> List[Tag]:
        """Получить все теги."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, color, created_at FROM tag ORDER BY name")
        return [Tag.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """Получить тег по ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, color, created_at FROM tag WHERE id = ?", (tag_id,))
        row = cursor.fetchone()
        return Tag.from_row(row) if row else None

    def get_by_name(self, name: str) -> Optional[Tag]:
        """Получить тег по имени."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, color, created_at FROM tag WHERE name = ?", (name,))
        row = cursor.fetchone()
        return Tag.from_row(row) if row else None

    def create(self, tag: Tag) -> Tag:
        """Создать тег."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tag (name, color)
            VALUES (?, ?)
        """, (tag.name, tag.color))
        
        self.conn.commit()
        tag.id = cursor.lastrowid
        return tag

    def update(self, tag: Tag) -> Optional[Tag]:
        """Обновить тег."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tag
            SET name = ?, color = ?
            WHERE id = ?
        """, (tag.name, tag.color, tag.id))
        
        self.conn.commit()
        
        if cursor.rowcount == 0:
            return None
        
        return self.get_by_id(tag.id)

    def delete(self, tag_id: int) -> bool:
        """Удалить тег."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tag WHERE id = ?", (tag_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # === Связи заметок с тегами ===

    def get_tags_for_note(self, note_id: int) -> List[Tag]:
        """Получить все теги заметки."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id, t.name, t.color, t.created_at
            FROM tag t
            JOIN note_tag nt ON t.id = nt.tag_id
            WHERE nt.note_id = ?
            ORDER BY t.name
        """, (note_id,))
        
        return [Tag.from_row(row) for row in cursor.fetchall()]

    def add_tag_to_note(self, note_id: int, tag_id: int) -> bool:
        """Добавить тег к заметке."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO note_tag (note_id, tag_id)
                VALUES (?, ?)
            """, (note_id, tag_id))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False

    def remove_tag_from_note(self, note_id: int, tag_id: int) -> bool:
        """Удалить тег из заметки."""
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM note_tag
            WHERE note_id = ? AND tag_id = ?
        """, (note_id, tag_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def set_tags_for_note(self, note_id: int, tag_ids: List[int]) -> None:
        """Установить все теги для заметки (заменяет старые)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM note_tag WHERE note_id = ?", (note_id,))
        
        for tag_id in tag_ids:
            cursor.execute("""
                INSERT OR IGNORE INTO note_tag (note_id, tag_id)
                VALUES (?, ?)
            """, (note_id, tag_id))
        
        self.conn.commit()

    def get_notes_by_tag(self, tag_id: int) -> List[dict]:
        """Получить все заметки с тегом."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT n.id, n.name, n.kategory_id, n.note_text, n.data_time
            FROM note n
            JOIN note_tag nt ON n.id = nt.note_id
            WHERE nt.tag_id = ?
            ORDER BY n.data_time DESC
        """, (tag_id,))
        
        return [dict(row) for row in cursor.fetchall()]
