"""
API эндпоинты для управления вложениями (изображения, аудио).
"""
import base64
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response

from db.connection import get_connection
from db.models import Attachment
from db.repositories.attachment_repo import AttachmentRepository


router = APIRouter(prefix="/api/attachments", tags=["attachments"])


def get_repo():
    """Получить репозиторий вложений."""
    conn = get_connection()
    return AttachmentRepository(conn)


@router.get("/note/{note_id}")
def get_attachments(note_id: int):
    """
    Получить все вложения для заметки.

    Возвращает метаданные без бинарных данных.
    """
    repo = get_repo()
    attachments = repo.get_by_note_id(note_id)
    return [att.to_dict(include_data=False) for att in attachments]


@router.get("/{attachment_id}/data")
def get_attachment_data(attachment_id: int):
    """
    Получить вложение как base64 для отображения в браузере.
    """
    repo = get_repo()
    attachment = repo.get_by_id(attachment_id)

    if attachment is None:
        raise HTTPException(status_code=404, detail="Вложение не найдено")

    file_data_base64 = base64.b64encode(attachment.file_data).decode('utf-8')

    return {
        "id": attachment.id,
        "file_name": attachment.file_name,
        "file_type": attachment.file_type,
        "file_size": attachment.file_size,
        "data": file_data_base64
    }


@router.get("/{attachment_id}")
def get_attachment(attachment_id: int, download: bool = False):
    """
    Получить вложение по ID.

    Возвращает бинарные данные файла (если download=true) или метаданные.
    """
    try:
        repo = get_repo()
        attachment = repo.get_by_id(attachment_id)

        if attachment is None:
            raise HTTPException(status_code=404, detail="Вложение не найдено")

        if download:
            # Проверяем, что данные есть
            if not attachment.file_data:
                raise HTTPException(status_code=404, detail="Файл не найден")

            # Генерируем имя файла на основе типа
            extension_map = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'image/webp': '.webp',
                'image/svg+xml': '.svg',
                'audio/mpeg': '.mp3',
                'audio/mp3': '.mp3',
                'audio/wav': '.wav',
                'audio/ogg': '.ogg',
                'audio/webm': '.webm',
            }
            extension = extension_map.get(attachment.file_type, '.bin')
            filename = f"attachment_{attachment.id}{extension}"
            
            # Кодируем имя файла для заголовка (UTF-8 encoding для русских символов)
            import urllib.parse
            encoded_filename = urllib.parse.quote(filename)

            return Response(
                content=attachment.file_data,
                media_type=attachment.file_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'
                }
            )

        # Возвращаем метаданные
        return attachment.to_dict(include_data=False)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при чтении файла: {str(e)}")


@router.post("/note/{note_id}")
async def upload_attachment(
    note_id: int,
    file: UploadFile = File(..., description="Файл для загрузки (изображение или аудио)"),
    note: str = Form(None, description="Примечание к вложению")
):
    """
    Загрузить вложение для заметки.

    Поддерживаемые типы:
    - Изображения: image/jpeg, image/png, image/gif, image/webp
    - Аудио: audio/mpeg, audio/mp3, audio/wav, audio/ogg, audio/webm
    """
    # Проверка типа файла
    allowed_types = [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
        'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/webm',
        'audio/webm;codecs=opus'  # Формат записи из браузера
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый тип файла: {file.content_type}. "
                   f"Разрешены: изображения (JPEG, PNG, GIF, WebP, SVG) и аудио (MP3, WAV, OGG, WebM)"
        )

    # Проверка размера (макс 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл слишком большой (макс. 10MB)")

    repo = get_repo()

    attachment = Attachment(
        note_id=note_id,
        file_type=file.content_type,
        file_data=content,
        file_size=len(content),
        note=note
    )

    created = repo.create(attachment)

    return created.to_dict(include_data=False)


@router.put("/{attachment_id}/note")
def update_attachment_note(attachment_id: int, note: str = Form(None, description="Примечание к вложению")):
    """
    Обновить вложение (примечание).
    """
    repo = get_repo()
    
    attachment = repo.get_by_id(attachment_id)
    if attachment is None:
        raise HTTPException(status_code=404, detail="Вложение не найдено")
    
    attachment.note = note
    updated = repo.update(attachment)
    
    return updated.to_dict(include_data=False)


@router.delete("/{attachment_id}")
def delete_attachment(attachment_id: int):
    """Удалить вложение."""
    repo = get_repo()
    deleted = repo.delete(attachment_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Вложение не найдено")
    
    return {"message": "Вложение удалено"}
