from datetime import datetime

from pydantic import BaseModel


class ForumPostCreate(BaseModel):
  title: str
  content: str
  course_id: int | None = None


class ForumCommentCreate(BaseModel):
  content: str


class ForumCommentResponse(BaseModel):
  id: int
  post_id: int
  author_id: int
  author_name: str
  content: str
  created_at: datetime

  model_config = {"from_attributes": True}


class ForumPostResponse(BaseModel):
  id: int
  title: str
  content: str
  author_id: int
  author_name: str
  course_id: int | None
  created_at: datetime
  like_count: int
  comment_count: int
  liked_by_me: bool = False


class ForumLikeResponse(BaseModel):
  liked: bool
  like_count: int
