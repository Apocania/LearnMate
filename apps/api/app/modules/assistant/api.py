import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.assistant.schemas import (
  AssistantHistoryMessage,
  AssistantMessageRequest,
  AssistantMessageResponse,
  AssistantSessionCreateRequest,
  AssistantSessionResponse,
)
from app.modules.assistant.chat_service import AssistantChatService
from app.modules.auth.dependencies import get_current_user, require_roles
from app.modules.auth.models import User

router = APIRouter()


@router.post("/messages", response_model=AssistantMessageResponse)
def send_message(
  payload: AssistantMessageRequest,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> AssistantMessageResponse:
  require_roles(current_user, {"student", "mentor"})
  service = AssistantChatService(db)
  if payload.mode == "plan":
    return service.answer(payload.content, current_user, payload.course_id, payload.session_id, payload.mode)
  return service.answer(payload.content, current_user, payload.course_id, payload.session_id)


@router.post("/messages/stream")
def stream_message(
  payload: AssistantMessageRequest,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> StreamingResponse:
  require_roles(current_user, {"student", "mentor"})
  service = AssistantChatService(db)

  def event_stream():
    try:
      stream = (
        service.stream_answer(payload.content, current_user, payload.course_id, payload.session_id, payload.mode)
        if payload.mode == "plan"
        else service.stream_answer(payload.content, current_user, payload.course_id, payload.session_id)
      )
      for event in stream:
        yield f"{json.dumps(event, ensure_ascii=False)}\n"
    except Exception as exc:
      yield f"{json.dumps({'type': 'error', 'message': str(exc)}, ensure_ascii=False)}\n"

  return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@router.get("/messages/recent", response_model=list[AssistantHistoryMessage])
def list_recent_messages(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> list[AssistantHistoryMessage]:
  require_roles(current_user, {"student", "mentor"})
  return AssistantChatService(db).list_recent_messages(current_user)


@router.get("/sessions/current", response_model=AssistantSessionResponse)
def get_current_session(
  course_id: int | None = None,
  session_id: int | None = None,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> AssistantSessionResponse:
  require_roles(current_user, {"student", "mentor"})
  return AssistantChatService(db).get_current_session(current_user, course_id=course_id, session_id=session_id)


@router.post("/sessions", response_model=AssistantSessionResponse)
def create_session(
  payload: AssistantSessionCreateRequest,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> AssistantSessionResponse:
  require_roles(current_user, {"student", "mentor"})
  return AssistantChatService(db).create_new_session(current_user, course_id=payload.course_id, title=payload.title)
