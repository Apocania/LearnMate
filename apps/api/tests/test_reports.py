from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.reports.service import LearningReportService


def test_report_requires_login() -> None:
  client = TestClient(app)
  response = client.get("/api/reports/me")

  assert response.status_code == 401


def test_report_returns_current_user_summary() -> None:
  current_user = User(id=7, username="student_demo", role="student", password_hash="unused")

  def override_current_user() -> User:
    return current_user

  def override_db() -> Iterator[object]:
    yield object()

  def get_my_report_for_test(self: LearningReportService, user: User):
    from app.modules.reports.schemas import LearningProgressItem, MyLearningReport

    return MyLearningReport(
      user_id=user.id,
      username=user.username,
      role=user.role,
      enrolled_course_count=2,
      created_course_count=0,
      forum_post_count=1,
      forum_comment_count=3,
      ai_question_count=0,
      estimated_study_hours=4.0,
      progress=[LearningProgressItem(label="课程参与", percent=50)],
      recent_activities=["加入课程：Python 入门"],
      suggestions=["继续参与讨论。"],
    )

  original_service = LearningReportService.get_my_report
  LearningReportService.get_my_report = get_my_report_for_test
  app.dependency_overrides[get_current_user] = override_current_user
  app.dependency_overrides[get_db] = override_db

  try:
    client = TestClient(app)
    response = client.get("/api/reports/me")
  finally:
    LearningReportService.get_my_report = original_service
    app.dependency_overrides.clear()

  assert response.status_code == 200
  body = response.json()
  assert body["user_id"] == 7
  assert body["username"] == "student_demo"
  assert body["enrolled_course_count"] == 2
  assert body["progress"][0]["label"] == "课程参与"
