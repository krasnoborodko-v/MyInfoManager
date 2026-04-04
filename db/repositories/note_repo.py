"""
Репозиторий для операций CRUD с заметками.
Все методы принимают user_id для изоляции данных пользователей.
"""
from datetime import datetime
from typing import List, Optional

from ..connection import Connection
from ..models import Note, KategoryNote


class NoteRepository:
    """Репозиторий для работы с заметками."""

    def __init__(self, conn: Connection):
        self.conn = conn

    def get_all(self, user_id: int, kategory_id: Optional[int] = None, folder_id: Optional[int] = None) -> List[Note]:
        """Получить все заметки пользователя."""
        cursor = self.conn.cursor()
        if folder_id is not None:
            cursor.execute("""
                SELECT n.id, n.name, n.kategory_id, n.note_text, n.data_time, kn.name as kategory_name, n.folder_id
                FROM note n
                LEFT JOIN kategory_note kn ON n.kategory_id = kn.id
                WHERE n.folder_id = ? AND n.user_id = ?
                ORDER BY n.data_time DESC
            """, (folder_id, user_id))
        elif kategory_id is not None:
            cursor.execute("""
                SELECT n.id, n.name, n.kategory_id, n.note_text, n.data_time, kn.name as kategory_name, n.folder_id
                FROM note n
                LEFT JOIN kategory_note kn ON n.kategory_id = kn.id
                WHERE n.kategory_id = ? AND n.user_id = ?
                ORDER BY n.data_time DESC
            """, (kategory_id, user_id))
        else:
            cursor.execute("""
                SELECT n.id, n.name, n.kategory_id, n.note_text, n.data_time, kn.name as kategory_name, n.folder_id
                FROM note n
                LEFT JOIN kategory_note kn ON n.kategory_id = kn.id
                WHERE n.user_id = ?
                ORDER BY n.data_time DESC
            """, (user_id,))
        return [Note.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, note_id: int, user_id: int) -> Optional[Note]:
        """Получить заметку по ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT n.id, n.name, n.kategory_id, n.note_text, n.data_time, kn.name as kategory_name, n.folder_id
            FROM note n
            LEFT JOIN kategory_note kn ON n.kategory_id = kn.id
            WHERE n.id = ? AND n.user_id = ?
        """, (note_id, user_id))
        row = cursor.fetchone()
        return Note.from_row(row) if row else None

    def search(self, user_id: int, query: str) -> List[Note]:
        """Поиск заметок."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT n.id, n.name, n.kategory_id, n.note_text, n.data_time, kn.name as kategory_name, n.folder_id
            FROM note n
            LEFT JOIN kategory_note kn ON n.kategory_id = kn.id
            WHERE n.user_id = ? AND (n.name LIKE ? OR n.note_text LIKE ?)
            ORDER BY n.data_time DESC
        """, (user_id, f"%{query}%", f"%{query}%"))
        return [Note.from_row(row) for row in cursor.fetchall()]

    def create(self, note: Note, user_id: int) -> Note:
        """Создать заметку."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO note (name, kategory_id, note_text, data_time, folder_id, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (note.name, note.kategory_id, note.note_text, note.data_time or datetime.now(), note.folder_id, user_id))
        self.conn.commit()
        note.id = cursor.lastrowid
        return note

    def update(self, note: Note, user_id: int) -> Optional[Note]:
        """Обновить заметку."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE note
            SET name = ?, kategory_id = ?, note_text = ?, data_time = ?, folder_id = ?
            WHERE id = ? AND user_id = ?
        """, (note.name, note.kategory_id, note.note_text, note.data_time, note.folder_id, note.id, user_id))
        self.conn.commit()
        if cursor.rowcount == 0:
            return None
        return self.get_by_id(note.id, user_id)

    def delete(self, note_id: int, user_id: int) -> bool:
        """Удалить заметку."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM note WHERE id = ? AND user_id = ?", (note_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def create_category(self, name: str, user_id: int) -> KategoryNote:
        """Создать категорию заметок."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO kategory_note (name, user_id) VALUES (?, ?)",
            (name, user_id),
        )
        self.conn.commit()
        return KategoryNote(id=cursor.lastrowid, name=name)

    def get_categories(self, user_id: int) -> List[KategoryNote]:
        """Получить категории заметок пользователя."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name FROM kategory_note WHERE user_id = ? ORDER BY name",
            (user_id,),
        )
        return [KategoryNote(id=row["id"], name=row["name"]) for row in cursor.fetchall()]

    def delete_category(self, category_id: int, user_id: int) -> bool:
        """Удалить категорию заметок."""
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM kategory_note WHERE id = ? AND user_id = ?",
            (category_id, user_id),
        )
        self.conn.commit()
        return cursor.rowcount > 0
