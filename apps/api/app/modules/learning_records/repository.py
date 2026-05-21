from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.learning_records.models import LearningEvent


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
