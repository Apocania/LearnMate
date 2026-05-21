from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.courses.service import CourseService


def test_course_chapters_can_be_listed_publicly() -> None:
  def override_db() -> Iterator[object]:
    yield object()

  def list_chapters_for_test(self: CourseService, course_id: int):
    from app.modules.courses.schemas import CourseChapterResponse

    assert course_id == 5
    return [CourseChapterResponse(id=1, course_id=5, title="导论", description="课程目标", sort_order=1)]

  original_method = CourseService.list_chapters
  CourseService.list_chapters = list_chapters_for_test
  app.dependency_overrides[get_db] = override_db

  try:
    client = TestClient(app)
    response = client.get("/api/courses/5/chapters")
  finally:
    CourseService.list_chapters = original_method
    app.dependency_overrides.clear()

  assert response.status_code == 200
  assert response.json()[0]["title"] == "导论"


def test_create_course_chapter_requires_login() -> None:
  client = TestClient(app)
  response = client.post("/api/courses/5/chapters", json={"title": "导论", "description": "", "sort_order": 1})

  assert response.status_code == 401


def test_create_course_chapter_uses_current_user() -> None:
  current_user = User(id=42, username="mentor_chapter", role="mentor", password_hash="unused", avatar_url=None)

  def override_current_user() -> User:
    return current_user

  def override_db() -> Iterator[object]:
    yield object()

  def create_chapter_for_test(self: CourseService, course_id: int, payload, user: User):
    from app.modules.courses.schemas import CourseChapterResponse

    assert course_id == 5
    assert payload.title == "导论"
    assert user.id == 42
    return CourseChapterResponse(id=7, course_id=5, title=payload.title, description="", sort_order=1)

  original_method = CourseService.create_chapter
  CourseService.create_chapter = create_chapter_for_test
  app.dependency_overrides[get_current_user] = override_current_user
  app.dependency_overrides[get_db] = override_db

  try:
    client = TestClient(app)
    response = client.post("/api/courses/5/chapters", json={"title": "导论", "description": "", "sort_order": 1})
  finally:
    CourseService.create_chapter = original_method
    app.dependency_overrides.clear()

  assert response.status_code == 201
  assert response.json()["id"] == 7
