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
