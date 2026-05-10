from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.courses.models import Course
from app.modules.courses.repository import CourseRepository
from app.modules.courses.schemas import CourseCreate, CourseUpdate


class CourseService:
  def __init__(self, db: Session) -> None:
    self.repository = CourseRepository(db)

  def list_courses(self) -> list[Course]:
    return self.repository.list_courses()

  def get_course(self, course_id: int) -> Course:
    course = self.repository.get_course(course_id)
    if course is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    return course

  def create_course(self, payload: CourseCreate, current_user: User) -> Course:
    return self.repository.create_course(
      title=payload.title,
      description=payload.description,
      teacher_id=current_user.id,
      teacher_name=current_user.username,
      status=payload.status,
    )

  def update_course(self, course_id: int, payload: CourseUpdate, current_user: User) -> Course:
    course = self.get_course(course_id)
    if course.teacher_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能修改自己创建的课程")

    values = payload.model_dump(exclude_unset=True)
    return self.repository.update_course(course, values)

  def delete_course(self, course_id: int, current_user: User) -> None:
    course = self.get_course(course_id)
    if course.teacher_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能删除自己创建的课程")
    self.repository.delete_course(course)
