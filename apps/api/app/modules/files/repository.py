from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.files.models import FileAsset


class FileRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def list_files(self) -> list[FileAsset]:
    return list(self.db.scalars(select(FileAsset).order_by(FileAsset.id.desc())).all())

  def get_file(self, file_id: int) -> FileAsset | None:
    return self.db.get(FileAsset, file_id)

  def create_file(
    self,
    original_name: str,
    stored_name: str,
    content_type: str,
    size: int,
    uploader_id: int,
    uploader_name: str,
  ) -> FileAsset:
    file_asset = FileAsset(
      original_name=original_name,
      stored_name=stored_name,
      content_type=content_type,
      size=size,
      uploader_id=uploader_id,
      uploader_name=uploader_name,
    )
    self.db.add(file_asset)
    self.db.commit()
    self.db.refresh(file_asset)
    return file_asset

  def delete_file(self, file_asset: FileAsset) -> None:
    self.db.delete(file_asset)
    self.db.commit()
