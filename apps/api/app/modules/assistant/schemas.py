from pydantic import BaseModel


class AssistantMessageRequest(BaseModel):
  content: str
  course_id: str | None = None


class AssistantCitation(BaseModel):
  document_id: str
  title: str
  chunk_index: int


class AssistantMessageResponse(BaseModel):
  answer: str
  citations: list[AssistantCitation]

