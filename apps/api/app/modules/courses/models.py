from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Course(Base):
  __tablename__ = "courses"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  title: Mapped[str]
  description: Mapped[str]
  teacher_id: Mapped[int]
  status: Mapped[str]

