"""
Репозиторий для операций CRUD с заметками.
"""
from datetime import datetime
from typing import List, Optional

from ..connection import Connection
from ..models import Note, KategoryNote


class NoteRepository:
    """Репозиторий для работы с заметками."""

    def __init__(self, conn: Connection):
        self.conn = conn
    
    def get_all(self, kategory_id: Optional[int] = None, folder_id: Optional[int] = None) -> List[Note]:
        """
        Получить все заметки, опционально фильтруя по категории или папке.
        
        Args:
            kategory_id: ID категории для фильтрации.
            folder_id: ID папки для фильтрации.
        
        Returns:
            Список заметок.
        """
        cursor = self.conn.cursor()
        
        if folder_id is not None:
            cursor.execute("""
                SELECT n.id, n.name, n.kategory_id, n.note_text, n.data_time, kn.name as kategory_name, n.folder_id
                FROM note n
                LEFT JOIN kategory_note kn ON n.kategory_id = kn.id
                WHERE n.folder_id = ?
                ORDER BY n.data_time DESC
            """, (folder_id,))
        elif kategory_id is not None:
            cursor.execute("""
                SELECT n.id, n.name, n.kategory_id, n.note_text, n.data_time, kn.name as kategory_name, n.folder_id
                FROM note n
                LEFT JOIN kategory_note kn ON n.kategory_id = kn.id
                WHERE n.kategory_id = ?
                ORDER BY n.data_time DESC
            """, (kategory_id,))
        else:
            cursor.execute("""
                SELECT n.id, n.name, n.kategory_id, n.note_text, n.data_time, kn.name as kategory_name, n.folder_id
                FROM note n
                LEFT JOIN kategory_note kn ON n.kategory_id = kn.id
                ORDER BY n.data_time DESC
            """)
        
        return [Note.from_row(row) for row in cursor.fetchall()]
    
    def get_by_id(self, note_id: int) -> Optional[Note]:
        """
        Получить заметку по ID.
        
        Args:
            note_id: ID заметки.
        
        Returns:
            Заметка или None, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT n.id, n.name, n.kategory_id, n.note_text, n.data_time, kn.name as kategory_name, n.folder_id
            FROM note n
            LEFT JOIN kategory_note kn ON n.kategory_id = kn.id
            WHERE n.id = ?
        """, (note_id,))
        
        row = cursor.fetchone()
        return Note.from_row(row) if row else None
    
    def search(self, query: str) -> List[Note]:
        """
        Поиск заметок по имени и тексту.
        
        Args:
            query: Строка поиска.
        
        Returns:
            Список найденных заметок.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT n.id, n.name, n.kategory_id, n.note_text, n.data_time, kn.name as kategory_name, n.folder_id
            FROM note n
            LEFT JOIN kategory_note kn ON n.kategory_id = kn.id
            WHERE n.name LIKE ? OR n.note_text LIKE ?
            ORDER BY n.data_time DESC
        """, (f"%{query}%", f"%{query}%"))
        
        return [Note.from_row(row) for row in cursor.fetchall()]
    
    def create(self, note: Note) -> Note:
        """
        Создать новую заметку.
        
        Args:
            note: Заметка для создания.
        
        Returns:
            Созданная заметка с присвоенным ID.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO note (name, kategory_id, folder_id, note_text, data_time)
            VALUES (?, ?, ?, ?, ?)
        """, (note.name, note.kategory_id, note.folder_id, note.note_text, note.data_time))

        self.conn.commit()
        note.id = cursor.lastrowid
        return note

    def update(self, note: Note) -> Optional[Note]:
        """
        Обновить существующую заметку.

        Args:
            note: Заметка с обновлёнными данными.

        Returns:
            Обновлённая заметка или None, если заметка не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE note
            SET name = ?, kategory_id = ?, folder_id = ?, note_text = ?, data_time = ?
            WHERE id = ?
        """, (note.name, note.kategory_id, note.folder_id, note.note_text, note.data_time, note.id))
        
        self.conn.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_by_id(note.id)

    def delete(self, note_id: int) -> bool:
        """
        Удалить заметку по ID.
        
        Args:
            note_id: ID заметки для удаления.
        
        Returns:
            True, если заметка удалена, False, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM note WHERE id = ?", (note_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_categories(self) -> List[KategoryNote]:
        """
        Получить все категории заметок.
        
        Returns:
            Список категорий.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM kategory_note ORDER BY name")
        return [KategoryNote.from_row(row) for row in cursor.fetchall()]
    
    def get_category_by_id(self, category_id: int) -> Optional[KategoryNote]:
        """
        Получить категорию по ID.
        
        Args:
            category_id: ID категории.
        
        Returns:
            Категория или None, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM kategory_note WHERE id = ?", (category_id,))
        row = cursor.fetchone()
        return KategoryNote.from_row(row) if row else None
    
    def create_category(self, name: str) -> KategoryNote:
        """
        Создать новую категорию заметок.
        
        Args:
            name: Название категории.
        
        Returns:
            Созданная категория с присвоенным ID.
        """
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO kategory_note (name) VALUES (?)", (name,))
        self.conn.commit()
        return KategoryNote(id=cursor.lastrowid, name=name)
    
    def delete_category(self, category_id: int) -> bool:
        """
        Удалить категорию заметок.
        
        Args:
            category_id: ID категории для удаления.
        
        Returns:
            True, если категория удалена, False, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM kategory_note WHERE id = ?", (category_id,))
        self.conn.commit()
        return cursor.rowcount > 0
