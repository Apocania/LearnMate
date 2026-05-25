import json
from io import BytesIO
from types import SimpleNamespace

import anyio
from fastapi import UploadFile

from app.modules.forum.models import ForumPost
from app.modules.forum.service import ForumService


class FakeStorage:
  def __init__(self) -> None:
    self.objects: dict[str, bytes] = {}

  def put_object(self, object_key: str, data: bytes, content_type: str):
    self.objects[object_key] = data
    return SimpleNamespace(provider="minio", object_key=object_key, public_url=None)

  def read_object(self, object_key: str, provider: str | None = None) -> bytes:
    return self.objects[object_key]


class FakeRepository:
  db = object()

  def __init__(self, post: ForumPost | None = None) -> None:
    self.post = post

  def find_post_by_attachment(self, stored_name: str) -> ForumPost | None:
    return self.post


def test_forum_attachment_upload_uses_object_storage(monkeypatch) -> None:
  fake_storage = FakeStorage()
  monkeypatch.setattr("app.modules.forum.service.ObjectStorageClient", lambda: fake_storage)
  service = ForumService(object())
  upload = UploadFile(filename="notes.txt", file=BytesIO(b"hello"), headers={"content-type": "text/plain"})

  attachments = anyio.run(service._store_attachments, [upload])

  assert attachments[0]["storage_provider"] == "minio"
  assert str(attachments[0]["object_key"]).startswith("forum-attachments/")
  assert fake_storage.objects[str(attachments[0]["object_key"])] == b"hello"
  assert attachments[0]["url"].startswith("/api/forum/attachments/")


def test_forum_attachment_download_reads_object_storage_metadata(monkeypatch) -> None:
  fake_storage = FakeStorage()
  fake_storage.objects["forum-attachments/stored.txt"] = b"stored content"
  monkeypatch.setattr("app.modules.forum.service.ObjectStorageClient", lambda: fake_storage)
  post = ForumPost(
    id=1,
    title="post",
    content="content",
    author_id=2,
    author_name="mentor",
    attachments=json.dumps(
      [
        {
          "original_name": "notes.txt",
          "stored_name": "stored.txt",
          "storage_provider": "minio",
          "object_key": "forum-attachments/stored.txt",
          "content_type": "text/plain",
          "size": 14,
          "url": "/api/forum/attachments/stored.txt/download",
        }
      ]
    ),
  )
  service = ForumService(object())
  service.repository = FakeRepository(post)

  data, content_type, original_name = service.get_attachment("stored.txt")

  assert data == b"stored content"
  assert content_type == "text/plain"
  assert original_name == "notes.txt"
