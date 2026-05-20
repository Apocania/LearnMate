from datetime import datetime

from pydantic import BaseModel, Field


class ForumPostCreate(BaseModel):
  title: str
  content: str
  course_id: int | None = None


class ForumAttachmentResponse(BaseModel):
  original_name: str
  stored_name: str
  content_type: str
  size: int
  url: str


class ForumCommentCreate(BaseModel):
  content: str


class ForumCommentResponse(BaseModel):
  id: int
  post_id: int
  author_id: int
  author_name: str
  author_avatar_url: str | None = None
  content: str
  created_at: datetime
  can_delete: bool = False

  model_config = {"from_attributes": True}


class ForumPostResponse(BaseModel):
  id: int
  title: str
  content: str
  author_id: int
  author_name: str
  author_avatar_url: str | None = None
  attachments: list[ForumAttachmentResponse] = Field(default_factory=list)
  course_id: int | None
  created_at: datetime
  like_count: int
  comment_count: int
  liked_by_me: bool = False


class ForumLikeResponse(BaseModel):
  liked: bool
  like_count: int
