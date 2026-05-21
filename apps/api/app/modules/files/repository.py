from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.files.models import FileAsset


class FileRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def list_files(self, course_id: int | None = None, chapter_id: int | None = None) -> list[FileAsset]:
    statement = select(FileAsset)
    if course_id is not None:
      statement = statement.where(FileAsset.course_id == course_id)
    if chapter_id is not None:
      statement = statement.where(FileAsset.chapter_id == chapter_id)
    return list(self.db.scalars(statement.order_by(FileAsset.id.desc())).all())

  def get_file(self, file_id: int) -> FileAsset | None:
    return self.db.get(FileAsset, file_id)

  def create_file(
    self,
    original_name: str,
    stored_name: str,
    content_type: str,
    size: int,
    course_id: int | None,
    chapter_id: int | None,
    storage_provider: str,
    object_key: str,
    public_url: str | None,
    uploader_id: int,
    uploader_name: str,
  ) -> FileAsset:
    file_asset = FileAsset(
      original_name=original_name,
      stored_name=stored_name,
      content_type=content_type,
      size=size,
      course_id=course_id,
      chapter_id=chapter_id,
      storage_provider=storage_provider,
      object_key=object_key,
      public_url=public_url,
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
