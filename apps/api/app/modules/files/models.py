from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FileAsset(Base):
  __tablename__ = "file_assets"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  original_name: Mapped[str]
  stored_name: Mapped[str]
  content_type: Mapped[str]
  size: Mapped[int]
  course_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
  chapter_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
  storage_provider: Mapped[str] = mapped_column(default="local", server_default="local")
  object_key: Mapped[str]
  public_url: Mapped[str | None] = mapped_column(nullable=True)
  uploader_id: Mapped[int] = mapped_column(index=True)
  uploader_name: Mapped[str]
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
