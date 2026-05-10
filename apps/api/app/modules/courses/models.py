from datetime import datetime

from sqlalchemy import DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Course(Base):
  __tablename__ = "courses"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  title: Mapped[str] = mapped_column(index=True)
  description: Mapped[str] = mapped_column(Text)
  teacher_id: Mapped[int] = mapped_column(index=True)
  teacher_name: Mapped[str]
  status: Mapped[str] = mapped_column(default="published")
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
