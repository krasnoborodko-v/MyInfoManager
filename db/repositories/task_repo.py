"""
Репозиторий для операций CRUD с задачами.
"""
from datetime import datetime
from typing import List, Optional

from ..connection import Connection
from ..models import Task, KategoryTask, Subtask


class TaskRepository:
    """Репозиторий для работы с задачами."""

    def __init__(self, conn: Connection):
        self.conn = conn

    def get_all(self, kategory_id: Optional[int] = None) -> List[Task]:
        """
        Получить все задачи, опционально фильтруя по категории.

        Args:
            kategory_id: ID категории для фильтрации.

        Returns:
            Список задач.
        """
        cursor = self.conn.cursor()

        if kategory_id is not None:
            cursor.execute("""
                SELECT t.id, t.name, t.kategory_id, t.description, t.data_time, 
                       kt.name as kategory_name, t.priority, t.status, t.created_at
                FROM task t
                LEFT JOIN kategory_task kt ON t.kategory_id = kt.id
                WHERE t.kategory_id = ?
                ORDER BY t.data_time
            """, (kategory_id,))
        else:
            cursor.execute("""
                SELECT t.id, t.name, t.kategory_id, t.description, t.data_time, 
                       kt.name as kategory_name, t.priority, t.status, t.created_at
                FROM task t
                LEFT JOIN kategory_task kt ON t.kategory_id = kt.id
                ORDER BY t.data_time
            """)

        return [Task.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """
        Получить задачу по ID.

        Args:
            task_id: ID задачи.

        Returns:
            Задача или None, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id, t.name, t.kategory_id, t.description, t.data_time, 
                   kt.name as kategory_name, t.priority, t.status, t.created_at
            FROM task t
            LEFT JOIN kategory_task kt ON t.kategory_id = kt.id
            WHERE t.id = ?
        """, (task_id,))

        row = cursor.fetchone()
        return Task.from_row(row) if row else None

    def search(self, query: str) -> List[Task]:
        """
        Поиск задач по имени и описанию.

        Args:
            query: Строка поиска.

        Returns:
            Список найденных задач.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id, t.name, t.kategory_id, t.description, t.data_time, 
                   kt.name as kategory_name, t.priority, t.status, t.created_at
            FROM task t
            LEFT JOIN kategory_task kt ON t.kategory_id = kt.id
            WHERE t.name LIKE ? OR t.description LIKE ?
            ORDER BY t.data_time
        """, (f"%{query}%", f"%{query}%"))

        return [Task.from_row(row) for row in cursor.fetchall()]

    def create(self, task: Task) -> Task:
        """
        Создать новую задачу.

        Args:
            task: Задача для создания.

        Returns:
            Созданная задача с присвоенным ID.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO task (name, kategory_id, description, data_time, priority, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task.name, task.kategory_id, task.description, task.data_time, 
              task.priority, task.status))

        self.conn.commit()
        task.id = cursor.lastrowid
        return task

    def update(self, task: Task) -> Optional[Task]:
        """
        Обновить существующую задачу.

        Args:
            task: Задача с обновлёнными данными.

        Returns:
            Обновлённая задача или None, если задача не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE task
            SET name = ?, kategory_id = ?, description = ?, data_time = ?, 
                priority = ?, status = ?
            WHERE id = ?
        """, (task.name, task.kategory_id, task.description, task.data_time, 
              task.priority, task.status, task.id))

        self.conn.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_by_id(task.id)

    def delete(self, task_id: int) -> bool:
        """
        Удалить задачу по ID.

        Args:
            task_id: ID задачи для удаления.

        Returns:
            True, если задача удалена, False, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM task WHERE id = ?", (task_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_categories(self) -> List[KategoryTask]:
        """
        Получить все категории задач.

        Returns:
            Список категорий.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM kategory_task ORDER BY name")
        return [KategoryTask.from_row(row) for row in cursor.fetchall()]

    def get_category_by_id(self, category_id: int) -> Optional[KategoryTask]:
        """
        Получить категорию по ID.

        Args:
            category_id: ID категории.

        Returns:
            Категория или None, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM kategory_task WHERE id = ?", (category_id,))
        row = cursor.fetchone()
        return KategoryTask.from_row(row) if row else None

    def create_category(self, name: str) -> KategoryTask:
        """
        Создать новую категорию задач.

        Args:
            name: Название категории.

        Returns:
            Созданная категория с присвоенным ID.
        """
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO kategory_task (name) VALUES (?)", (name,))
        self.conn.commit()
        return KategoryTask(id=cursor.lastrowid, name=name)

    def delete_category(self, category_id: int) -> bool:
        """
        Удалить категорию задач.

        Args:
            category_id: ID категории для удаления.

        Returns:
            True, если категория удалена, False, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM kategory_task WHERE id = ?", (category_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # === Методы для подзадач ===

    def get_subtasks(self, task_id: int) -> List[Subtask]:
        """
        Получить все подзадачи для задачи.

        Args:
            task_id: ID задачи.

        Returns:
            Список подзадач.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, task_id, title, description, due_date, is_completed, created_at
            FROM subtask
            WHERE task_id = ?
            ORDER BY created_at
        """, (task_id,))

        return [Subtask.from_row(row) for row in cursor.fetchall()]

    def get_subtask_by_id(self, subtask_id: int) -> Optional[Subtask]:
        """
        Получить подзадачу по ID.

        Args:
            subtask_id: ID подзадачи.

        Returns:
            Подзадача или None, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, task_id, title, description, due_date, is_completed, created_at
            FROM subtask
            WHERE id = ?
        """, (subtask_id,))

        row = cursor.fetchone()
        return Subtask.from_row(row) if row else None

    def create_subtask(self, subtask: Subtask) -> Subtask:
        """
        Создать новую подзадачу.

        Args:
            subtask: Подзадача для создания.

        Returns:
            Созданная подзадача с присвоенным ID.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO subtask (task_id, title, description, due_date, is_completed)
            VALUES (?, ?, ?, ?, ?)
        """, (subtask.task_id, subtask.title, subtask.description, subtask.due_date,
              1 if subtask.is_completed else 0))

        self.conn.commit()
        subtask.id = cursor.lastrowid
        return subtask

    def update_subtask(self, subtask: Subtask) -> Optional[Subtask]:
        """
        Обновить существующую подзадачу.

        Args:
            subtask: Подзадача с обновлёнными данными.

        Returns:
            Обновлённая подзадача или None, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE subtask
            SET title = ?, description = ?, due_date = ?, is_completed = ?
            WHERE id = ?
        """, (subtask.title, subtask.description, subtask.due_date,
              1 if subtask.is_completed else 0, subtask.id))

        self.conn.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_subtask_by_id(subtask.id)

    def delete_subtask(self, subtask_id: int) -> bool:
        """
        Удалить подзадачу по ID.

        Args:
            subtask_id: ID подзадачи для удаления.

        Returns:
            True, если подзадача удалена, False, если не найдена.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM subtask WHERE id = ?", (subtask_id,))
        self.conn.commit()
        return cursor.rowcount > 0
