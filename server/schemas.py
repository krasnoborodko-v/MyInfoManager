"""
Pydantic схемы для валидации данных API.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# === Авторизация ===

class UserCreate(BaseModel):
    """Регистрация нового пользователя."""
    email: str = Field(..., min_length=3, max_length=200)
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str = Field("", max_length=200)


class UserLogin(BaseModel):
    """Вход в систему."""
    email: str
    password: str


class UserResponse(BaseModel):
    """Информация о пользователе (без пароля)."""
    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Ответ при успешном входе."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenRefresh(BaseModel):
    """Запрос на обновление токена."""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Ответ с новым access-токеном."""
    access_token: str
    token_type: str = "bearer"


# === Категории ресурсов ===

class KategoryResourceBase(BaseModel):
    """Базовая схема категории ресурса."""
    name: str = Field(..., min_length=1, max_length=100)


class KategoryResourceCreate(KategoryResourceBase):
    """Схема для создания категории ресурса."""
    pass


class KategoryResourceResponse(KategoryResourceBase):
    """Схема ответа категории ресурса."""
    id: int
    
    model_config = {"from_attributes": True}


# === Ресурсы ===

class ResourceBase(BaseModel):
    """Базовая схема ресурса."""
    name: str = Field(..., min_length=1, max_length=200)
    kategory_id: Optional[int] = None
    url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None


class ResourceCreate(ResourceBase):
    """Схема для создания ресурса."""
    pass


class ResourceUpdate(ResourceBase):
    """Схема для обновления ресурса."""
    pass


class ResourceResponse(ResourceBase):
    """Схема ответа ресурса."""
    id: int
    kategory_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


# === Категории заметок ===

class KategoryNoteBase(BaseModel):
    """Базовая схема категории заметки."""
    name: str = Field(..., min_length=1, max_length=100)


class KategoryNoteCreate(KategoryNoteBase):
    """Схема для создания категории заметки."""
    pass


class KategoryNoteResponse(KategoryNoteBase):
    """Схема ответа категории заметки."""
    id: int
    
    model_config = {"from_attributes": True}


# === Заметки ===

class NoteBase(BaseModel):
    """Базовая схема заметки."""
    name: str = Field(..., min_length=1, max_length=200)
    kategory_id: Optional[int] = None
    folder_id: Optional[int] = None  # Папка
    note_text: Optional[str] = None
    data_time: Optional[datetime] = None


class NoteCreate(NoteBase):
    """Схема для создания заметки."""
    pass


class NoteUpdate(NoteBase):
    """Схема для обновления заметки."""
    pass


class NoteResponse(NoteBase):
    """Схема ответа заметки."""
    id: int
    kategory_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


# === Категории задач ===

class KategoryTaskBase(BaseModel):
    """Базовая схема категории задачи."""
    name: str = Field(..., min_length=1, max_length=100)


class KategoryTaskCreate(KategoryTaskBase):
    """Схема для создания категории задачи."""
    pass


class KategoryTaskResponse(KategoryTaskBase):
    """Схема ответа категории задачи."""
    id: int
    
    model_config = {"from_attributes": True}


# === Задачи ===

class TaskBase(BaseModel):
    """Базовая схема задачи."""
    name: str = Field(..., min_length=1, max_length=200)
    kategory_id: Optional[int] = None
    description: Optional[str] = None
    data_time: Optional[datetime] = None
    priority: str = Field(default="medium", pattern="^(high|medium|low)$")
    status: str = Field(default="not_done", pattern="^(not_done|in_progress|done)$")


class TaskCreate(TaskBase):
    """Схема для создания задачи."""
    pass


class TaskUpdate(TaskBase):
    """Схема для обновления задачи."""
    pass


class TaskResponse(TaskBase):
    """Схема ответа задачи."""
    id: int
    kategory_name: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# === Подзадачи ===

class SubtaskBase(BaseModel):
    """Базовая схема подзадачи."""
    task_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: bool = False


class SubtaskCreate(BaseModel):
    """Схема для создания подзадачи."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: bool = False


class SubtaskUpdate(BaseModel):
    """Схема для обновления подзадачи."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None


class SubtaskResponse(SubtaskBase):
    """Схема ответа подзадачи."""
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# === Контакты ===

class ContactGroupBase(BaseModel):
    """Базовая схема группы контактов."""
    name: str = Field(..., min_length=1, max_length=100)
    color: str = "#008888"


class ContactGroupCreate(BaseModel):
    """Схема для создания группы контактов."""
    name: str = Field(..., min_length=1, max_length=100)
    color: str = "#008888"


class ContactGroupUpdate(BaseModel):
    """Схема для обновления группы контактов."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = None


class ContactGroupResponse(ContactGroupBase):
    """Схема ответа группы контактов."""
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ContactBase(BaseModel):
    """Базовая схема контакта."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = None
    group_id: Optional[int] = None
    phones: Optional[str] = None  # JSON
    emails: Optional[str] = None  # JSON
    address: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    birth_date: Optional[datetime] = None
    socials: Optional[str] = None  # JSON
    website: Optional[str] = None
    is_favorite: bool = False
    notes: Optional[str] = None


class ContactCreate(BaseModel):
    """Схема для создания контакта."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = None
    group_id: Optional[int] = None
    phones: Optional[str] = None
    emails: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    birth_date: Optional[datetime] = None
    socials: Optional[str] = None
    website: Optional[str] = None
    is_favorite: bool = False
    notes: Optional[str] = None


class ContactUpdate(BaseModel):
    """Схема для обновления контакта."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = None
    group_id: Optional[int] = None
    phones: Optional[str] = None
    emails: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    birth_date: Optional[datetime] = None
    socials: Optional[str] = None
    website: Optional[str] = None
    is_favorite: Optional[bool] = None
    notes: Optional[str] = None


class ContactResponse(ContactBase):
    """Схема ответа контакта."""
    id: int
    photo: Optional[str] = None  # Base64 encoded
    photo_type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    group_name: Optional[str] = None

    model_config = {"from_attributes": True}

