from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LearningEvent(Base):
  __tablename__ = "learning_events"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  user_id: Mapped[int]
  course_id: Mapped[int | None]
  event_type: Mapped[str]

