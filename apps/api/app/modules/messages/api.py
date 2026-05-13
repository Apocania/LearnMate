from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.messages.schemas import (
  AnnouncementCreate,
  AnnouncementResult,
  PrivateMessageCreate,
  StudentRecipientResponse,
  UnreadCountResponse,
  UserMessageResponse,
)
from app.modules.messages.service import MessageService

router = APIRouter()


@router.get("", response_model=list[UserMessageResponse])
def list_messages(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> list[UserMessageResponse]:
  return MessageService(db).list_my_messages(current_user)


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> UnreadCountResponse:
  return UnreadCountResponse(unread_count=MessageService(db).get_unread_count(current_user))


@router.get("/student-recipients", response_model=list[StudentRecipientResponse])
def list_student_recipients(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> list[StudentRecipientResponse]:
  return MessageService(db).list_student_recipients(current_user)


@router.post("/{message_id}/read", response_model=UserMessageResponse)
def mark_message_as_read(
  message_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> UserMessageResponse:
  return MessageService(db).mark_as_read(message_id, current_user)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_messages_as_read(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> Response:
  MessageService(db).mark_all_as_read(current_user)
  return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/private", response_model=UserMessageResponse, status_code=status.HTTP_201_CREATED)
def send_private_message(
  payload: PrivateMessageCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> UserMessageResponse:
  return MessageService(db).send_private_message(payload, current_user)


@router.post("/announcements", response_model=AnnouncementResult, status_code=status.HTTP_201_CREATED)
def send_announcement(
  payload: AnnouncementCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> AnnouncementResult:
  return MessageService(db).send_announcement(payload, current_user)
