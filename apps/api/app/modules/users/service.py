from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.infrastructure.object_storage import ObjectStorageClient
from app.modules.auth.models import User

AVATAR_PREFIX = "avatars"
LEGACY_AVATAR_DIR = Path(__file__).resolve().parents[3] / "storage" / "avatars"
AVATAR_TYPES = {
  "image/jpeg": ".jpg",
  "image/png": ".png",
  "image/webp": ".webp",
  "image/gif": ".gif",
}
MAX_AVATAR_SIZE_BYTES = 3 * 1024 * 1024


class UserService:
  def __init__(self, db: Session) -> None:
    self.db = db
    self.storage = ObjectStorageClient()

  async def update_avatar(self, upload: UploadFile, current_user: User) -> User:
    content_type = upload.content_type or ""
    suffix = AVATAR_TYPES.get(content_type)
    if suffix is None:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="头像仅支持 JPG、PNG、WebP 或 GIF")

    content = await upload.read()
    if len(content) > MAX_AVATAR_SIZE_BYTES:
      raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="头像不能超过 3MB")
    if not content:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="头像文件不能为空")

    stored_name = f"user-{current_user.id}-{uuid4().hex}{suffix}"
    object_key = f"{AVATAR_PREFIX}/{stored_name}"
    self.storage.put_object(object_key, content, content_type)

    self._remove_old_avatar(current_user.avatar_url)
    current_user.avatar_url = f"/api/users/avatars/{stored_name}"
    self.db.add(current_user)
    self.db.commit()
    self.db.refresh(current_user)
    return current_user

  def get_avatar(self, stored_name: str) -> tuple[bytes, str]:
    self._ensure_safe_name(stored_name)
    content_type = self._get_content_type(stored_name)
    legacy_path = LEGACY_AVATAR_DIR / stored_name
    if legacy_path.exists():
      return legacy_path.read_bytes(), content_type
    return self.storage.read_object(f"{AVATAR_PREFIX}/{stored_name}"), content_type

  def _remove_old_avatar(self, avatar_url: str | None) -> None:
    if not avatar_url:
      return
    if avatar_url.startswith("/static/avatars/"):
      (LEGACY_AVATAR_DIR / Path(avatar_url).name).unlink(missing_ok=True)
      return
    if avatar_url.startswith("/api/users/avatars/"):
      old_name = Path(avatar_url).name
      try:
        self.storage.delete_object(f"{AVATAR_PREFIX}/{old_name}")
      except Exception:
        return

  def _ensure_safe_name(self, stored_name: str) -> None:
    if "/" in stored_name or "\\" in stored_name or not stored_name:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="头像路径无效")

  def _get_content_type(self, stored_name: str) -> str:
    suffix = Path(stored_name).suffix.lower()
    content_types = {value: key for key, value in AVATAR_TYPES.items()}
    return content_types.get(suffix, "application/octet-stream")
