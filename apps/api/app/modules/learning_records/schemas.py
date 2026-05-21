from datetime import datetime

from pydantic import BaseModel, Field


class LearningEventRequest(BaseModel):
  course_id: int | None = None
  event_type: str
  event_payload: dict[str, str] = Field(default_factory=dict)


class LearningEventResponse(BaseModel):
  id: int
  user_id: int
  course_id: int | None = None
  event_type: str
  event_payload: dict[str, str] = Field(default_factory=dict)
  created_at: datetime
