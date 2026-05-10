from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ForumPost(Base):
  __tablename__ = "forum_posts"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  title: Mapped[str] = mapped_column(index=True)
  content: Mapped[str] = mapped_column(Text)
  author_id: Mapped[int] = mapped_column(index=True)
  author_name: Mapped[str]
  course_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ForumComment(Base):
  __tablename__ = "forum_comments"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  post_id: Mapped[int] = mapped_column(ForeignKey("forum_posts.id", ondelete="CASCADE"), index=True)
  author_id: Mapped[int] = mapped_column(index=True)
  author_name: Mapped[str]
  content: Mapped[str] = mapped_column(Text)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ForumLike(Base):
  __tablename__ = "forum_likes"
  __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_forum_like_post_user"),)

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  post_id: Mapped[int] = mapped_column(ForeignKey("forum_posts.id", ondelete="CASCADE"), index=True)
  user_id: Mapped[int] = mapped_column(index=True)
