from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.courses.models import Course, CourseChapter
from app.modules.courses.repository import CourseRepository
from app.modules.courses.schemas import (
  CourseChapterCreate,
  CourseChapterResponse,
  CourseChapterUpdate,
  CourseCreate,
  CourseEnrollmentResponse,
  CourseResponse,
  CourseUpdate,
)
from app.modules.learning_records.service import LearningRecordService


class CourseService:
  def __init__(self, db: Session) -> None:
    self.repository = CourseRepository(db)

  def list_courses(self, current_user: User | None = None) -> list[CourseResponse]:
    include_drafts = current_user is not None and current_user.role == "mentor"
    current_user_id = current_user.id if current_user else None
    courses = self.repository.list_courses(current_user_id=current_user_id, include_drafts=include_drafts)
    return [self._build_course_response(course, current_user) for course in courses]

  def get_course(self, course_id: int, current_user: User | None = None) -> CourseResponse:
    course = self._get_course_or_404(course_id)
    self._ensure_course_visible(course, current_user)
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
    self._ensure_course_visible(course, current_user)
    if self.repository.get_enrollment(course.id, current_user.id) is None:
      self.repository.enroll_course(course, current_user.id, current_user.username)
      LearningRecordService(self.repository.db).record_event(
        current_user,
        "course_enrolled",
        course_id=course.id,
        metadata={"course_title": course.title},
      )
    return self._build_course_response(course, current_user)

  def leave_course(self, course_id: int, current_user: User) -> CourseResponse:
    self._ensure_student(current_user)
    course = self._get_course_or_404(course_id)
    self._ensure_course_visible(course, current_user)
    enrollment = self.repository.get_enrollment(course.id, current_user.id)
    if enrollment is not None:
      self.repository.leave_course(enrollment)
      LearningRecordService(self.repository.db).record_event(
        current_user,
        "course_left",
        course_id=course.id,
        metadata={"course_title": course.title},
      )
    return self._build_course_response(course, current_user)

  def list_chapters(self, course_id: int, current_user: User | None = None) -> list[CourseChapterResponse]:
    course = self._get_course_or_404(course_id)
    self._ensure_course_visible(course, current_user)
    return [CourseChapterResponse.model_validate(chapter) for chapter in self.repository.list_chapters(course_id)]

  def list_enrollments(self, course_id: int, current_user: User) -> list[CourseEnrollmentResponse]:
    self._ensure_course_owner(course_id, current_user)
    return [
      CourseEnrollmentResponse.model_validate(enrollment)
      for enrollment in self.repository.list_enrollments(course_id)
    ]

  def remove_enrollment(self, course_id: int, enrollment_id: int, current_user: User) -> None:
    self._ensure_course_owner(course_id, current_user)
    enrollment = self.repository.get_enrollment_by_id(enrollment_id)
    if enrollment is None or enrollment.course_id != course_id:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生选课记录不存在")
    self.repository.leave_course(enrollment)

  def create_chapter(
    self,
    course_id: int,
    payload: CourseChapterCreate,
    current_user: User,
  ) -> CourseChapterResponse:
    course = self._ensure_course_owner(course_id, current_user)
    chapter = self.repository.create_chapter(
      course_id=course.id,
      title=payload.title,
      description=payload.description,
      sort_order=payload.sort_order,
    )
    LearningRecordService(self.repository.db).record_event(
      current_user,
      "chapter_created",
      course_id=course.id,
      metadata={"course_title": course.title, "chapter_title": chapter.title},
    )
    return CourseChapterResponse.model_validate(chapter)

  def update_chapter(
    self,
    course_id: int,
    chapter_id: int,
    payload: CourseChapterUpdate,
    current_user: User,
  ) -> CourseChapterResponse:
    self._ensure_course_owner(course_id, current_user)
    chapter = self._get_chapter_or_404(chapter_id, course_id)
    values = payload.model_dump(exclude_unset=True)
    return CourseChapterResponse.model_validate(self.repository.update_chapter(chapter, values))

  def delete_chapter(self, course_id: int, chapter_id: int, current_user: User) -> None:
    self._ensure_course_owner(course_id, current_user)
    chapter = self._get_chapter_or_404(chapter_id, course_id)
    self.repository.delete_chapter(chapter)

  def _ensure_course_owner(self, course_id: int, current_user: User) -> Course:
    self._ensure_mentor(current_user)
    course = self._get_course_or_404(course_id)
    if course.teacher_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能管理自己创建的课程")
    return course

  def _ensure_course_visible(self, course: Course, current_user: User | None = None) -> None:
    if course.status == "published":
      return
    if current_user and current_user.role == "mentor" and course.teacher_id == current_user.id:
      return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")

  def _get_chapter_or_404(self, chapter_id: int, course_id: int) -> CourseChapter:
    chapter = self.repository.get_chapter(chapter_id)
    if chapter is None or chapter.course_id != course_id:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="章节不存在")
    return chapter

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
