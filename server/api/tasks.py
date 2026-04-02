"""
API эндпоинты для управления задачами.
"""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query # type: ignore

from db.database import get_connection
from db.models import Task as TaskModel, Subtask as SubtaskModel
from db.repositories.task_repo import TaskRepository
from server.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    KategoryTaskResponse,
    SubtaskCreate,
    SubtaskUpdate,
    SubtaskResponse,
)


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def get_repo():
    """Получить репозиторий задач."""
    conn = get_connection()
    return TaskRepository(conn)


# === Категории задач (должны быть перед /{task_id}) ===

@router.get("/categories", response_model=List[KategoryTaskResponse])
def get_categories():
    """Получить список всех категорий задач."""
    repo = get_repo()
    return repo.get_categories()


@router.post("/categories", response_model=KategoryTaskResponse)
def create_category(name: str = Query(..., min_length=1)):
    """Создать новую категорию задач."""
    repo = get_repo()
    return repo.create_category(name)


@router.delete("/categories/{category_id}")
def delete_category(category_id: int):
    """Удалить категорию задач."""
    repo = get_repo()
    deleted = repo.delete_category(category_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    return {"message": "Категория удалена"}


# === Задачи ===

@router.get("", response_model=List[TaskResponse])
def get_tasks(kategory_id: Optional[int] = Query(None)):
    """Получить список всех задач, опционально фильтруя по категории."""
    repo = get_repo()
    tasks = repo.get_all(kategory_id=kategory_id)
    return tasks


@router.get("/search", response_model=List[TaskResponse])
def search_tasks(q: str = Query(..., min_length=1)):
    """Поиск задач по имени и описанию."""
    repo = get_repo()
    tasks = repo.search(q)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    """Получить задачу по ID."""
    repo = get_repo()
    task = repo.get_by_id(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return task


@router.post("", response_model=TaskResponse)
def create_task(task: TaskCreate):
    """Создать новую задачу."""
    repo = get_repo()
    model = TaskModel(
        name=task.name,
        kategory_id=task.kategory_id,
        description=task.description,
        data_time=task.data_time,
        priority=task.priority,
        status=task.status,
    )
    created = repo.create(model)
    return created


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate):
    """Обновить существующую задачу."""
    repo = get_repo()
    model = TaskModel(
        id=task_id,
        name=task.name,
        kategory_id=task.kategory_id,
        description=task.description,
        data_time=task.data_time,
        priority=task.priority,
        status=task.status,
    )
    updated = repo.update(model)

    if updated is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return updated


@router.delete("/{task_id}")
def delete_task(task_id: int):
    """Удалить задачу."""
    repo = get_repo()
    deleted = repo.delete(task_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return {"message": "Задача удалена"}


# === Подзадачи ===

@router.get("/{task_id}/subtasks", response_model=List[SubtaskResponse])
def get_subtasks(task_id: int):
    """Получить все подзадачи для задачи."""
    repo = get_repo()
    
    # Проверяем существование задачи
    task = repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return repo.get_subtasks(task_id)


@router.post("/{task_id}/subtasks", response_model=SubtaskResponse)
def create_subtask(task_id: int, subtask: SubtaskCreate):
    """Создать новую подзадачу."""
    repo = get_repo()
    
    # Проверяем существование задачи
    task = repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    model = SubtaskModel(
        task_id=task_id,
        title=subtask.title,
        due_date=subtask.due_date,
        is_completed=subtask.is_completed,
    )
    created = repo.create_subtask(model)
    return created


@router.put("/{task_id}/subtasks/{subtask_id}", response_model=SubtaskResponse)
def update_subtask(task_id: int, subtask_id: int, subtask: SubtaskUpdate):
    """Обновить существующую подзадачу."""
    repo = get_repo()
    
    # Проверяем существование задачи
    task = repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    # Получаем подзадачу
    existing = repo.get_subtask_by_id(subtask_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Подзадача не найдена")
    
    # Обновляем только указанные поля
    model = SubtaskModel(
        id=subtask_id,
        task_id=task_id,
        title=subtask.title if subtask.title is not None else existing.title,
        due_date=subtask.due_date if subtask.due_date is not None else existing.due_date,
        is_completed=subtask.is_completed if subtask.is_completed is not None else existing.is_completed,
    )
    updated = repo.update_subtask(model)
    return updated


@router.delete("/{task_id}/subtasks/{subtask_id}")
def delete_subtask(task_id: int, subtask_id: int):
    """Удалить подзадачу."""
    repo = get_repo()
    
    # Проверяем существование задачи
    task = repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    deleted = repo.delete_subtask(subtask_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Подзадача не найдена")

    return {"message": "Подзадача удалена"}
