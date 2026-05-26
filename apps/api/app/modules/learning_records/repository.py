from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.learning_records.models import CourseLearningProgress, LearningEvent


class LearningRecordRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def create_event(
    self,
    user_id: int,
    event_type: str,
    course_id: int | None = None,
    event_payload: str = "{}",
  ) -> LearningEvent:
    event = LearningEvent(user_id=user_id, course_id=course_id, event_type=event_type, event_payload=event_payload)
    self.db.add(event)
    self.db.commit()
    self.db.refresh(event)
    return event

  def list_events(self, user_id: int, limit: int = 30) -> list[LearningEvent]:
    return list(
      self.db.scalars(
        select(LearningEvent)
        .where(LearningEvent.user_id == user_id)
        .order_by(LearningEvent.created_at.desc(), LearningEvent.id.desc())
        .limit(limit)
      ).all()
    )

  def count_events(self, user_id: int, event_type: str | None = None) -> int:
    statement = select(func.count()).select_from(LearningEvent).where(LearningEvent.user_id == user_id)
    if event_type is not None:
      statement = statement.where(LearningEvent.event_type == event_type)
    return self.db.scalar(statement) or 0

  def get_course_progress(self, user_id: int, course_id: int) -> CourseLearningProgress | None:
    return self.db.scalar(
      select(CourseLearningProgress).where(
        CourseLearningProgress.user_id == user_id,
        CourseLearningProgress.course_id == course_id,
      )
    )

  def upsert_course_progress(
    self,
    user_id: int,
    course_id: int,
    progress_percent: int,
    study_seconds_delta: int,
    last_position: str,
  ) -> CourseLearningProgress:
    progress = self.get_course_progress(user_id, course_id)
    if progress is None:
      progress = CourseLearningProgress(
        user_id=user_id,
        course_id=course_id,
        progress_percent=progress_percent,
        study_seconds=study_seconds_delta,
        last_position=last_position,
      )
      self.db.add(progress)
    else:
      progress.progress_percent = max(progress.progress_percent, progress_percent)
      progress.study_seconds += study_seconds_delta
      progress.last_position = last_position or progress.last_position
      self.db.add(progress)
    self.db.commit()
    self.db.refresh(progress)
    return progress
