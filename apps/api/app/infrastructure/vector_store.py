import re

from sqlalchemy.orm import Session

from app.modules.assistant.repository import AssistantRepository


class VectorStore:
  def __init__(self, db: Session) -> None:
    self.repository = AssistantRepository(db)

  def search(self, query: str, course_id: int | None = None) -> list[dict[str, str]]:
    if course_id is None:
      return []
    terms = self._tokenize(query)
    chunks = self.repository.search_chunks(terms, course_id=course_id)
    return [
      {
        "document_id": chunk.document_id,
        "title": chunk.title,
        "chunk_index": str(chunk.chunk_index),
        "content": chunk.content,
        "source_url": chunk.source_url or "",
      }
      for chunk in chunks
    ]

  def _tokenize(self, query: str) -> list[str]:
    tokens = re.findall(r"[\w\u4e00-\u9fff]{2,}", query.lower())
    return list(dict.fromkeys(tokens))
