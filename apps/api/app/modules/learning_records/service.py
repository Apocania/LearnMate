import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.courses.repository import CourseRepository
from app.modules.learning_records.models import LearningEvent
from app.modules.learning_records.repository import LearningRecordRepository
from app.modules.learning_records.schemas import (
  CourseProgressResponse,
  CourseProgressUpdateRequest,
  LearningEventRequest,
  LearningEventResponse,
)


class LearningRecordService:
  def __init__(self, db: Session) -> None:
    self.db = db
    self.repository = LearningRecordRepository(db)
    self.course_repository = CourseRepository(db)

  def record_event(
    self,
    current_user: User,
    event_type: str,
    course_id: int | None = None,
    metadata: dict[str, str] | None = None,
  ) -> LearningEventResponse:
    event = self.repository.create_event(
      user_id=current_user.id,
      course_id=course_id,
      event_type=event_type,
      event_payload=json.dumps(metadata or {}, ensure_ascii=False),
    )
    return self._to_response(event)

  def create_event(self, payload: LearningEventRequest, current_user: User) -> LearningEventResponse:
    return self.record_event(
      current_user,
      event_type=payload.event_type,
      course_id=payload.course_id,
      metadata=payload.event_payload,
    )

  def list_my_events(self, current_user: User, limit: int = 30) -> list[LearningEventResponse]:
    return [self._to_response(event) for event in self.repository.list_events(current_user.id, limit)]

  def update_course_progress(
    self,
    payload: CourseProgressUpdateRequest,
    current_user: User,
  ) -> CourseProgressResponse:
    course = self.course_repository.get_course(payload.course_id)
    if course is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    if current_user.role != "student":
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有学生学习课程时才记录浏览进度")
    if self.course_repository.get_enrollment(payload.course_id, current_user.id) is None:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="加入课程后才会记录学习进度")
    progress = self.repository.upsert_course_progress(
      user_id=current_user.id,
      course_id=payload.course_id,
      progress_percent=payload.progress_percent,
      study_seconds_delta=payload.study_seconds_delta,
      last_position=payload.last_position,
    )
    return CourseProgressResponse.model_validate(progress)

  def _to_response(self, event: LearningEvent) -> LearningEventResponse:
    try:
      payload = json.loads(event.event_payload or "{}")
    except json.JSONDecodeError:
      payload = {}
    if not isinstance(payload, dict):
      payload = {}
    return LearningEventResponse(
      id=event.id,
      user_id=event.user_id,
      course_id=event.course_id,
      event_type=event.event_type,
      event_payload={str(key): str(value) for key, value in payload.items()},
      created_at=event.created_at,
    )
