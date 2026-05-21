from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.learning_records.service import LearningRecordService


def test_learning_records_require_login() -> None:
  client = TestClient(app)
  response = client.get("/api/learning-records")

  assert response.status_code == 401


def test_learning_record_endpoint_uses_current_user() -> None:
  current_user = User(id=30, username="student_events", role="student", password_hash="unused", avatar_url=None)

  def override_current_user() -> User:
    return current_user

  def override_db() -> Iterator[object]:
    yield object()

  def create_event_for_test(self: LearningRecordService, payload, user: User):
    from datetime import datetime, timezone

    from app.modules.learning_records.schemas import LearningEventResponse

    assert user.id == 30
    return LearningEventResponse(
      id=1,
      user_id=user.id,
      course_id=payload.course_id,
      event_type=payload.event_type,
      event_payload=payload.event_payload,
      created_at=datetime.now(timezone.utc),
    )

  original_method = LearningRecordService.create_event
  LearningRecordService.create_event = create_event_for_test
  app.dependency_overrides[get_current_user] = override_current_user
  app.dependency_overrides[get_db] = override_db

  try:
    client = TestClient(app)
    response = client.post(
      "/api/learning-records",
      json={"course_id": 2, "event_type": "course_viewed", "event_payload": {"source": "test"}},
    )
  finally:
    LearningRecordService.create_event = original_method
    app.dependency_overrides.clear()

  assert response.status_code == 201
  body = response.json()
  assert body["user_id"] == 30
  assert body["event_type"] == "course_viewed"
  assert body["event_payload"] == {"source": "test"}
