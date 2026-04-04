"""
API эндпоинты для контактов.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form

from db.connection import get_connection
from db.models import Contact as ContactModel, ContactGroup as ContactGroupModel, User
from db.repositories.contact_repo import ContactRepository
from server.schemas import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactGroupCreate,
    ContactGroupUpdate,
    ContactGroupResponse,
)
from server.auth import get_current_user

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


def get_repo():
    conn = get_connection()
    return ContactRepository(conn)


# === Группы ===

@router.get("/groups", response_model=List[ContactGroupResponse])
def get_groups(current_user: User = Depends(get_current_user)):
    return get_repo().get_groups(user_id=current_user.id)


@router.post("/groups", response_model=ContactGroupResponse, status_code=201)
def create_group(
    name: str = Query(...),
    color: str = Query('#008888'),
    current_user: User = Depends(get_current_user),
):
    return get_repo().create_group(name, user_id=current_user.id, color=color)


@router.put("/groups/{group_id}", response_model=ContactGroupResponse)
def update_group(
    group_id: int,
    data: ContactGroupUpdate,
    current_user: User = Depends(get_current_user),
):
    updated = get_repo().update_group(
        group_id, user_id=current_user.id,
        name=data.name, color=data.color,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return updated


@router.delete("/groups/{group_id}")
def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
):
    deleted = get_repo().delete_group(group_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return {"message": "Группа удалена"}


# === Контакты ===

@router.get("", response_model=List[ContactResponse])
def get_contacts(
    group_id: Optional[int] = Query(None),
    favorite: bool = Query(False),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    return get_repo().get_all(
        user_id=current_user.id,
        group_id=group_id,
        favorite=favorite,
        search=search,
    )


@router.get("/search", response_model=List[ContactResponse])
def search_contacts(
    q: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    return get_repo().get_all(user_id=current_user.id, search=q)


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
):
    contact = get_repo().get_by_id(contact_id, user_id=current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    return contact


@router.post("", response_model=ContactResponse, status_code=201)
def create_contact(
    data: ContactCreate,
    current_user: User = Depends(get_current_user),
):
    contact = ContactModel(**data.model_dump())
    return get_repo().create(contact, user_id=current_user.id)


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    data: ContactUpdate,
    current_user: User = Depends(get_current_user),
):
    existing = get_repo().get_by_id(contact_id, user_id=current_user.id)
    if not existing:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(existing, field, value)
    updated = get_repo().update(existing, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    return updated


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
):
    deleted = get_repo().delete(contact_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    return {"message": "Контакт удалён"}


@router.post("/{contact_id}/toggle-favorite", response_model=ContactResponse)
def toggle_favorite(
    contact_id: int,
    current_user: User = Depends(get_current_user),
):
    toggled = get_repo().toggle_favorite(contact_id, user_id=current_user.id)
    if not toggled:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    return toggled


# === Фото ===

@router.post("/{contact_id}/photo", response_model=ContactResponse)
async def upload_photo(
    contact_id: int,
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    photo_data = await photo.read()
    updated = get_repo().upload_photo(contact_id, user_id=current_user.id, photo_data=photo_data, photo_type=photo.content_type or "image/jpeg")
    if not updated:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    return updated


@router.delete("/{contact_id}/photo", response_model=ContactResponse)
def delete_photo(
    contact_id: int,
    current_user: User = Depends(get_current_user),
):
    updated = get_repo().delete_photo(contact_id, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    return updated
