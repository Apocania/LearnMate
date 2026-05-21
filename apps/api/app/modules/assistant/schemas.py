from pydantic import BaseModel


class AssistantMessageRequest(BaseModel):
  content: str
  course_id: int | None = None
  session_id: int | None = None


class AssistantCitation(BaseModel):
  document_id: str
  title: str
  chunk_index: int
  snippet: str = ""
  source_url: str | None = None


class AssistantMessageResponse(BaseModel):
  session_id: int | None = None
  answer: str
  citations: list[AssistantCitation]
