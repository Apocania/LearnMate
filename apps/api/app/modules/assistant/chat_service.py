from app.infrastructure.llm_client import LLMClient
from app.modules.assistant.prompt_builder import build_course_prompt
from app.modules.assistant.retrieval_service import RetrievalService


class AssistantChatService:
  def __init__(self) -> None:
    self.retrieval_service = RetrievalService()
    self.llm_client = LLMClient()

  def answer(self, question: str, course_id: str | None = None) -> str:
    chunks = self.retrieval_service.retrieve(question, course_id)
    prompt = build_course_prompt(question, chunks)
    return self.llm_client.chat(prompt)

