"""
Модели данных для приложения MyInfoManager.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# === Пользователи ===

@dataclass
class User:
    """Пользователь системы."""
    id: Optional[int] = None
    email: str = ""
    hashed_password: str = ""
    full_name: str = ""
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row) -> "User":
        return cls(
            id=row["id"],
            email=row["email"],
            hashed_password=row.get("hashed_password", ""),
            full_name=row.get("full_name", ""),
            is_active=bool(row.get("is_active", True)),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )


# === Категории ресурсов ===

@dataclass
class KategoryResource:
    """Категория ресурса."""
    id: Optional[int] = None
    name: str = ""
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name
        }
    
    @classmethod
    def from_row(cls, row) -> "KategoryResource":
        return cls(
            id=row["id"],
            name=row["name"]
        )


# === Ресурсы ===

@dataclass
class Resource:
    """Информационный ресурс (например, ссылка на сайт)."""
    id: Optional[int] = None
    name: str = ""
    kategory_id: Optional[int] = None
    url: Optional[str] = None
    description: Optional[str] = None
    kategory_name: Optional[str] = None  # Для JOIN-запросов
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "kategory_id": self.kategory_id,
            "url": self.url,
            "description": self.description,
            "kategory_name": self.kategory_name
        }
    
    @classmethod
    def from_row(cls, row) -> "Resource":
        return cls(
            id=row["id"],
            name=row["name"],
            kategory_id=row["kategory_id"],
            url=row["url"],
            description=row["description"],
            kategory_name=row["kategory_name"] if row["kategory_name"] else None
        )


# === Категории заметок ===

@dataclass
class KategoryNote:
    """Категория заметки."""
    id: Optional[int] = None
    name: str = ""
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name
        }
    
    @classmethod
    def from_row(cls, row) -> "KategoryNote":
        return cls(
            id=row["id"],
            name=row["name"]
        )


# === Заметки ===

@dataclass
class Note:
    """Заметка."""
    id: Optional[int] = None
    name: str = ""
    kategory_id: Optional[int] = None
    note_text: Optional[str] = None
    data_time: Optional[datetime] = None
    kategory_name: Optional[str] = None  # Для JOIN-запросов
    folder_id: Optional[int] = None  # Папка, к которой принадлежит заметка
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "kategory_id": self.kategory_id,
            "note_text": self.note_text,
            "data_time": self.data_time.isoformat() if self.data_time else None,
            "kategory_name": self.kategory_name,
            "folder_id": self.folder_id,
        }
    
    @classmethod
    def from_row(cls, row) -> "Note":
        data_time = row["data_time"]
        if isinstance(data_time, str):
            data_time = datetime.fromisoformat(data_time)
        
        kategory_name = row["kategory_name"]
        
        return cls(
            id=row["id"],
            name=row["name"],
            kategory_id=row["kategory_id"],
            note_text=row["note_text"],
            data_time=data_time,
            kategory_name=kategory_name if kategory_name else None,
            folder_id=row["folder_id"]
        )


# === Категории задач ===

@dataclass
class KategoryTask:
    """Категория задачи."""
    id: Optional[int] = None
    name: str = ""
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name
        }
    
    @classmethod
    def from_row(cls, row) -> "KategoryTask":
        return cls(
            id=row["id"],
            name=row["name"]
        )


# === Задачи ===

@dataclass
class Task:
    """Задача."""
    id: Optional[int] = None
    name: str = ""
    kategory_id: Optional[int] = None
    description: Optional[str] = None
    data_time: Optional[datetime] = None
    kategory_name: Optional[str] = None  # Для JOIN-запросов
    priority: str = "medium"  # high, medium, low
    status: str = "not_done"  # not_done, in_progress, done
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "kategory_id": self.kategory_id,
            "description": self.description,
            "data_time": self.data_time.isoformat() if self.data_time else None,
            "kategory_name": self.kategory_name,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_row(cls, row) -> "Task":
        data_time = row["data_time"]
        if isinstance(data_time, str):
            data_time = datetime.fromisoformat(data_time)

        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            id=row["id"],
            name=row["name"],
            kategory_id=row["kategory_id"],
            description=row["description"],
            data_time=data_time,
            kategory_name=row["kategory_name"] if row["kategory_name"] else None,
            priority=row["priority"] if row["priority"] else "medium",
            status=row["status"] if row["status"] else "not_done",
            created_at=created_at
        )


# === Подзадачи ===

@dataclass
class Subtask:
    """Подзадача."""
    id: Optional[int] = None
    task_id: int = 0
    title: str = ""
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: bool = False
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_completed": self.is_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_row(cls, row) -> "Subtask":
        due_date = row["due_date"]
        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date)

        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            id=row["id"],
            task_id=row["task_id"],
            title=row["title"],
            description=row["description"] if row["description"] else None,
            due_date=due_date,
            is_completed=bool(row["is_completed"] if row["is_completed"] else 0),
            created_at=created_at
        )


# === Вложения ===

@dataclass
class Attachment:
    """Вложение (изображение или аудио) для заметки."""
    id: Optional[int] = None
    note_id: int = 0
    file_type: str = ""  # MIME тип, например 'image/png', 'audio/mp3'
    file_data: Optional[bytes] = None  # Для загрузки
    file_size: Optional[int] = None
    note: Optional[str] = None  # Примечание к вложению
    created_at: Optional[datetime] = None

    def to_dict(self, include_data: bool = False) -> dict:
        """
        Преобразовать в словарь.

        Args:
            include_data: Включать ли бинарные данные файла.
        """
        result = {
            "id": self.id,
            "note_id": self.note_id,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_data and self.file_data:
            # Кодируем в base64 для передачи через JSON
            import base64
            result["file_data"] = base64.b64encode(self.file_data).decode('utf-8')
        return result

    @classmethod
    def from_row(cls, row) -> "Attachment":
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            id=row["id"],
            note_id=row["note_id"],
            file_type=row["file_type"],
            file_data=row["file_data"],
            file_size=row["file_size"],
            note=row["note"],
            created_at=created_at
        )


# === Папки ===

@dataclass
class Folder:
    """Папка для заметок (иерархическая)."""
    id: Optional[int] = None
    name: str = ""
    parent_id: Optional[int] = None
    note_category_id: Optional[int] = None
    created_at: Optional[datetime] = None
    parent_name: Optional[str] = None  # Для JOIN
    children: list = None  # Дочерние папки
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    def to_dict(self, include_children: bool = False) -> dict:
        result = {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "note_category_id": self.note_category_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "parent_name": self.parent_name,
        }
        if include_children and self.children:
            result["children"] = [c.to_dict(include_children=True) for c in self.children]
        return result
    
    @classmethod
    def from_row(cls, row) -> "Folder":
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            id=row["id"],
            name=row["name"],
            parent_id=row["parent_id"],
            note_category_id=row["note_category_id"],
            created_at=created_at,
            parent_name=row["parent_name"] if row["parent_name"] else None
        )


# === Теги ===

@dataclass
class Tag:
    """Тег для заметок."""
    id: Optional[int] = None
    name: str = ""
    color: str = "#008888"
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_row(cls, row) -> "Tag":
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            id=row["id"],
            name=row["name"],
            color=row["color"],
            created_at=created_at
        )


# === Контакты ===

@dataclass
class ContactGroup:
    """Группа контактов (семья, коллеги и т.д.)."""
    id: Optional[int] = None
    name: str = ""
    color: str = "#008888"
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_row(cls, row) -> "ContactGroup":
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            id=row["id"],
            name=row["name"],
            color=row["color"] if row["color"] else "#008888",
            created_at=created_at
        )


@dataclass
class Contact:
    """Контакт (персона)."""
    id: Optional[int] = None
    first_name: str = ""  # Имя
    last_name: str = ""   # Фамилия
    middle_name: str = ""  # Отчество
    group_id: Optional[int] = None
    phones: Optional[str] = None  # JSON массив телефонов: [{"type": "mobile", "value": "..."}]
    emails: Optional[str] = None  # JSON массив email
    address: Optional[str] = None
    company: Optional[str] = None  # Место работы
    position: Optional[str] = None  # Должность
    birth_date: Optional[datetime] = None
    photo: Optional[bytes] = None  # Фото (BLOB)
    photo_type: Optional[str] = None  # MIME тип фото
    socials: Optional[str] = None  # JSON соцсетей: [{"type": "telegram", "value": "..."}]
    website: Optional[str] = None
    is_favorite: bool = False
    notes: Optional[str] = None  # Комментарий
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    group_name: Optional[str] = None  # Для JOIN-запросов

    def to_dict(self, include_photo: bool = False) -> dict:
        import base64
        result = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "group_id": self.group_id,
            "phones": self.phones,
            "emails": self.emails,
            "address": self.address,
            "company": self.company,
            "position": self.position,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "socials": self.socials,
            "website": self.website,
            "is_favorite": self.is_favorite,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "group_name": self.group_name,
        }
        if include_photo and self.photo:
            result["photo"] = base64.b64encode(self.photo).decode('utf-8')
            result["photo_type"] = self.photo_type
        return result

    @classmethod
    def from_row(cls, row) -> "Contact":
        birth_date = row["birth_date"]
        if isinstance(birth_date, str):
            birth_date = datetime.fromisoformat(birth_date)

        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = row["updated_at"]
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return cls(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            middle_name=row["middle_name"] if row["middle_name"] else "",
            group_id=row["group_id"],
            phones=row["phones"],
            emails=row["emails"],
            address=row["address"],
            company=row["company"],
            position=row["position"],
            birth_date=birth_date,
            photo=row["photo"],
            photo_type=row["photo_type"],
            socials=row["socials"],
            website=row["website"],
            is_favorite=bool(row["is_favorite"] if row["is_favorite"] else 0),
            notes=row["notes"],
            created_at=created_at,
            updated_at=updated_at,
            group_name=row["group_name"] if row["group_name"] else None
        )
