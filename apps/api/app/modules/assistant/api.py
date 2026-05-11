from fastapi import APIRouter, Depends

from app.modules.assistant.schemas import AssistantMessageRequest, AssistantMessageResponse
from app.modules.assistant.chat_service import AssistantChatService
from app.modules.auth.dependencies import get_current_user, require_roles
from app.modules.auth.models import User

router = APIRouter()


@router.post("/messages", response_model=AssistantMessageResponse)
def send_message(
  payload: AssistantMessageRequest,
  current_user: User = Depends(get_current_user),
) -> AssistantMessageResponse:
  require_roles(current_user, {"student", "mentor"})
  service = AssistantChatService()
  answer = service.answer(payload.content, payload.course_id)
  return AssistantMessageResponse(answer=answer, citations=[])
