import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.assistant.schemas import AssistantMessageRequest, AssistantMessageResponse
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
      for event in service.stream_answer(payload.content, current_user, payload.course_id, payload.session_id):
        yield f"{json.dumps(event, ensure_ascii=False)}\n"
    except Exception as exc:
      yield f"{json.dumps({'type': 'error', 'message': str(exc)}, ensure_ascii=False)}\n"

  return StreamingResponse(event_stream(), media_type="application/x-ndjson")
