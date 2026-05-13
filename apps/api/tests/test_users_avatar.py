from collections.abc import Iterator
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.users import service as user_service_module
from app.modules.users.service import UserService


class DummyDb:
  def add(self, user: User) -> None:
    self.user = user

  def commit(self) -> None:
    return None

  def refresh(self, user: User) -> None:
    return None


def test_upload_avatar_requires_login() -> None:
  client = TestClient(app)
  response = client.post("/api/users/me/avatar", files={"file": ("avatar.png", b"image", "image/png")})

  assert response.status_code == 401


def test_avatar_service_stores_file_and_updates_user(tmp_path: Path, monkeypatch) -> None:
  monkeypatch.setattr(user_service_module, "AVATAR_DIR", tmp_path)
  user = User(id=9, username="avatar_user", role="student", password_hash="unused", avatar_url=None)
  upload = UploadFile(filename="avatar.png", file=BytesIO(b"fake image bytes"), headers={"content-type": "image/png"})

  import anyio

  updated_user = anyio.run(UserService(DummyDb()).update_avatar, upload, user)

  assert updated_user.avatar_url is not None
  assert updated_user.avatar_url.startswith("/static/avatars/user-9-")
  assert (tmp_path / Path(updated_user.avatar_url).name).read_bytes() == b"fake image bytes"


def test_upload_avatar_endpoint_returns_updated_user(tmp_path: Path, monkeypatch) -> None:
  monkeypatch.setattr(user_service_module, "AVATAR_DIR", tmp_path)
  current_user = User(id=10, username="student_avatar", role="student", password_hash="unused", avatar_url=None)

  def override_current_user() -> User:
    return current_user

  def override_db() -> Iterator[DummyDb]:
    yield DummyDb()

  app.dependency_overrides[get_current_user] = override_current_user

  try:
    from app.core.database import get_db

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    response = client.post("/api/users/me/avatar", files={"file": ("avatar.png", b"image", "image/png")})
  finally:
    app.dependency_overrides.clear()

  assert response.status_code == 200
  body = response.json()
  assert body["id"] == 10
  assert body["avatar_url"].startswith("/static/avatars/user-10-")
