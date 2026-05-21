from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
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


class CourseEnrollment(Base):
  __tablename__ = "course_enrollments"
  __table_args__ = (UniqueConstraint("course_id", "student_id", name="uq_course_enrollment_course_student"),)

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
  student_id: Mapped[int] = mapped_column(index=True)
  student_name: Mapped[str]
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CourseChapter(Base):
  __tablename__ = "course_chapters"
  __table_args__ = (UniqueConstraint("course_id", "sort_order", name="uq_course_chapter_course_sort"),)

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
  title: Mapped[str] = mapped_column(index=True)
  description: Mapped[str] = mapped_column(Text, default="", server_default="")
  sort_order: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
