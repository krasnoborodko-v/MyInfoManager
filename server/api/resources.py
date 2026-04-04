"""
API эндпоинты для управления ресурсами.
Все эндпоинты требуют авторизации.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from db.connection import get_connection
from db.models import Resource as ResourceModel, User
from db.repositories.resource_repo import ResourceRepository
from server.schemas import (
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    KategoryResourceResponse,
)
from server.auth import get_current_user

router = APIRouter(prefix="/api/resources", tags=["resources"])


def get_repo():
    conn = get_connection()
    return ResourceRepository(conn)


# === Категории ===

@router.get("/categories", response_model=List[KategoryResourceResponse])
def get_categories(current_user: User = Depends(get_current_user)):
    repo = get_repo()
    return repo.get_categories(user_id=current_user.id)


@router.post("/categories", response_model=KategoryResourceResponse, status_code=201)
def create_category(
    name: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
):
    repo = get_repo()
    return repo.create_category(name, user_id=current_user.id)


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
):
    repo = get_repo()
    deleted = repo.delete_category(category_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return {"message": "Категория удалена"}


# === Ресурсы ===

@router.get("", response_model=List[ResourceResponse])
def get_resources(
    kategory_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
):
    repo = get_repo()
    return repo.get_all(user_id=current_user.id, kategory_id=kategory_id)


@router.post("", response_model=ResourceResponse, status_code=201)
def create_resource(
    data: ResourceCreate,
    current_user: User = Depends(get_current_user),
):
    repo = get_repo()
    resource = ResourceModel(**data.model_dump())
    return repo.create(resource, user_id=current_user.id)


@router.get("/search", response_model=List[ResourceResponse])
def search_resources(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
):
    repo = get_repo()
    return repo.search(user_id=current_user.id, query=q)


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
):
    repo = get_repo()
    resource = repo.get_by_id(resource_id, user_id=current_user.id)
    if not resource:
        raise HTTPException(status_code=404, detail="Ресурс не найден")
    return resource


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    data: ResourceUpdate,
    current_user: User = Depends(get_current_user),
):
    repo = get_repo()
    existing = repo.get_by_id(resource_id, user_id=current_user.id)
    if not existing:
        raise HTTPException(status_code=404, detail="Ресурс не найден")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(existing, field, value)
    updated = repo.update(existing, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Ресурс не найден")
    return updated


@router.delete("/{resource_id}")
def delete_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
):
    repo = get_repo()
    deleted = repo.delete(resource_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ресурс не найден")
    return {"message": "Ресурс удалён"}
