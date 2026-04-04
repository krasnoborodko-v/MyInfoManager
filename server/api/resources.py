"""
API эндпоинты для управления ресурсами.
"""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from db.connection import get_connection
from db.models import Resource as ResourceModel
from db.repositories.resource_repo import ResourceRepository
from server.schemas import (
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    KategoryResourceResponse,
)


router = APIRouter(prefix="/api/resources", tags=["resources"])


def get_repo():
    """Получить репозиторий ресурсов."""
    conn = get_connection()
    return ResourceRepository(conn)


# === Категории ресурсов (должны быть перед /{resource_id}) ===

@router.get("/categories", response_model=List[KategoryResourceResponse])
def get_categories():
    """Получить список всех категорий ресурсов."""
    repo = get_repo()
    return repo.get_categories()


@router.post("/categories", response_model=KategoryResourceResponse)
def create_category(name: str = Query(..., min_length=1)):
    """Создать новую категорию ресурсов."""
    repo = get_repo()
    return repo.create_category(name)


@router.delete("/categories/{category_id}")
def delete_category(category_id: int):
    """Удалить категорию ресурсов."""
    repo = get_repo()
    deleted = repo.delete_category(category_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    return {"message": "Категория удалена"}


# === Ресурсы ===

@router.get("", response_model=List[ResourceResponse])
def get_resources(kategory_id: Optional[int] = Query(None)):
    """Получить список всех ресурсов, опционально фильтруя по категории."""
    repo = get_repo()
    resources = repo.get_all(kategory_id=kategory_id)
    return resources


@router.get("/search", response_model=List[ResourceResponse])
def search_resources(q: str = Query(..., min_length=1)):
    """Поиск ресурсов по имени."""
    repo = get_repo()
    resources = repo.search(q)
    return resources


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: int):
    """Получить ресурс по ID."""
    repo = get_repo()
    resource = repo.get_by_id(resource_id)

    if resource is None:
        raise HTTPException(status_code=404, detail="Ресурс не найден")

    return resource


@router.post("", response_model=ResourceResponse)
def create_resource(resource: ResourceCreate):
    """Создать новый ресурс."""
    repo = get_repo()
    model = ResourceModel(
        name=resource.name,
        kategory_id=resource.kategory_id,
        url=resource.url,
        description=resource.description,
    )
    created = repo.create(model)
    return created


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: int, resource: ResourceUpdate):
    """Обновить существующий ресурс."""
    repo = get_repo()
    model = ResourceModel(
        id=resource_id,
        name=resource.name,
        kategory_id=resource.kategory_id,
        url=resource.url,
        description=resource.description,
    )
    updated = repo.update(model)

    if updated is None:
        raise HTTPException(status_code=404, detail="Ресурс не найден")

    return updated


@router.delete("/{resource_id}")
def delete_resource(resource_id: int):
    """Удалить ресурс."""
    repo = get_repo()
    deleted = repo.delete(resource_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Ресурс не найден")

    return {"message": "Ресурс удалён"}
