from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.files.models import FileAsset
from app.modules.files.repository import FileRepository
from app.modules.files.schemas import FileAssetResponse

UPLOAD_DIR = Path(__file__).resolve().parents[3] / "storage" / "uploads"


class FileService:
  def __init__(self, db: Session) -> None:
    self.repository = FileRepository(db)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

  def list_files(self) -> list[FileAssetResponse]:
    return [self._to_response(file_asset) for file_asset in self.repository.list_files()]

  async def upload_file(self, upload: UploadFile, current_user: User) -> FileAssetResponse:
    original_name = upload.filename or "unnamed-file"
    suffix = Path(original_name).suffix
    stored_name = f"{uuid4().hex}{suffix}"
    target_path = UPLOAD_DIR / stored_name

    content = await upload.read()
    target_path.write_bytes(content)

    file_asset = self.repository.create_file(
      original_name=original_name,
      stored_name=stored_name,
      content_type=upload.content_type or "application/octet-stream",
      size=len(content),
      uploader_id=current_user.id,
      uploader_name=current_user.username,
    )
    return self._to_response(file_asset)

  def get_file_path(self, file_id: int) -> tuple[FileAsset, Path]:
    file_asset = self.repository.get_file(file_id)
    if file_asset is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    path = UPLOAD_DIR / file_asset.stored_name
    if not path.exists():
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件已丢失")

    return file_asset, path

  def _to_response(self, file_asset: FileAsset) -> FileAssetResponse:
    return FileAssetResponse(
      id=file_asset.id,
      original_name=file_asset.original_name,
      stored_name=file_asset.stored_name,
      content_type=file_asset.content_type,
      size=file_asset.size,
      uploader_id=file_asset.uploader_id,
      uploader_name=file_asset.uploader_name,
      created_at=file_asset.created_at,
      url=f"/api/files/{file_asset.id}/download",
    )

