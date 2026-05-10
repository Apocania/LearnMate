from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.courses.models import Course


class CourseRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def list_courses(self) -> list[Course]:
    return list(self.db.scalars(select(Course).order_by(Course.id.desc())).all())

  def get_course(self, course_id: int) -> Course | None:
    return self.db.get(Course, course_id)

  def create_course(self, title: str, description: str, teacher_id: int, teacher_name: str, status: str) -> Course:
    course = Course(
      title=title,
      description=description,
      teacher_id=teacher_id,
      teacher_name=teacher_name,
      status=status,
    )
    self.db.add(course)
    self.db.commit()
    self.db.refresh(course)
    return course

  def update_course(self, course: Course, values: dict[str, str]) -> Course:
    for key, value in values.items():
      setattr(course, key, value)
    self.db.commit()
    self.db.refresh(course)
    return course

  def delete_course(self, course: Course) -> None:
    self.db.delete(course)
    self.db.commit()
