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

    def get_all(self, category_id: Optional[int] = None) -> List[Folder]:
        """Получить все папки, опционально фильтруя по категории."""
        cursor = self.conn.cursor()
        
        if category_id:
            cursor.execute("""
                SELECT f.id, f.name, f.parent_id, f.note_category_id, f.created_at,
                       p.name as parent_name
                FROM folder f
                LEFT JOIN folder p ON f.parent_id = p.id
                WHERE f.note_category_id = ?
                ORDER BY f.name
            """, (category_id,))
        else:
            cursor.execute("""
                SELECT f.id, f.name, f.parent_id, f.note_category_id, f.created_at,
                       p.name as parent_name
                FROM folder f
                LEFT JOIN folder p ON f.parent_id = p.id
                ORDER BY f.note_category_id, f.name
            """)
        
        return [Folder.from_row(row) for row in cursor.fetchall()]

    def get_tree(self, category_id: Optional[int] = None) -> List[Folder]:
        """Получить папки в виде дерева."""
        folders = self.get_all(category_id)
        return self._build_tree(folders)

    def _build_tree(self, folders: List[Folder]) -> List[Folder]:
        """Построить дерево из плоского списка."""
        folder_map = {f.id: f for f in folders}
        roots = []
        
        for folder in folders:
            if folder.parent_id is None:
                roots.append(folder)
            elif folder.parent_id in folder_map:
                folder_map[folder.parent_id].children.append(folder)
        
        return roots

    def get_by_id(self, folder_id: int) -> Optional[Folder]:
        """Получить папку по ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT f.id, f.name, f.parent_id, f.note_category_id, f.created_at,
                   p.name as parent_name
            FROM folder f
            LEFT JOIN folder p ON f.parent_id = p.id
            WHERE f.id = ?
        """, (folder_id,))
        
        row = cursor.fetchone()
        return Folder.from_row(row) if row else None

    def create(self, folder: Folder) -> Folder:
        """Создать папку."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO folder (name, parent_id, note_category_id)
            VALUES (?, ?, ?)
        """, (folder.name, folder.parent_id, folder.note_category_id))
        
        self.conn.commit()
        folder.id = cursor.lastrowid
        return folder

    def update(self, folder: Folder) -> Optional[Folder]:
        """Обновить папку."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE folder
            SET name = ?, parent_id = ?, note_category_id = ?
            WHERE id = ?
        """, (folder.name, folder.parent_id, folder.note_category_id, folder.id))
        
        self.conn.commit()
        
        if cursor.rowcount == 0:
            return None
        
        return self.get_by_id(folder.id)

    def delete(self, folder_id: int) -> bool:
        """Удалить папку."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM folder WHERE id = ?", (folder_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_notes(self, folder_id: int) -> List[dict]:
        """Получить все заметки в папке (и подпапках)."""
        cursor = self.conn.cursor()
        
        # Рекурсивно получаем все подпапки
        def get_all_subfolder_ids(fid: int) -> List[int]:
            cursor.execute("SELECT id FROM folder WHERE parent_id = ?", (fid,))
            subfolder_ids = [row[0] for row in cursor.fetchall()]
            all_ids = [fid] + subfolder_ids
            for sub_id in subfolder_ids:
                all_ids.extend(get_all_subfolder_ids(sub_id))
            return all_ids
        
        all_folder_ids = get_all_subfolder_ids(folder_id)
        
        # Получаем заметки из всех папок
        placeholders = ','.join('?' * len(all_folder_ids))
        cursor.execute(f"""
            SELECT n.id, n.name, n.kategory_id, n.note_text, n.data_time
            FROM note n
            WHERE n.kategory_id IN (
                SELECT DISTINCT note_category_id FROM folder WHERE id IN ({placeholders})
            )
            ORDER BY n.data_time DESC
        """, all_folder_ids)
        
        return [dict(row) for row in cursor.fetchall()]
