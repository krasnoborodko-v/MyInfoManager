"""
Репозиторий для операций с папками заметок.
"""
from typing import List, Optional

from ..connection import Connection
from ..models import Folder


class FolderRepository:
    """Репозиторий для работы с папками."""

    def __init__(self, conn: Connection):
        self.conn = conn

    def get_all(self, user_id: int, category_id: Optional[int] = None) -> List[Folder]:
        """Получить все папки пользователя."""
        cursor = self.conn.cursor()
        if category_id is not None:
            cursor.execute("""
                SELECT * FROM folder WHERE user_id = ? AND note_category_id = ? ORDER BY name
            """, (user_id, category_id))
        else:
            cursor.execute("""
                SELECT * FROM folder WHERE user_id = ? ORDER BY name
            """, (user_id,))
        return [Folder.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, folder_id: int, user_id: int) -> Optional[Folder]:
        """Получить папку по ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM folder WHERE id = ? AND user_id = ?", (folder_id, user_id))
        row = cursor.fetchone()
        return Folder.from_row(row) if row else None

    def create(self, folder: Folder, user_id: int) -> Folder:
        """Создать папку."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO folder (name, parent_id, note_category_id, user_id)
            VALUES (?, ?, ?, ?)
            RETURNING id
        """, (folder.name, folder.parent_id, folder.note_category_id, user_id))
        self.conn.commit()
        folder.id = cursor.lastrowid
        return folder

    def update(self, folder: Folder, user_id: int) -> Optional[Folder]:
        """Обновить папку."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE folder SET name = ?, parent_id = ?, note_category_id = ?
            WHERE id = ? AND user_id = ?
        """, (folder.name, folder.parent_id, folder.note_category_id, folder.id, user_id))
        self.conn.commit()
        if cursor.rowcount == 0:
            return None
        return self.get_by_id(folder.id, user_id)

    def delete(self, folder_id: int, user_id: int) -> bool:
        """Удалить папку."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM folder WHERE id = ? AND user_id = ?", (folder_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_tree(self, user_id: int, category_id: Optional[int] = None) -> List[dict]:
        """Получить дерево папок."""
        folders = self.get_all(user_id, category_id)
        return self._build_tree(folders)

    def _build_tree(self, folders: List[Folder], parent_id: Optional[int] = None) -> List[dict]:
        """Построить иерархию."""
        result = []
        for f in folders:
            if f.parent_id == parent_id:
                children = self._build_tree(folders, f.id)
                result.append({**f.to_dict(), "children": children})
        return result
