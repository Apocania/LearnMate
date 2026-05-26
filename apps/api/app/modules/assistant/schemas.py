from pydantic import BaseModel


class AssistantMessageRequest(BaseModel):
  content: str
  course_id: int | None = None
  session_id: int | None = None
  mode: str = "qa"


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


class AssistantHistoryMessage(BaseModel):
  id: int
  role: str
  content: str
  citations: list[AssistantCitation] = []


class AssistantSessionResponse(BaseModel):
  id: int
  course_id: int | None = None
  title: str
  messages: list[AssistantHistoryMessage] = []


class AssistantSessionCreateRequest(BaseModel):
  course_id: int | None = None
  title: str = "新的伴学对话"
