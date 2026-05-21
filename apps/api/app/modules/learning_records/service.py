import json

from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.learning_records.models import LearningEvent
from app.modules.learning_records.repository import LearningRecordRepository
from app.modules.learning_records.schemas import LearningEventRequest, LearningEventResponse


class LearningRecordService:
  def __init__(self, db: Session) -> None:
    self.repository = LearningRecordRepository(db)

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
