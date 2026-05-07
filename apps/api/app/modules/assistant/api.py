from fastapi import APIRouter

from app.modules.assistant.schemas import AssistantMessageRequest, AssistantMessageResponse
from app.modules.assistant.chat_service import AssistantChatService

router = APIRouter()


@router.post("/messages", response_model=AssistantMessageResponse)
def send_message(payload: AssistantMessageRequest) -> AssistantMessageResponse:
  service = AssistantChatService()
  answer = service.answer(payload.content, payload.course_id)
  return AssistantMessageResponse(answer=answer, citations=[])

