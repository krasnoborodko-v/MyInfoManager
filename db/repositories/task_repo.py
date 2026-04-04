"""
Репозиторий для операций CRUD с задачами.
Все методы принимают user_id для изоляции данных пользователей.
"""
from datetime import datetime
from typing import List, Optional

from ..connection import Connection
from ..models import Task, KategoryTask, Subtask


class TaskRepository:
    """Репозиторий для работы с задачами."""

    def __init__(self, conn: Connection):
        self.conn = conn

    def get_all(self, user_id: int, kategory_id: Optional[int] = None) -> List[Task]:
        """Получить все задачи пользователя."""
        cursor = self.conn.cursor()
        if kategory_id is not None:
            cursor.execute("""
                SELECT t.id, t.name, t.kategory_id, t.description, t.data_time, t.priority, t.status, t.created_at, kt.name as kategory_name
                FROM task t
                LEFT JOIN kategory_task kt ON t.kategory_id = kt.id
                WHERE t.kategory_id = ? AND t.user_id = ?
                ORDER BY t.created_at DESC
            """, (kategory_id, user_id))
        else:
            cursor.execute("""
                SELECT t.id, t.name, t.kategory_id, t.description, t.data_time, t.priority, t.status, t.created_at, kt.name as kategory_name
                FROM task t
                LEFT JOIN kategory_task kt ON t.kategory_id = kt.id
                WHERE t.user_id = ?
                ORDER BY t.created_at DESC
            """, (user_id,))
        return [Task.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        """Получить задачу по ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id, t.name, t.kategory_id, t.description, t.data_time, t.priority, t.status, t.created_at, kt.name as kategory_name
            FROM task t
            LEFT JOIN kategory_task kt ON t.kategory_id = kt.id
            WHERE t.id = ? AND t.user_id = ?
        """, (task_id, user_id))
        row = cursor.fetchone()
        return Task.from_row(row) if row else None

    def search(self, user_id: int, query: str) -> List[Task]:
        """Поиск задач."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id, t.name, t.kategory_id, t.description, t.data_time, t.priority, t.status, t.created_at, kt.name as kategory_name
            FROM task t
            LEFT JOIN kategory_task kt ON t.kategory_id = kt.id
            WHERE t.user_id = ? AND (t.name LIKE ? OR t.description LIKE ?)
            ORDER BY t.created_at DESC
        """, (user_id, f"%{query}%", f"%{query}%"))
        return [Task.from_row(row) for row in cursor.fetchall()]

    def create(self, task: Task, user_id: int) -> Task:
        """Создать задачу."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO task (name, kategory_id, description, data_time, priority, status, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (task.name, task.kategory_id, task.description, task.data_time, task.priority or 'medium', task.status or 'not_done', user_id))
        self.conn.commit()
        task.id = cursor.lastrowid
        return task

    def update(self, task: Task, user_id: int) -> Optional[Task]:
        """Обновить задачу."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE task
            SET name = ?, kategory_id = ?, description = ?, data_time = ?, priority = ?, status = ?
            WHERE id = ? AND user_id = ?
        """, (task.name, task.kategory_id, task.description, task.data_time, task.priority, task.status, task.id, user_id))
        self.conn.commit()
        if cursor.rowcount == 0:
            return None
        return self.get_by_id(task.id, user_id)

    def delete(self, task_id: int, user_id: int) -> bool:
        """Удалить задачу."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM task WHERE id = ? AND user_id = ?", (task_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def create_category(self, name: str, user_id: int) -> KategoryTask:
        """Создать категорию задач."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO kategory_task (name, user_id) VALUES (?, ?)",
            (name, user_id),
        )
        self.conn.commit()
        return KategoryTask(id=cursor.lastrowid, name=name)

    def get_categories(self, user_id: int) -> List[KategoryTask]:
        """Получить категории задач пользователя."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name FROM kategory_task WHERE user_id = ? ORDER BY name",
            (user_id,),
        )
        return [KategoryTask(id=row["id"], name=row["name"]) for row in cursor.fetchall()]

    def delete_category(self, category_id: int, user_id: int) -> bool:
        """Удалить категорию задач."""
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM kategory_task WHERE id = ? AND user_id = ?",
            (category_id, user_id),
        )
        self.conn.commit()
        return cursor.rowcount > 0

    # --- Подзадачи ---

    def get_subtasks(self, task_id: int, user_id: int) -> List[Subtask]:
        """Получить подзадачи задачи."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.* FROM subtask s
            INNER JOIN task t ON s.task_id = t.id
            WHERE s.task_id = ? AND t.user_id = ?
            ORDER BY s.created_at
        """, (task_id, user_id))
        return [Subtask(
            id=row["id"], task_id=row["task_id"], title=row["title"],
            description=row.get("description"), due_date=row.get("due_date"),
            is_completed=bool(row.get("is_completed", 0)),
            created_at=row.get("created_at"),
        ) for row in cursor.fetchall()]

    def create_subtask(self, task_id: int, subtask: Subtask, user_id: int) -> Subtask:
        """Создать подзадачу."""
        # Проверяем что задача принадлежит пользователю
        task = self.get_by_id(task_id, user_id)
        if not task:
            raise ValueError("Task not found or access denied")
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO subtask (task_id, title, description, due_date, is_completed)
            VALUES (?, ?, ?, ?, ?)
        """, (task_id, subtask.title, subtask.description, subtask.due_date, int(subtask.is_completed or False)))
        self.conn.commit()
        subtask.id = cursor.lastrowid
        subtask.task_id = task_id
        return subtask

    def update_subtask(self, task_id: int, subtask_id: int, subtask: Subtask, user_id: int) -> Optional[Subtask]:
        """Обновить подзадачу."""
        task = self.get_by_id(task_id, user_id)
        if not task:
            return None
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE subtask
            SET title = ?, description = ?, due_date = ?, is_completed = ?
            WHERE id = ? AND task_id = ?
        """, (subtask.title, subtask.description, subtask.due_date, int(subtask.is_completed or False), subtask_id, task_id))
        self.conn.commit()
        if cursor.rowcount == 0:
            return None
        return self.get_subtasks(task_id, user_id)[0] if self.get_subtasks(task_id, user_id) else None

    def delete_subtask(self, task_id: int, subtask_id: int, user_id: int) -> bool:
        """Удалить подзадачу."""
        task = self.get_by_id(task_id, user_id)
        if not task:
            return False
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM subtask WHERE id = ? AND task_id = ?", (subtask_id, task_id))
        self.conn.commit()
        return cursor.rowcount > 0
