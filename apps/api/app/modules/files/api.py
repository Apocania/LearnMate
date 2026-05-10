from urllib.parse import quote

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.files.schemas import FileAssetResponse
from app.modules.files.service import FileService

router = APIRouter()


@router.get("", response_model=list[FileAssetResponse])
def list_files(db: Session = Depends(get_db)) -> list[FileAssetResponse]:
  return FileService(db).list_files()


@router.post("/upload", response_model=FileAssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
  file: UploadFile,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> FileAssetResponse:
  return await FileService(db).upload_file(file, current_user)


@router.get("/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db)) -> FileResponse:
  file_asset, path = FileService(db).get_file_path(file_id)
  return FileResponse(
    path,
    media_type=file_asset.content_type,
    filename=quote(file_asset.original_name),
  )

