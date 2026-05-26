from app.infrastructure.llm_client import LLMClient
from app.modules.assistant.prompt_builder import build_course_prompt
from app.modules.assistant.repository import AssistantRepository
from app.modules.assistant.retrieval_service import RetrievalService
import json

from app.modules.assistant.schemas import AssistantCitation, AssistantHistoryMessage, AssistantMessageResponse, AssistantSessionResponse
from app.modules.auth.models import User
from app.modules.learning_records.service import LearningRecordService
from sqlalchemy.orm import Session


class AssistantChatService:
  def __init__(self, db: Session) -> None:
    self.db = db
    self.repository = AssistantRepository(db)
    self.retrieval_service = RetrievalService(db)
    self.llm_client = LLMClient()

  def answer(
    self,
    question: str,
    current_user: User,
    course_id: int | None = None,
    session_id: int | None = None,
    mode: str = "qa",
  ) -> AssistantMessageResponse:
    prepared = self._prepare_answer(question, current_user, course_id, session_id, mode)
    answer = self.llm_client.chat(prepared["prompt"])
    self._persist_answer(
      question,
      answer,
      current_user,
      course_id,
      prepared["session"].id,
      prepared["citations"],
    )
    return AssistantMessageResponse(session_id=prepared["session"].id, answer=answer, citations=prepared["citations"])

  def stream_answer(
    self,
    question: str,
    current_user: User,
    course_id: int | None = None,
    session_id: int | None = None,
    mode: str = "qa",
  ):
    prepared = self._prepare_answer(question, current_user, course_id, session_id, mode)
    answer_parts: list[str] = []
    yield {
      "type": "meta",
      "session_id": prepared["session"].id,
      "citations": [citation.model_dump() for citation in prepared["citations"]],
    }
    for chunk in self.llm_client.stream_chat(prepared["prompt"]):
      answer_parts.append(chunk)
      yield {"type": "delta", "content": chunk}
    answer = "".join(answer_parts)
    self._persist_answer(
      question,
      answer,
      current_user,
      course_id,
      prepared["session"].id,
      prepared["citations"],
    )
    yield {"type": "done"}

  def get_current_session(
    self,
    current_user: User,
    course_id: int | None = None,
    session_id: int | None = None,
    limit: int = 12,
  ) -> AssistantSessionResponse:
    session = None
    if session_id is not None:
      existing_session = self.repository.get_session(session_id)
      if existing_session is not None and existing_session.user_id == current_user.id:
        session = existing_session
    if session is None:
      session = self.repository.get_latest_session(current_user.id, course_id)
    if session is None:
      session = self.repository.create_session(current_user.id, title="新的伴学对话", course_id=course_id)
    return self._build_session_response(current_user, session.id, limit)

  def create_new_session(
    self,
    current_user: User,
    course_id: int | None = None,
    title: str = "新的伴学对话",
  ) -> AssistantSessionResponse:
    session = self.repository.create_session(current_user.id, title=title.strip()[:80] or "新的伴学对话", course_id=course_id)
    return AssistantSessionResponse(id=session.id, course_id=session.course_id, title=session.title, messages=[])

  def list_recent_messages(self, current_user: User, limit: int = 8) -> list[AssistantHistoryMessage]:
    return [
      AssistantHistoryMessage(
        id=message.id,
        role=message.role,
        content=message.content,
        citations=self._load_citations(message.citations),
      )
      for message in self.repository.list_latest_messages(current_user.id, limit)
    ]

  def _build_session_response(self, current_user: User, session_id: int, limit: int) -> AssistantSessionResponse:
    session = self.repository.get_session(session_id)
    if session is None or session.user_id != current_user.id:
      session = self.repository.create_session(current_user.id, title="新的伴学对话")
      messages = []
    else:
      messages = [
        AssistantHistoryMessage(
          id=message.id,
          role=message.role,
          content=message.content,
          citations=self._load_citations(message.citations),
        )
        for message in self.repository.list_recent_messages(current_user.id, session.id, limit)
      ]
    return AssistantSessionResponse(
      id=session.id,
      course_id=session.course_id,
      title=session.title,
      messages=messages,
    )

  def _prepare_answer(
    self,
    question: str,
    current_user: User,
    course_id: int | None,
    session_id: int | None,
    mode: str,
  ):
    normalized_mode = "plan" if mode == "plan" else "qa"
    prompt_question = self._build_mode_question(question, normalized_mode)
    session = self._resolve_session(question, current_user, course_id, session_id)
    chunks = self.retrieval_service.retrieve(prompt_question, course_id)
    prompt = build_course_prompt(prompt_question, chunks)
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
    return {"session": session, "prompt": prompt, "citations": citations}

  def _build_mode_question(self, question: str, mode: str) -> str:
    if mode != "plan":
      return question
    return (
      "请以儿童学习规划师身份回答，语气温柔、具体、容易执行。"
      "先给出一条清楚的学习路径，再列出今天可以完成的 2-3 个小任务，"
      "每个任务都要短小、可完成。"
      f"学生输入：{question}"
    )

  def _persist_answer(
    self,
    question: str,
    answer: str,
    current_user: User,
    course_id: int | None,
    session_id: int,
    citations: list[AssistantCitation],
  ) -> None:
    self.repository.create_message(
      user_id=current_user.id,
      role="user",
      content=question,
      session_id=session_id,
      course_id=course_id,
    )
    self.repository.create_message(
      user_id=current_user.id,
      role="assistant",
      content=answer,
      session_id=session_id,
      course_id=course_id,
      citations=citations,
    )
    LearningRecordService(self.db).record_event(
      current_user,
      "assistant_question",
      course_id=course_id,
      metadata={"question": question[:120], "citation_count": str(len(citations))},
    )

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

  def _load_citations(self, raw_citations: str | None) -> list[AssistantCitation]:
    if not raw_citations:
      return []
    try:
      values = json.loads(raw_citations)
    except json.JSONDecodeError:
      return []
    if not isinstance(values, list):
      return []
    citations: list[AssistantCitation] = []
    for value in values:
      if not isinstance(value, dict):
        continue
      try:
        citations.append(AssistantCitation.model_validate(value))
      except ValueError:
        continue
    return citations
