"""
API эндпоинты для управления папками и тегами.
"""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Body

from db.connection import get_connection
from db.models import Folder, Tag
from db.repositories.folder_repo import FolderRepository
from db.repositories.tag_repo import TagRepository


router = APIRouter(prefix="/api", tags=["folders", "tags"])


def get_folder_repo():
    conn = get_connection()
    return FolderRepository(conn)


def get_tag_repo():
    conn = get_connection()
    return TagRepository(conn)


# === Папки ===

@router.get("/folders", response_model=None)
def get_folders(
    category_id: Optional[int] = Query(None),
    tree: bool = Query(False)
):
    """Получить все папки (плоский список или дерево)."""
    try:
        repo = get_folder_repo()
        
        if tree:
            folders = repo.get_tree(category_id)
        else:
            folders = repo.get_all(category_id)
        
        return [f.to_dict(include_children=tree) for f in folders]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/folders", response_model=dict)
def create_folder(
    name: str = Body(..., embed=True),
    parent_id: Optional[int] = Body(None, embed=True),
    note_category_id: int = Body(..., embed=True)
):
    """Создать папку."""
    repo = get_folder_repo()
    
    # Проверка родительской папки
    if parent_id:
        parent = repo.get_by_id(parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Родительская папка не найдена")
    
    folder = Folder(
        name=name,
        parent_id=parent_id,
        note_category_id=note_category_id
    )
    
    created = repo.create(folder)
    return created.to_dict()


@router.put("/folders/{folder_id}", response_model=dict)
def update_folder(
    folder_id: int,
    name: str = Body(..., embed=True),
    parent_id: Optional[int] = Body(None, embed=True),
    note_category_id: int = Body(..., embed=True)
):
    """Обновить папку."""
    repo = get_folder_repo()
    
    # Нельзя сделать папку дочерней самой себя
    if parent_id == folder_id:
        raise HTTPException(status_code=400, detail="Папка не может быть дочерней самой себя")
    
    folder = Folder(
        id=folder_id,
        name=name,
        parent_id=parent_id,
        note_category_id=note_category_id
    )
    
    updated = repo.update(folder)
    if not updated:
        raise HTTPException(status_code=404, detail="Папка не найдена")
    
    return updated.to_dict()


@router.delete("/folders/{folder_id}")
def delete_folder(folder_id: int):
    """Удалить папку."""
    repo = get_folder_repo()
    deleted = repo.delete(folder_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Папка не найдена")
    
    return {"message": "Папка удалена"}


# === Теги ===

@router.get("/tags", response_model=List[dict])
def get_tags():
    """Получить все теги."""
    repo = get_tag_repo()
    tags = repo.get_all()
    return [t.to_dict() for t in tags]


@router.post("/tags", response_model=dict)
def create_tag(
    name: str = Body(..., embed=True),
    color: str = Body("#008888", embed=True)
):
    """Создать тег."""
    repo = get_tag_repo()
    
    # Проверка на дубликат
    existing = repo.get_by_name(name)
    if existing:
        raise HTTPException(status_code=400, detail="Тег с таким именем уже существует")
    
    tag = Tag(name=name, color=color)
    created = repo.create(tag)
    return created.to_dict()


@router.put("/tags/{tag_id}", response_model=dict)
def update_tag(
    tag_id: int,
    name: str = Body(..., embed=True),
    color: str = Body("#008888", embed=True)
):
    """Обновить тег."""
    repo = get_tag_repo()
    
    tag = Tag(id=tag_id, name=name, color=color)
    updated = repo.update(tag)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Тег не найден")
    
    return updated.to_dict()


@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: int):
    """Удалить тег."""
    repo = get_tag_repo()
    deleted = repo.delete(tag_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Тег не найден")
    
    return {"message": "Тег удален"}


# === Теги заметок ===

@router.get("/notes/{note_id}/tags", response_model=List[dict])
def get_note_tags(note_id: int):
    """Получить теги заметки."""
    repo = get_tag_repo()
    tags = repo.get_tags_for_note(note_id)
    return [t.to_dict() for t in tags]


@router.post("/notes/{note_id}/tags", response_model=dict)
def add_tag_to_note(note_id: int, tag_id: int = Body(..., embed=True)):
    """Добавить тег к заметке."""
    repo = get_tag_repo()
    
    # Проверка существования
    if not repo.get_by_id(tag_id):
        raise HTTPException(status_code=404, detail="Тег не найден")
    
    success = repo.add_tag_to_note(note_id, tag_id)
    
    return {"note_id": note_id, "tag_id": tag_id, "added": success}


@router.delete("/notes/{note_id}/tags/{tag_id}")
def remove_tag_from_note(note_id: int, tag_id: int):
    """Удалить тег из заметки."""
    repo = get_tag_repo()
    success = repo.remove_tag_from_note(note_id, tag_id)
    
    return {"note_id": note_id, "tag_id": tag_id, "removed": success}


@router.put("/notes/{note_id}/tags", response_model=dict)
def set_note_tags(note_id: int, tag_ids: List[int] = Body(..., embed=True)):
    """Установить все теги для заметки."""
    repo = get_tag_repo()
    repo.set_tags_for_note(note_id, tag_ids)
    return {"note_id": note_id, "tag_ids": tag_ids}
