from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.courses.models import Course, CourseChapter, CourseEnrollment


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

  def get_enrollment(self, course_id: int, student_id: int) -> CourseEnrollment | None:
    return self.db.scalar(
      select(CourseEnrollment).where(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == student_id,
      )
    )

  def enroll_course(self, course: Course, student_id: int, student_name: str) -> CourseEnrollment:
    enrollment = CourseEnrollment(course_id=course.id, student_id=student_id, student_name=student_name)
    self.db.add(enrollment)
    self.db.commit()
    self.db.refresh(enrollment)
    return enrollment

  def leave_course(self, enrollment: CourseEnrollment) -> None:
    self.db.delete(enrollment)
    self.db.commit()

  def count_enrollments(self, course_id: int) -> int:
    return self.db.scalar(
      select(func.count()).select_from(CourseEnrollment).where(CourseEnrollment.course_id == course_id)
    ) or 0

  def list_chapters(self, course_id: int) -> list[CourseChapter]:
    return list(
      self.db.scalars(
        select(CourseChapter)
        .where(CourseChapter.course_id == course_id)
        .order_by(CourseChapter.sort_order.asc(), CourseChapter.id.asc())
      ).all()
    )

  def get_chapter(self, chapter_id: int) -> CourseChapter | None:
    return self.db.get(CourseChapter, chapter_id)

  def create_chapter(self, course_id: int, title: str, description: str, sort_order: int) -> CourseChapter:
    chapter = CourseChapter(course_id=course_id, title=title, description=description, sort_order=sort_order)
    self.db.add(chapter)
    self.db.commit()
    self.db.refresh(chapter)
    return chapter

  def update_chapter(self, chapter: CourseChapter, values: dict[str, str | int]) -> CourseChapter:
    for key, value in values.items():
      setattr(chapter, key, value)
    self.db.commit()
    self.db.refresh(chapter)
    return chapter

  def delete_chapter(self, chapter: CourseChapter) -> None:
    self.db.delete(chapter)
    self.db.commit()
