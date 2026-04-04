"""
API эндпоинты для управления категориями (общие операции).
"""
from typing import List

from fastapi import APIRouter

from db.connection import get_connection
from db.repositories.resource_repo import ResourceRepository
from db.repositories.note_repo import NoteRepository
from db.repositories.task_repo import TaskRepository
from server.schemas import (
    KategoryResourceResponse,
    KategoryNoteResponse,
    KategoryTaskResponse,
)


router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("/resources", response_model=List[KategoryResourceResponse])
def get_resource_categories():
    """Получить все категории ресурсов."""
    conn = get_connection()
    repo = ResourceRepository(conn)
    return repo.get_categories()


@router.get("/notes", response_model=List[KategoryNoteResponse])
def get_note_categories():
    """Получить все категории заметок."""
    conn = get_connection()
    repo = NoteRepository(conn)
    return repo.get_categories()


@router.get("/tasks", response_model=List[KategoryTaskResponse])
def get_task_categories():
    """Получить все категории задач."""
    conn = get_connection()
    repo = TaskRepository(conn)
    return repo.get_categories()
