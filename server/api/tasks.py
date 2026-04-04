"""
API эндпоинты для задач.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from db.connection import get_connection
from db.models import Task as TaskModel, Subtask as SubtaskModel, User
from db.repositories.task_repo import TaskRepository
from server.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    SubtaskCreate,
    SubtaskUpdate,
    SubtaskResponse,
    KategoryTaskResponse,
)
from server.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def get_repo():
    conn = get_connection()
    return TaskRepository(conn)


# === Категории ===

@router.get("/categories", response_model=List[KategoryTaskResponse])
def get_categories(current_user: User = Depends(get_current_user)):
    return get_repo().get_categories(user_id=current_user.id)


@router.post("/categories", response_model=KategoryTaskResponse, status_code=201)
def create_category(
    name: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
):
    return get_repo().create_category(name, user_id=current_user.id)


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
):
    deleted = get_repo().delete_category(category_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return {"message": "Категория удалена"}


# === Задачи ===

@router.get("", response_model=List[TaskResponse])
def get_tasks(
    kategory_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
):
    return get_repo().get_all(user_id=current_user.id, kategory_id=kategory_id)


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
):
    task = TaskModel(**data.model_dump())
    return get_repo().create(task, user_id=current_user.id)


@router.get("/search", response_model=List[TaskResponse])
def search_tasks(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
):
    return get_repo().search(user_id=current_user.id, query=q)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
):
    task = get_repo().get_by_id(task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
):
    existing = get_repo().get_by_id(task_id, user_id=current_user.id)
    if not existing:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(existing, field, value)
    updated = get_repo().update(existing, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return updated


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
):
    deleted = get_repo().delete(task_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {"message": "Задача удалена"}


# === Подзадачи ===

@router.get("/{task_id}/subtasks", response_model=List[SubtaskResponse])
def get_subtasks(
    task_id: int,
    current_user: User = Depends(get_current_user),
):
    return get_repo().get_subtasks(task_id, user_id=current_user.id)


@router.post("/{task_id}/subtasks", response_model=SubtaskResponse, status_code=201)
def create_subtask(
    task_id: int,
    data: SubtaskCreate,
    current_user: User = Depends(get_current_user),
):
    subtask = SubtaskModel(**data.model_dump())
    return get_repo().create_subtask(task_id, subtask, user_id=current_user.id)


@router.put("/{task_id}/subtasks/{subtask_id}", response_model=SubtaskResponse)
def update_subtask(
    task_id: int,
    subtask_id: int,
    data: SubtaskUpdate,
    current_user: User = Depends(get_current_user),
):
    existing_list = get_repo().get_subtasks(task_id, user_id=current_user.id)
    existing = next((s for s in existing_list if s.id == subtask_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="Подзадача не найдена")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(existing, field, value)
    updated = get_repo().update_subtask(task_id, subtask_id, existing, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Подзадача не найдена")
    return updated


@router.delete("/{task_id}/subtasks/{subtask_id}")
def delete_subtask(
    task_id: int,
    subtask_id: int,
    current_user: User = Depends(get_current_user),
):
    deleted = get_repo().delete_subtask(task_id, subtask_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Подзадача не найдена")
    return {"message": "Подзадача удалена"}
