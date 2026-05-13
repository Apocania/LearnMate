from datetime import datetime

from sqlalchemy import Boolean, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserMessage(Base):
  __tablename__ = "user_messages"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  recipient_id: Mapped[int] = mapped_column(index=True)
  recipient_name: Mapped[str]
  sender_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
  sender_name: Mapped[str | None] = mapped_column(nullable=True)
  message_type: Mapped[str] = mapped_column(index=True)
  title: Mapped[str]
  content: Mapped[str] = mapped_column(Text)
  source_type: Mapped[str | None] = mapped_column(nullable=True, index=True)
  source_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
  is_read: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
