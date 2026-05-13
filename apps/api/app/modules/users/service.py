from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User

AVATAR_DIR = Path(__file__).resolve().parents[3] / "storage" / "avatars"
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
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)

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
    target_path = AVATAR_DIR / stored_name
    target_path.write_bytes(content)

    self._remove_old_avatar(current_user.avatar_url)
    current_user.avatar_url = f"/static/avatars/{stored_name}"
    self.db.add(current_user)
    self.db.commit()
    self.db.refresh(current_user)
    return current_user

  def _remove_old_avatar(self, avatar_url: str | None) -> None:
    if not avatar_url or not avatar_url.startswith("/static/avatars/"):
      return
    old_path = AVATAR_DIR / Path(avatar_url).name
    if old_path.exists():
      old_path.unlink()
