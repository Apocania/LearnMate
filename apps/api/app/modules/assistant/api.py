from fastapi import APIRouter, Depends
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
