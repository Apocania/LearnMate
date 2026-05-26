from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LearningEvent(Base):
  __tablename__ = "learning_events"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  user_id: Mapped[int] = mapped_column(index=True)
  course_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
  event_type: Mapped[str] = mapped_column(index=True)
  event_payload: Mapped[str] = mapped_column(Text, default="{}", server_default="{}")
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CourseLearningProgress(Base):
  __tablename__ = "course_learning_progress"
  __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_course_learning_progress_user_course"),)

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  user_id: Mapped[int] = mapped_column(index=True)
  course_id: Mapped[int] = mapped_column(index=True)
  progress_percent: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
  study_seconds: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
  last_position: Mapped[str] = mapped_column(default="", server_default="")
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
