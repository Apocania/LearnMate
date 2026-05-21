from app.infrastructure.vector_store import VectorStore
from sqlalchemy.orm import Session


class RetrievalService:
  def __init__(self, db: Session) -> None:
    self.vector_store = VectorStore(db)

  def retrieve(self, question: str, course_id: int | None = None) -> list[dict[str, str]]:
    return self.vector_store.search(question, course_id)
