"""
Pydantic схемы для валидации данных API.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


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
    due_date: Optional[datetime] = None
    is_completed: bool = False


class SubtaskCreate(BaseModel):
    """Схема для создания подзадачи."""
    title: str = Field(..., min_length=1, max_length=200)
    due_date: Optional[datetime] = None
    is_completed: bool = False


class SubtaskUpdate(BaseModel):
    """Схема для обновления подзадачи."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None


class SubtaskResponse(SubtaskBase):
    """Схема ответа подзадачи."""
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
