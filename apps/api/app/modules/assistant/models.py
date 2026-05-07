from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AssistantSession(Base):
  __tablename__ = "assistant_sessions"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  user_id: Mapped[int]
  course_id: Mapped[int | None]
  title: Mapped[str]

