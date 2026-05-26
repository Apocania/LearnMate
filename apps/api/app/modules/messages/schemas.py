from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


MessageType = Literal["like", "comment", "private", "announcement"]


class UserMessageResponse(BaseModel):
  id: int
  recipient_id: int
  recipient_name: str
  sender_id: int | None = None
  sender_name: str | None = None
  message_type: MessageType
  title: str
  content: str
  source_type: str | None = None
  source_id: int | None = None
  is_read: bool
  created_at: datetime

  model_config = {"from_attributes": True}


class PrivateMessageCreate(BaseModel):
  course_id: int | None = None
  recipient_username: str = Field(min_length=3, max_length=32)
  title: str = Field(min_length=1, max_length=80)
  content: str = Field(min_length=1, max_length=1000)


class AnnouncementCreate(BaseModel):
  course_id: int | None = None
  title: str = Field(min_length=1, max_length=80)
  content: str = Field(min_length=1, max_length=1200)


class AnnouncementResult(BaseModel):
  created_count: int


class UnreadCountResponse(BaseModel):
  unread_count: int


class StudentRecipientResponse(BaseModel):
  id: int
  username: str
  avatar_url: str | None = None
  course_id: int
  course_title: str
