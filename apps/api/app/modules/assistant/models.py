from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AssistantSession(Base):
  __tablename__ = "assistant_sessions"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  user_id: Mapped[int] = mapped_column(index=True)
  course_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
  title: Mapped[str]
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AssistantMessage(Base):
  __tablename__ = "assistant_messages"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  session_id: Mapped[int | None] = mapped_column(ForeignKey("assistant_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
  user_id: Mapped[int] = mapped_column(index=True)
  course_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
  role: Mapped[str] = mapped_column(index=True)
  content: Mapped[str] = mapped_column(Text)
  citations: Mapped[str] = mapped_column(Text, default="[]", server_default="[]")
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class KnowledgeChunk(Base):
  __tablename__ = "knowledge_chunks"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  file_asset_id: Mapped[int | None] = mapped_column(ForeignKey("file_assets.id", ondelete="CASCADE"), nullable=True, index=True)
  course_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
  chapter_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
  document_id: Mapped[str] = mapped_column(index=True)
  title: Mapped[str]
  chunk_index: Mapped[int]
  content: Mapped[str] = mapped_column(Text)
  keywords: Mapped[str] = mapped_column(Text, default="", server_default="")
  embedding: Mapped[str] = mapped_column(Text, default="[]", server_default="[]")
  source_url: Mapped[str | None] = mapped_column(nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
