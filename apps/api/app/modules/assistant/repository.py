import json
import hashlib
import re

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import func as sql_func

from app.modules.assistant.models import AssistantMessage, AssistantSession, KnowledgeChunk
from app.modules.assistant.schemas import AssistantCitation

EMBEDDING_DIMENSION = 64


class AssistantRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def get_session(self, session_id: int) -> AssistantSession | None:
    return self.db.get(AssistantSession, session_id)

  def create_session(self, user_id: int, title: str, course_id: int | None = None) -> AssistantSession:
    session = AssistantSession(user_id=user_id, title=title, course_id=course_id)
    self.db.add(session)
    self.db.commit()
    self.db.refresh(session)
    return session

  def get_latest_session(self, user_id: int, course_id: int | None = None) -> AssistantSession | None:
    statement = select(AssistantSession).where(AssistantSession.user_id == user_id)
    if course_id is None:
      statement = statement.where(AssistantSession.course_id.is_(None))
    else:
      statement = statement.where(AssistantSession.course_id == course_id)
    return self.db.scalar(statement.order_by(AssistantSession.updated_at.desc(), AssistantSession.id.desc()).limit(1))

  def create_message(
    self,
    user_id: int,
    role: str,
    content: str,
    session_id: int | None = None,
    course_id: int | None = None,
    citations: list[AssistantCitation] | None = None,
  ) -> AssistantMessage:
    message = AssistantMessage(
      session_id=session_id,
      user_id=user_id,
      course_id=course_id,
      role=role,
      content=content,
      citations=json.dumps([citation.model_dump() for citation in citations or []], ensure_ascii=False),
    )
    self.db.add(message)
    if session_id is not None:
      session = self.db.get(AssistantSession, session_id)
      if session is not None:
        session.updated_at = sql_func.now()
        self.db.add(session)
    self.db.commit()
    self.db.refresh(message)
    return message

  def list_recent_messages(self, user_id: int, session_id: int, limit: int = 8) -> list[AssistantMessage]:
    messages = list(
      self.db.scalars(
        select(AssistantMessage)
        .where(AssistantMessage.user_id == user_id, AssistantMessage.session_id == session_id)
        .order_by(AssistantMessage.id.desc())
        .limit(limit)
      ).all()
    )
    return list(reversed(messages))

  def list_latest_messages(self, user_id: int, limit: int = 8) -> list[AssistantMessage]:
    messages = list(
      self.db.scalars(
        select(AssistantMessage)
        .where(AssistantMessage.user_id == user_id)
        .order_by(AssistantMessage.created_at.desc(), AssistantMessage.id.desc())
        .limit(limit)
      ).all()
    )
    return list(reversed(messages))

  def delete_chunks_for_file(self, file_asset_id: int) -> int:
    result = self.db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.file_asset_id == file_asset_id))
    self.db.commit()
    return result.rowcount or 0

  def create_chunks(self, chunks: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
    if not chunks:
      return []
    self.db.add_all(chunks)
    self.db.commit()
    for chunk in chunks:
      self.db.refresh(chunk)
    return chunks

  def search_chunks(self, query_terms: list[str], course_id: int | None = None, limit: int = 5) -> list[KnowledgeChunk]:
    statement = select(KnowledgeChunk)
    if course_id is not None:
      statement = statement.where(KnowledgeChunk.course_id == course_id)
    chunks = list(self.db.scalars(statement.order_by(KnowledgeChunk.id.desc())).all())
    if not query_terms:
      return chunks[:limit]

    query_embedding = self._embed(" ".join(query_terms))
    scored: list[tuple[float, KnowledgeChunk]] = []
    for chunk in chunks:
      haystack = f"{chunk.title} {chunk.content} {chunk.keywords}".lower()
      keyword_score = sum(haystack.count(term) for term in query_terms)
      vector_score = self._cosine(query_embedding, self._load_embedding(chunk.embedding))
      score = keyword_score + vector_score
      if keyword_score > 0 or vector_score >= 0.35:
        scored.append((score, chunk))

    scored.sort(key=lambda item: (item[0], item[1].id), reverse=True)
    return [chunk for _, chunk in scored[:limit]]

  def count_user_questions(self, user_id: int) -> int:
    return (
      self.db.scalar(
        select(func.count())
        .select_from(AssistantMessage)
        .where(AssistantMessage.user_id == user_id, AssistantMessage.role == "user")
      )
      or 0
    )

  def _embed(self, text: str) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSION
    tokens = re.findall(r"[\w\u4e00-\u9fff]{2,}", text.lower())
    for token in tokens:
      digest = hashlib.sha256(token.encode("utf-8")).digest()
      index = int.from_bytes(digest[:2], "big") % EMBEDDING_DIMENSION
      sign = 1.0 if digest[2] % 2 == 0 else -1.0
      vector[index] += sign
    norm = sum(value * value for value in vector) ** 0.5
    if norm == 0:
      return vector
    return [value / norm for value in vector]

  def _load_embedding(self, raw_embedding: str | None) -> list[float]:
    if not raw_embedding:
      return []
    try:
      values = json.loads(raw_embedding)
    except json.JSONDecodeError:
      return []
    if not isinstance(values, list):
      return []
    return [float(value) for value in values if isinstance(value, int | float)]

  def _cosine(self, left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
      return 0.0
    return sum(left_value * right_value for left_value, right_value in zip(left, right))
