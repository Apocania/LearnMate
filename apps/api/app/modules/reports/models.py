from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LearningReport(Base):
  __tablename__ = "learning_reports"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  user_id: Mapped[int]
  course_id: Mapped[int | None]
  summary: Mapped[str]

