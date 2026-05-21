from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_roles
from app.modules.auth.models import User
from app.modules.files.schemas import FileAssetResponse
from app.modules.files.service import FileService

router = APIRouter()


@router.get("", response_model=list[FileAssetResponse])
def list_files(
  course_id: int | None = None,
  chapter_id: int | None = None,
  db: Session = Depends(get_db),
) -> list[FileAssetResponse]:
  return FileService(db).list_files(course_id, chapter_id)


@router.post("/upload", response_model=FileAssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
  file: UploadFile,
  course_id: int | None = Form(None),
  chapter_id: int | None = Form(None),
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> FileAssetResponse:
  require_roles(current_user, {"mentor"})
  return await FileService(db).upload_file(file, current_user, course_id=course_id, chapter_id=chapter_id)


@router.get("/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db)) -> FileResponse:
  service = FileService(db)
  file_asset = service.get_file(file_id)
  if file_asset.storage_provider == "local":
    _, path = service.get_file_path(file_id)
    return FileResponse(
      path,
      media_type=file_asset.content_type,
      filename=quote(file_asset.original_name),
    )
  _, data = service.get_file_bytes(file_id)
  return Response(
    content=data,
    media_type=file_asset.content_type,
    headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(file_asset.original_name)}"},
  )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
  file_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> Response:
  FileService(db).delete_file(file_id, current_user)
  return Response(status_code=status.HTTP_204_NO_CONTENT)
