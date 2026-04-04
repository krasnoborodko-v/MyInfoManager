"""
API эндпоинты для папок и тегов.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body

from db.connection import get_connection
from db.models import Folder, Tag, User
from db.repositories.folder_repo import FolderRepository
from db.repositories.tag_repo import TagRepository
from server.schemas import (
    FolderCreate,
    FolderUpdate,
    FolderResponse,
    TagCreate,
    TagUpdate,
    TagResponse,
)
from server.auth import get_current_user

router = APIRouter(prefix="/api", tags=["folders", "tags"])


# === Папки ===

@router.get("/folders", response_model=List[FolderResponse])
def get_folders(
    category_id: Optional[int] = Query(None),
    tree: bool = Query(False),
    current_user: User = Depends(get_current_user),
):
    conn = get_connection()
    repo = FolderRepository(conn)
    if tree:
        return repo.get_tree(user_id=current_user.id, category_id=category_id)
    return repo.get_all(user_id=current_user.id, category_id=category_id)


@router.post("/folders", response_model=FolderResponse, status_code=201)
def create_folder(
    data: FolderCreate,
    current_user: User = Depends(get_current_user),
):
    conn = get_connection()
    repo = FolderRepository(conn)
    folder = Folder(name=data.name, parent_id=data.parent_id, note_category_id=data.note_category_id)
    return repo.create(folder, user_id=current_user.id)


@router.put("/folders/{folder_id}", response_model=FolderResponse)
def update_folder(
    folder_id: int,
    data: FolderUpdate,
    current_user: User = Depends(get_current_user),
):
    conn = get_connection()
    repo = FolderRepository(conn)
    existing = repo.get_by_id(folder_id, user_id=current_user.id)
    if not existing:
        raise HTTPException(status_code=404, detail="Папка не найдена")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(existing, field, value)
    updated = repo.update(existing, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Папка не найдена")
    return updated


@router.delete("/folders/{folder_id}")
def delete_folder(
    folder_id: int,
    current_user: User = Depends(get_current_user),
):
    conn = get_connection()
    repo = FolderRepository(conn)
    deleted = repo.delete(folder_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Папка не найдена")
    return {"message": "Папка удалена"}


# === Теги ===

@router.get("/tags", response_model=List[TagResponse])
def get_tags(current_user: User = Depends(get_current_user)):
    conn = get_connection()
    return TagRepository(conn).get_all(user_id=current_user.id)


@router.post("/tags", response_model=TagResponse, status_code=201)
def create_tag(
    data: TagCreate,
    current_user: User = Depends(get_current_user),
):
    conn = get_connection()
    repo = TagRepository(conn)
    tag = Tag(name=data.name, color=data.color)
    return repo.create(tag, user_id=current_user.id)


@router.put("/tags/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    data: TagUpdate,
    current_user: User = Depends(get_current_user),
):
    conn = get_connection()
    repo = TagRepository(conn)
    existing = repo.get_by_id(tag_id, user_id=current_user.id)
    if not existing:
        raise HTTPException(status_code=404, detail="Тег не найден")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(existing, field, value)
    updated = repo.update(existing, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Тег не найден")
    return updated


@router.delete("/tags/{tag_id}")
def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
):
    conn = get_connection()
    repo = TagRepository(conn)
    deleted = repo.delete(tag_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Тег не найден")
    return {"message": "Тег удалён"}


# === Теги заметки ===

@router.get("/notes/{note_id}/tags", response_model=List[TagResponse])
def get_note_tags(
    note_id: int,
    current_user: User = Depends(get_current_user),
):
    conn = get_connection()
    return TagRepository(conn).get_for_note(note_id, user_id=current_user.id)


@router.post("/notes/{note_id}/tags", status_code=201)
def add_tag_to_note(
    note_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
):
    conn = get_connection()
    repo = TagRepository(conn)
    added = repo.add_tag_to_note(note_id, data["tag_id"], user_id=current_user.id)
    if not added:
        raise HTTPException(status_code=404, detail="Тег или заметка не найдены")
    return {"message": "Тег добавлен"}


@router.delete("/notes/{note_id}/tags/{tag_id}")
def remove_tag_from_note(
    note_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_user),
):
    conn = get_connection()
    repo = TagRepository(conn)
    deleted = repo.remove_tag_from_note(note_id, tag_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Тег не найден в заметке")
    return {"message": "Тег удалён из заметки"}


@router.put("/notes/{note_id}/tags")
def set_tags_for_note(
    note_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
):
    conn = get_connection()
    repo = TagRepository(conn)
    repo.set_tags_for_note(note_id, data.get("tag_ids", []), user_id=current_user.id)
    return {"message": "Теги установлены"}
