from pydantic import BaseModel, Field


class LearningEventRequest(BaseModel):
  course_id: str | None = None
  event_type: str
  event_payload: dict[str, str] = Field(default_factory=dict)
