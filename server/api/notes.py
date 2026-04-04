"""
API эндпоинты для заметок.
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Body

from db.connection import get_connection
from db.models import Note as NoteModel, User
from db.repositories.note_repo import NoteRepository
from server.schemas import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    KategoryNoteResponse,
)
from server.auth import get_current_user

router = APIRouter(prefix="/api/notes", tags=["notes"])


def get_repo():
    conn = get_connection()
    return NoteRepository(conn)


# === Категории ===

@router.get("/categories", response_model=List[KategoryNoteResponse])
def get_categories(current_user: User = Depends(get_current_user)):
    return get_repo().get_categories(user_id=current_user.id)


@router.post("/categories", response_model=KategoryNoteResponse, status_code=201)
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


# === Заметки ===

@router.get("", response_model=List[NoteResponse])
def get_notes(
    kategory_id: Optional[int] = Query(None),
    folder_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
):
    return get_repo().get_all(user_id=current_user.id, kategory_id=kategory_id, folder_id=folder_id)


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(
    data: NoteCreate,
    current_user: User = Depends(get_current_user),
):
    note = NoteModel(**data.model_dump())
    if not note.data_time:
        note.data_time = datetime.now()
    return get_repo().create(note, user_id=current_user.id)


@router.get("/search", response_model=List[NoteResponse])
def search_notes(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
):
    return get_repo().search(user_id=current_user.id, query=q)


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
):
    note = get_repo().get_by_id(note_id, user_id=current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return note


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    data: NoteUpdate,
    current_user: User = Depends(get_current_user),
):
    existing = get_repo().get_by_id(note_id, user_id=current_user.id)
    if not existing:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(existing, field, value)
    updated = get_repo().update(existing, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return updated


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
):
    deleted = get_repo().delete(note_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return {"message": "Заметка удалена"}
