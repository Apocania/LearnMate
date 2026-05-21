from app.infrastructure.llm_client import LLMClient
from app.modules.assistant.prompt_builder import build_course_prompt
from app.modules.assistant.repository import AssistantRepository
from app.modules.assistant.retrieval_service import RetrievalService
from app.modules.assistant.schemas import AssistantCitation, AssistantMessageResponse
from app.modules.auth.models import User
from app.modules.learning_records.service import LearningRecordService
from sqlalchemy.orm import Session


class AssistantChatService:
  def __init__(self, db: Session) -> None:
    self.db = db
    self.repository = AssistantRepository(db)
    self.retrieval_service = RetrievalService(db)
    self.llm_client = LLMClient()

  def answer(self, question: str, current_user: User, course_id: int | None = None, session_id: int | None = None) -> AssistantMessageResponse:
    session = self._resolve_session(question, current_user, course_id, session_id)
    chunks = self.retrieval_service.retrieve(question, course_id)
    prompt = build_course_prompt(question, chunks)
    answer = self.llm_client.chat(prompt)
    citations = [
      AssistantCitation(
        document_id=chunk.get("document_id", ""),
        title=chunk.get("title", "课程资料"),
        chunk_index=int(chunk.get("chunk_index", "0") or 0),
        snippet=self._snippet(chunk.get("content", "")),
        source_url=chunk.get("source_url") or None,
      )
      for chunk in chunks
    ]
    self.repository.create_message(
      user_id=current_user.id,
      role="user",
      content=question,
      session_id=session.id,
      course_id=course_id,
    )
    self.repository.create_message(
      user_id=current_user.id,
      role="assistant",
      content=answer,
      session_id=session.id,
      course_id=course_id,
      citations=citations,
    )
    LearningRecordService(self.db).record_event(
      current_user,
      "assistant_question",
      course_id=course_id,
      metadata={"question": question[:120], "citation_count": str(len(citations))},
    )
    return AssistantMessageResponse(session_id=session.id, answer=answer, citations=citations)

  def _resolve_session(self, question: str, current_user: User, course_id: int | None, session_id: int | None):
    if session_id is not None:
      session = self.repository.get_session(session_id)
      if session is not None and session.user_id == current_user.id:
        return session
    title = question.strip()[:32] or "新的伴学对话"
    return self.repository.create_session(current_user.id, title=title, course_id=course_id)

  def _snippet(self, content: str) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= 120:
      return normalized
    return f"{normalized[:120]}..."
