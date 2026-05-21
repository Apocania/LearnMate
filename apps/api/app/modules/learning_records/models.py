from datetime import datetime

from sqlalchemy import DateTime, Text, func
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
