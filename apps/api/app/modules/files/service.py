from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infrastructure.object_storage import ObjectStorageClient
from app.modules.assistant.knowledge_ingestion import KnowledgeIngestionService
from app.modules.auth.models import User
from app.modules.courses.repository import CourseRepository
from app.modules.files.models import FileAsset
from app.modules.files.repository import FileRepository
from app.modules.files.schemas import FileAssetResponse
from app.modules.learning_records.service import LearningRecordService

UPLOAD_DIR = Path(__file__).resolve().parents[3] / "storage" / "uploads"


class FileService:
  def __init__(self, db: Session) -> None:
    self.db = db
    self.repository = FileRepository(db)
    self.course_repository = CourseRepository(db)
    self.storage = ObjectStorageClient()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

  def list_files(
    self,
    course_id: int | None = None,
    chapter_id: int | None = None,
    current_user: User | None = None,
  ) -> list[FileAssetResponse]:
    file_assets = self.repository.list_files(course_id, chapter_id)
    visible_files = [file_asset for file_asset in file_assets if self._is_file_visible(file_asset, current_user)]
    return [self._to_response(file_asset) for file_asset in visible_files]

  async def upload_file(
    self,
    upload: UploadFile,
    current_user: User,
    course_id: int | None = None,
    chapter_id: int | None = None,
  ) -> FileAssetResponse:
    self._ensure_course_context(course_id, chapter_id, current_user)
    original_name = upload.filename or "unnamed-file"
    content_type = upload.content_type or "application/octet-stream"
    if content_type not in settings.upload_allowed_types:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的文件类型")

    suffix = Path(original_name).suffix
    stored_name = f"{uuid4().hex}{suffix}"

    content = await upload.read()
    if len(content) > settings.upload_max_size_bytes:
      raise HTTPException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail=f"文件不能超过 {settings.upload_max_size_mb}MB",
      )

    stored_object = self.storage.put_object(stored_name, content, content_type)

    file_asset = self.repository.create_file(
      original_name=original_name,
      stored_name=stored_name,
      content_type=content_type,
      size=len(content),
      course_id=course_id,
      chapter_id=chapter_id,
      storage_provider=stored_object.provider,
      object_key=stored_object.object_key,
      public_url=stored_object.public_url,
      uploader_id=current_user.id,
      uploader_name=current_user.username,
    )
    chunk_count = KnowledgeIngestionService(self.db).ingest_file(file_asset, content)
    LearningRecordService(self.db).record_event(
      current_user,
      "file_uploaded",
      course_id=course_id,
      metadata={"file_name": original_name, "chunk_count": str(chunk_count)},
    )
    return self._to_response(file_asset)

  def get_file(self, file_id: int, current_user: User | None = None) -> FileAsset:
    file_asset = self.repository.get_file(file_id)
    if file_asset is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
    if not self._is_file_visible(file_asset, current_user):
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
    return file_asset

  def get_file_path(self, file_id: int, current_user: User | None = None) -> tuple[FileAsset, Path]:
    file_asset = self.get_file(file_id, current_user)
    if file_asset.storage_provider != "local":
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前文件不在本地存储")
    path = self.storage.get_local_path(file_asset.object_key or file_asset.stored_name)
    return file_asset, path

  def get_file_bytes(self, file_id: int, current_user: User | None = None) -> tuple[FileAsset, bytes]:
    file_asset = self.get_file(file_id, current_user)
    data = self.storage.read_object(file_asset.object_key or file_asset.stored_name, file_asset.storage_provider)
    return file_asset, data

  def delete_file(self, file_id: int, current_user: User) -> None:
    file_asset = self.get_file(file_id, current_user)
    if current_user.role != "mentor":
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有伴学师可以删除课件")
    if file_asset.uploader_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能删除自己上传的课件")

    self.storage.delete_object(file_asset.object_key or file_asset.stored_name, file_asset.storage_provider)
    KnowledgeIngestionService(self.db).remove_file_chunks(file_asset.id)
    self.repository.delete_file(file_asset)

  def _ensure_course_context(self, course_id: int | None, chapter_id: int | None, current_user: User) -> None:
    if course_id is None and chapter_id is not None:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="章节资料必须绑定课程")
    if course_id is None:
      return

    course = self.course_repository.get_course(course_id)
    if course is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    if current_user.role != "mentor" or course.teacher_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能给自己创建的课程上传课件")
    if chapter_id is not None:
      chapter = self.course_repository.get_chapter(chapter_id)
      if chapter is None or chapter.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="章节不存在")

  def _is_file_visible(self, file_asset: FileAsset, current_user: User | None) -> bool:
    if file_asset.course_id is None:
      return True
    course = self.course_repository.get_course(file_asset.course_id)
    if course is None:
      return False
    if course.status == "published":
      return True
    return bool(current_user and current_user.role == "mentor" and course.teacher_id == current_user.id)

  def _to_response(self, file_asset: FileAsset) -> FileAssetResponse:
    return FileAssetResponse(
      id=file_asset.id,
      original_name=file_asset.original_name,
      stored_name=file_asset.stored_name,
      content_type=file_asset.content_type,
      size=file_asset.size,
      course_id=file_asset.course_id,
      chapter_id=file_asset.chapter_id,
      storage_provider=file_asset.storage_provider,
      public_url=file_asset.public_url,
      uploader_id=file_asset.uploader_id,
      uploader_name=file_asset.uploader_name,
      created_at=file_asset.created_at,
      url=f"/api/files/{file_asset.id}/download",
    )
