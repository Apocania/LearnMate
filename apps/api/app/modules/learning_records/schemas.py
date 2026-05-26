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


class CourseProgressUpdateRequest(BaseModel):
  course_id: int
  progress_percent: int = Field(ge=0, le=100)
  study_seconds_delta: int = Field(default=0, ge=0, le=600)
  last_position: str = Field(default="", max_length=120)


class CourseProgressResponse(BaseModel):
  id: int
  user_id: int
  course_id: int
  progress_percent: int
  study_seconds: int
  last_position: str = ""
  created_at: datetime
  updated_at: datetime

  model_config = {"from_attributes": True}
