"""
API эндпоинты для получения всех категорий (ресурсы, заметки, задачи).
"""
from typing import List

from fastapi import APIRouter, Depends

from db.connection import get_connection
from db.models import User
from db.repositories.resource_repo import ResourceRepository
from db.repositories.note_repo import NoteRepository
from db.repositories.task_repo import TaskRepository
from server.schemas import (
    KategoryResourceResponse,
    KategoryNoteResponse,
    KategoryTaskResponse,
)
from server.auth import get_current_user

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("/resources", response_model=List[KategoryResourceResponse])
def get_resource_categories(current_user: User = Depends(get_current_user)):
    conn = get_connection()
    return ResourceRepository(conn).get_categories(user_id=current_user.id)


@router.get("/notes", response_model=List[KategoryNoteResponse])
def get_note_categories(current_user: User = Depends(get_current_user)):
    conn = get_connection()
    return NoteRepository(conn).get_categories(user_id=current_user.id)


@router.get("/tasks", response_model=List[KategoryTaskResponse])
def get_task_categories(current_user: User = Depends(get_current_user)):
    conn = get_connection()
    return TaskRepository(conn).get_categories(user_id=current_user.id)
