"""
API эндпоинты для вложений.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response

from db.connection import get_connection
from db.models import Attachment, User
from db.repositories.attachment_repo import AttachmentRepository
from server.schemas import AttachmentResponse
from server.auth import get_current_user

router = APIRouter(prefix="/api/attachments", tags=["attachments"])


def get_repo():
    conn = get_connection()
    return AttachmentRepository(conn)


@router.get("/note/{note_id}", response_model=List[AttachmentResponse])
def get_attachments(
    note_id: int,
    current_user: User = Depends(get_current_user),
):
    return get_repo().get_by_note_id(note_id, user_id=current_user.id)


@router.post("/note/{note_id}", response_model=AttachmentResponse, status_code=201)
async def upload_attachment(
    note_id: int,
    file: UploadFile = File(...),
    note: str = Form(None),
    current_user: User = Depends(get_current_user),
):
    file_data = await file.read()
    attachment = Attachment(
        note_id=note_id,
        file_type=file.content_type or "application/octet-stream",
        file_data=file_data,
        file_size=len(file_data),
        note=note,
    )
    return get_repo().create(attachment, user_id=current_user.id)


@router.put("/{attachment_id}/note")
async def update_attachment_note(
    attachment_id: int,
    note: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    updated = get_repo().update_note(attachment_id, note=note, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Вложение не найдено")
    return {"message": "Примечание обновлено"}


@router.get("/{attachment_id}")
def download_attachment(
    attachment_id: int,
    download: bool = False,
    current_user: User = Depends(get_current_user),
):
    attachment = get_repo().get_by_id(attachment_id, user_id=current_user.id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Вложение не найдено")
    file_data = get_repo().get_file_data(attachment_id, user_id=current_user.id)
    return Response(
        content=file_data,
        media_type=attachment.file_type,
        headers={"Content-Disposition": f"attachment; filename={attachment_id}"} if download else {},
    )


@router.delete("/{attachment_id}")
def delete_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
):
    deleted = get_repo().delete(attachment_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Вложение не найдено")
    return {"message": "Вложение удалено"}
