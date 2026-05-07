from app.infrastructure.vector_store import VectorStore


class RetrievalService:
  def __init__(self) -> None:
    self.vector_store = VectorStore()

  def retrieve(self, question: str, course_id: str | None = None) -> list[dict[str, str]]:
    return self.vector_store.search(question, course_id)

