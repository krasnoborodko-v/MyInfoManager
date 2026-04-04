"""
API эндпоинты для управления заметками.
"""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Body

from db.connection import get_connection
from db.models import Note as NoteModel
from db.repositories.note_repo import NoteRepository
from server.schemas import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    KategoryNoteResponse,
)


router = APIRouter(prefix="/api/notes", tags=["notes"])


def get_repo():
    """Получить репозиторий заметок."""
    conn = get_connection()
    return NoteRepository(conn)


# === Категории заметок (должны быть перед /{note_id}) ===

@router.get("/categories", response_model=List[KategoryNoteResponse])
def get_categories():
    """Получить список всех категорий заметок."""
    repo = get_repo()
    return repo.get_categories()


@router.post("/categories", response_model=KategoryNoteResponse)
def create_category(name: str = Query(..., min_length=1)):
    """Создать новую категорию заметок."""
    repo = get_repo()
    return repo.create_category(name)


@router.delete("/categories/{category_id}")
def delete_category(category_id: int):
    """Удалить категорию заметок."""
    repo = get_repo()
    deleted = repo.delete_category(category_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    return {"message": "Категория удалена"}


# === Заметки ===

@router.get("", response_model=List[NoteResponse])
def get_notes(kategory_id: Optional[int] = Query(None)):
    """Получить список всех заметок, опционально фильтруя по категории."""
    repo = get_repo()
    notes = repo.get_all(kategory_id=kategory_id)
    return notes


@router.get("/search", response_model=List[NoteResponse])
def search_notes(q: str = Query(..., min_length=1)):
    """Поиск заметок по имени и тексту."""
    repo = get_repo()
    notes = repo.search(q)
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: int):
    """Получить заметку по ID."""
    repo = get_repo()
    note = repo.get_by_id(note_id)

    if note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    return note


@router.post("", response_model=NoteResponse)
def create_note(note: NoteCreate):
    """Создать новую заметку."""
    repo = get_repo()
    model = NoteModel(
        name=note.name,
        kategory_id=note.kategory_id,
        note_text=note.note_text,
        data_time=note.data_time,
    )
    created = repo.create(model)
    return created


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note: NoteUpdate):
    """Обновить существующую заметку."""
    repo = get_repo()
    model = NoteModel(
        id=note_id,
        name=note.name,
        kategory_id=note.kategory_id,
        folder_id=note.folder_id,
        note_text=note.note_text,
        data_time=note.data_time,
    )
    updated = repo.update(model)

    if updated is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    return updated


@router.patch("/{note_id}/folder", response_model=NoteResponse)
def move_note_to_folder(note_id: int, folder_id: Optional[int] = Body(None, embed=True)):
    """Переместить заметку в другую папку (или убрать из папки)."""
    repo = get_repo()
    note = repo.get_by_id(note_id)
    
    if note is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    
    # Обновляем только folder_id
    note.folder_id = folder_id
    updated = repo.update(note)
    
    return updated


@router.delete("/{note_id}")
def delete_note(note_id: int):
    """Удалить заметку."""
    repo = get_repo()
    deleted = repo.delete(note_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    return {"message": "Заметка удалена"}
