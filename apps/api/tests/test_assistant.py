from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.modules.assistant.chat_service import AssistantChatService
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User


def test_assistant_requires_login() -> None:
  client = TestClient(app)
  response = client.post("/api/assistant/messages", json={"content": "hello"})

  assert response.status_code == 401


def test_assistant_response_includes_session_and_citations() -> None:
  current_user = User(id=41, username="student_ai", role="student", password_hash="unused", avatar_url=None)

  def override_current_user() -> User:
    return current_user

  def override_db() -> Iterator[object]:
    yield object()

  def answer_for_test(self: AssistantChatService, question: str, user: User, course_id=None, session_id=None):
    from app.modules.assistant.schemas import AssistantCitation, AssistantMessageResponse

    assert question == "什么是梯度下降？"
    assert user.id == 41
    assert course_id == 3
    return AssistantMessageResponse(
      session_id=99,
      answer="梯度下降是一种沿负梯度方向更新参数的优化方法。",
      citations=[
        AssistantCitation(
          document_id="file:1",
          title="机器学习基础.txt",
          chunk_index=1,
          snippet="负梯度方向通常对应局部下降最快方向。",
          source_url="/api/files/1/download",
        )
      ],
    )

  original_method = AssistantChatService.answer
  AssistantChatService.answer = answer_for_test
  app.dependency_overrides[get_current_user] = override_current_user
  app.dependency_overrides[get_db] = override_db

  try:
    client = TestClient(app)
    response = client.post("/api/assistant/messages", json={"content": "什么是梯度下降？", "course_id": 3})
  finally:
    AssistantChatService.answer = original_method
    app.dependency_overrides.clear()

  assert response.status_code == 200
  body = response.json()
  assert body["session_id"] == 99
  assert body["citations"][0]["title"] == "机器学习基础.txt"


def test_assistant_stream_returns_meta_delta_and_done() -> None:
  current_user = User(id=42, username="stream_student", role="student", password_hash="unused", avatar_url=None)

  def override_current_user() -> User:
    return current_user

  def override_db() -> Iterator[object]:
    yield object()

  def stream_for_test(self: AssistantChatService, question: str, user: User, course_id=None, session_id=None):
    assert question == "请流式回答"
    assert user.id == 42
    yield {"type": "meta", "session_id": 7, "citations": []}
    yield {"type": "delta", "content": "第一段"}
    yield {"type": "delta", "content": "第二段"}
    yield {"type": "done"}

  original_method = AssistantChatService.stream_answer
  AssistantChatService.stream_answer = stream_for_test
  app.dependency_overrides[get_current_user] = override_current_user
  app.dependency_overrides[get_db] = override_db

  try:
    client = TestClient(app)
    response = client.post("/api/assistant/messages/stream", json={"content": "请流式回答"})
  finally:
    AssistantChatService.stream_answer = original_method
    app.dependency_overrides.clear()

  assert response.status_code == 200
  events = [line for line in response.text.splitlines() if line]
  assert '"type": "meta"' in events[0]
  assert '"content": "第一段"' in events[1]
  assert '"type": "done"' in events[-1]


def test_assistant_session_history_is_user_scoped() -> None:
  owner = User(id=101, username="owner_student", role="student", password_hash="unused", avatar_url=None)
  other = User(id=202, username="other_student", role="student", password_hash="unused", avatar_url=None)

  class FakeSession:
    id = 9
    user_id = owner.id
    course_id = None
    title = "owner session"

  class FakeRepository:
    def __init__(self) -> None:
      self.created_for_user_id = 0

    def get_session(self, session_id: int):
      if session_id == 9:
        return FakeSession()
      if session_id == 10:
        session = FakeSession()
        session.id = 10
        session.user_id = other.id
        session.title = "新的伴学对话"
        return session
      return None

    def get_latest_session(self, user_id: int, course_id=None):
      assert user_id == other.id
      return None

    def create_session(self, user_id: int, title: str, course_id=None):
      self.created_for_user_id = user_id
      session = FakeSession()
      session.id = 10
      session.user_id = user_id
      session.course_id = course_id
      session.title = title
      return session

    def list_recent_messages(self, user_id: int, session_id: int, limit: int = 12):
      assert user_id == other.id
      assert session_id == 10
      return []

  service = AssistantChatService.__new__(AssistantChatService)
  service.repository = FakeRepository()

  response = service.get_current_session(other, session_id=9)

  assert response.id == 10
  assert response.messages == []
