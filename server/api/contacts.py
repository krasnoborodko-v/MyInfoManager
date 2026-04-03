"""
API эндпоинты для управления контактами.
"""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form # type: ignore

from db.database import get_connection
from db.models import Contact as ContactModel, ContactGroup as ContactGroupModel
from db.repositories.contact_repo import ContactRepository
from server.schemas import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactGroupCreate,
    ContactGroupUpdate,
    ContactGroupResponse,
)


router = APIRouter(prefix="/api/contacts", tags=["contacts"])


def get_repo():
    """Получить репозиторий контактов."""
    conn = get_connection()
    return ContactRepository(conn)


# === Группы контактов ===

@router.get("/groups", response_model=List[ContactGroupResponse])
def get_groups():
    """Получить все группы контактов."""
    repo = get_repo()
    return repo.get_groups()


@router.post("/groups", response_model=ContactGroupResponse)
def create_group(group: ContactGroupCreate):
    """Создать новую группу контактов."""
    repo = get_repo()
    return repo.create_group(group.name, group.color)


@router.put("/groups/{group_id}", response_model=ContactGroupResponse)
def update_group(group_id: int, group: ContactGroupUpdate):
    """Обновить группу контактов."""
    repo = get_repo()
    
    # Получаем текущую группу
    current = repo.get_group_by_id(group_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    
    # Обновляем только указанные поля
    new_name = group.name if group.name is not None else current.name
    new_color = group.color if group.color is not None else current.color
    
    updated = repo.update_group(group_id, new_name, new_color)
    return updated


@router.delete("/groups/{group_id}")
def delete_group(group_id: int):
    """Удалить группу контактов."""
    repo = get_repo()
    deleted = repo.delete_group(group_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    
    return {"message": "Группа удалена"}


# === Контакты ===

@router.get("", response_model=List[ContactResponse])
def get_contacts(
    group_id: Optional[int] = Query(None),
    favorite: bool = Query(False),
    search: Optional[str] = Query(None)
):
    """
    Получить список всех контактов с фильтрацией.
    
    Args:
        group_id: ID группы для фильтрации.
        favorite: Только избранные контакты.
        search: Поисковый запрос.
    """
    repo = get_repo()
    contacts = repo.get_all(
        group_id=group_id if group_id else None,
        favorite_only=favorite,
        search=search
    )
    # Не возвращаем фото в списке контактов
    for contact in contacts:
        contact.photo = None
        contact.photo_type = None
    return contacts


@router.get("/search", response_model=List[ContactResponse])
def search_contacts(q: str = Query(..., min_length=1)):
    """Поиск контактов по имени, телефону, email."""
    repo = get_repo()
    contacts = repo.search(q)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int):
    """Получить контакт по ID."""
    repo = get_repo()
    contact = repo.get_by_id(contact_id)
    
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    
    # Конвертируем фото в base64
    if contact.photo:
        import base64
        contact.photo = base64.b64encode(contact.photo).decode('utf-8')
        contact.photo_type = contact.photo_type or 'image/jpeg'
    else:
        contact.photo = None
        contact.photo_type = None
    
    return contact


@router.post("", response_model=ContactResponse)
def create_contact(contact: ContactCreate):
    """Создать новый контакт."""
    repo = get_repo()
    model = ContactModel(
        first_name=contact.first_name,
        last_name=contact.last_name,
        middle_name=contact.middle_name,
        group_id=contact.group_id,
        phones=contact.phones,
        emails=contact.emails,
        address=contact.address,
        company=contact.company,
        position=contact.position,
        birth_date=contact.birth_date,
        socials=contact.socials,
        website=contact.website,
        is_favorite=contact.is_favorite,
        notes=contact.notes,
    )
    created = repo.create(model)
    return created


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact: ContactUpdate):
    """Обновить существующий контакт."""
    import base64
    repo = get_repo()

    # Получаем текущий контакт
    current = repo.get_by_id(contact_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Контакт не найден")

    # Обновляем только указанные поля
    model = ContactModel(
        id=contact_id,
        first_name=contact.first_name if contact.first_name is not None else current.first_name,
        last_name=contact.last_name if contact.last_name is not None else current.last_name,
        middle_name=contact.middle_name if contact.middle_name is not None else current.middle_name,
        group_id=contact.group_id if contact.group_id is not None else current.group_id,
        phones=contact.phones if contact.phones is not None else current.phones,
        emails=contact.emails if contact.emails is not None else current.emails,
        address=contact.address if contact.address is not None else current.address,
        company=contact.company if contact.company is not None else current.company,
        position=contact.position if contact.position is not None else current.position,
        birth_date=contact.birth_date if contact.birth_date is not None else current.birth_date,
        photo=current.photo,  # Сохраняем существующее фото (уже base64 из get_by_id)
        photo_type=current.photo_type,  # Сохраняем тип фото
        socials=contact.socials if contact.socials is not None else current.socials,
        website=contact.website if contact.website is not None else current.website,
        is_favorite=contact.is_favorite if contact.is_favorite is not None else current.is_favorite,
        notes=contact.notes if contact.notes is not None else current.notes,
    )
    updated = repo.update(model)
    
    # Конвертируем фото в base64 для ответа
    if updated and updated.photo:
        updated.photo = base64.b64encode(updated.photo).decode('utf-8')
    
    return updated


@router.delete("/{contact_id}")
def delete_contact(contact_id: int):
    """Удалить контакт."""
    repo = get_repo()
    deleted = repo.delete(contact_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    
    return {"message": "Контакт удалён"}


@router.post("/{contact_id}/toggle-favorite", response_model=ContactResponse)
def toggle_favorite(contact_id: int):
    """Переключить статус избранного для контакта."""
    repo = get_repo()
    contact = repo.toggle_favorite(contact_id)
    
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    
    return contact


@router.post("/{contact_id}/photo")
async def upload_photo(
    contact_id: int,
    photo: UploadFile = File(..., description="Фотография контакта"),
):
    """
    Загрузить фото контакта.

    Args:
        contact_id: ID контакта.
        photo: Файл изображения.
    """
    import logging
    logger = logging.getLogger(__name__)
    import base64
    
    try:
        repo = get_repo()

        # Проверяем существование контакта
        contact = repo.get_by_id(contact_id)
        if contact is None:
            raise HTTPException(status_code=404, detail="Контакт не найден")

        # Проверяем тип файла
        if not photo.content_type or not photo.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail=f"Файл должен быть изображением, получен тип: {photo.content_type}")

        # Читаем файл
        photo_data = await photo.read()
        
        # Проверяем размер (макс 10MB)
        if len(photo_data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Размер файла не должен превышать 10MB")
        
        logger.info(f"Uploaded photo: {photo.filename}, size: {len(photo_data)} bytes, type: {photo.content_type}")

        # Обновляем контакт с фото
        model = ContactModel(
            id=contact_id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            middle_name=contact.middle_name,
            group_id=contact.group_id,
            phones=contact.phones,
            emails=contact.emails,
            address=contact.address,
            company=contact.company,
            position=contact.position,
            birth_date=contact.birth_date,
            photo=photo_data,
            photo_type=photo.content_type,
            socials=contact.socials,
            website=contact.website,
            is_favorite=contact.is_favorite,
            notes=contact.notes,
        )
        updated = repo.update(model)
        
        # Конвертируем фото в base64 для ответа
        if updated and updated.photo:
            updated.photo = base64.b64encode(updated.photo).decode('utf-8')
        
        return updated
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error uploading photo: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки фото: {str(e)}")


@router.delete("/{contact_id}/photo", response_model=ContactResponse)
def delete_photo(contact_id: int):
    """Удалить фото контакта."""
    repo = get_repo()
    
    contact = repo.get_by_id(contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    
    # Обновляем контакт без фото
    model = ContactModel(
        id=contact_id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        middle_name=contact.middle_name,
        group_id=contact.group_id,
        phones=contact.phones,
        emails=contact.emails,
        address=contact.address,
        company=contact.company,
        position=contact.position,
        birth_date=contact.birth_date,
        photo=None,
        photo_type=None,
        socials=contact.socials,
        website=contact.website,
        is_favorite=contact.is_favorite,
        notes=contact.notes,
    )
    updated = repo.update(model)
    return updated
