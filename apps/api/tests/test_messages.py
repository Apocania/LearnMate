from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.messages.service import MessageService


def test_messages_require_login() -> None:
  client = TestClient(app)
  response = client.get("/api/messages")

  assert response.status_code == 401


def test_unread_count_uses_current_user() -> None:
  current_user = User(id=12, username="student_msg", role="student", password_hash="unused", avatar_url=None)

  def override_current_user() -> User:
    return current_user

  def override_db() -> Iterator[object]:
    yield object()

  def get_unread_count_for_test(self: MessageService, user: User) -> int:
    assert user.id == 12
    return 3

  original_method = MessageService.get_unread_count
  MessageService.get_unread_count = get_unread_count_for_test
  app.dependency_overrides[get_current_user] = override_current_user
  app.dependency_overrides[get_db] = override_db

  try:
    client = TestClient(app)
    response = client.get("/api/messages/unread-count")
  finally:
    MessageService.get_unread_count = original_method
    app.dependency_overrides.clear()

  assert response.status_code == 200
  assert response.json() == {"unread_count": 3}


def test_private_message_requires_mentor() -> None:
  current_user = User(id=13, username="student_msg", role="student", password_hash="unused", avatar_url=None)

  def override_current_user() -> User:
    return current_user

  def override_db() -> Iterator[object]:
    yield object()

  app.dependency_overrides[get_current_user] = override_current_user
  app.dependency_overrides[get_db] = override_db

  try:
    client = TestClient(app)
    response = client.post(
      "/api/messages/private",
      json={"recipient_username": "target_student", "title": "hi", "content": "hello"},
    )
  finally:
    app.dependency_overrides.clear()

  assert response.status_code == 403
