from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.courses.models import Course
from app.modules.courses.repository import CourseRepository
from app.modules.courses.schemas import CourseCreate, CourseResponse, CourseUpdate


class CourseService:
  def __init__(self, db: Session) -> None:
    self.repository = CourseRepository(db)

  def list_courses(self, current_user: User | None = None) -> list[CourseResponse]:
    return [self._build_course_response(course, current_user) for course in self.repository.list_courses()]

  def get_course(self, course_id: int, current_user: User | None = None) -> CourseResponse:
    course = self._get_course_or_404(course_id)
    return self._build_course_response(course, current_user)

  def _get_course_or_404(self, course_id: int) -> Course:
    course = self.repository.get_course(course_id)
    if course is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    return course

  def create_course(self, payload: CourseCreate, current_user: User) -> CourseResponse:
    self._ensure_mentor(current_user)
    course = self.repository.create_course(
      title=payload.title,
      description=payload.description,
      teacher_id=current_user.id,
      teacher_name=current_user.username,
      status=payload.status,
    )
    return self._build_course_response(course, current_user)

  def update_course(self, course_id: int, payload: CourseUpdate, current_user: User) -> CourseResponse:
    self._ensure_mentor(current_user)
    course = self._get_course_or_404(course_id)
    if course.teacher_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能修改自己创建的课程")

    values = payload.model_dump(exclude_unset=True)
    updated_course = self.repository.update_course(course, values)
    return self._build_course_response(updated_course, current_user)

  def delete_course(self, course_id: int, current_user: User) -> None:
    self._ensure_mentor(current_user)
    course = self._get_course_or_404(course_id)
    if course.teacher_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能删除自己创建的课程")
    self.repository.delete_course(course)

  def enroll_course(self, course_id: int, current_user: User) -> CourseResponse:
    self._ensure_student(current_user)
    course = self._get_course_or_404(course_id)
    if self.repository.get_enrollment(course.id, current_user.id) is None:
      self.repository.enroll_course(course, current_user.id, current_user.username)
    return self._build_course_response(course, current_user)

  def leave_course(self, course_id: int, current_user: User) -> CourseResponse:
    self._ensure_student(current_user)
    course = self._get_course_or_404(course_id)
    enrollment = self.repository.get_enrollment(course.id, current_user.id)
    if enrollment is not None:
      self.repository.leave_course(enrollment)
    return self._build_course_response(course, current_user)

  def _build_course_response(self, course: Course, current_user: User | None = None) -> CourseResponse:
    joined_by_me = False
    if current_user and current_user.role == "student":
      joined_by_me = self.repository.get_enrollment(course.id, current_user.id) is not None

    return CourseResponse(
      id=course.id,
      title=course.title,
      description=course.description,
      teacher_id=course.teacher_id,
      teacher_name=course.teacher_name,
      status=course.status,
      enrollment_count=self.repository.count_enrollments(course.id),
      joined_by_me=joined_by_me,
    )

  def _ensure_student(self, current_user: User) -> None:
    if current_user.role != "student":
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有学生可以加入或退出课程")

  def _ensure_mentor(self, current_user: User) -> None:
    if current_user.role != "mentor":
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有伴学师可以管理课程")
