from fastapi import APIRouter, Depends, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.schemas import UserResponse
from app.modules.users.service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
  return current_user


@router.get("/avatars/{stored_name}")
def get_avatar(stored_name: str, db: Session = Depends(get_db)) -> Response:
  data, content_type = UserService(db).get_avatar(stored_name)
  return Response(content=data, media_type=content_type)


@router.post("/me/avatar", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def upload_my_avatar(
  file: UploadFile,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> User:
  return await UserService(db).update_avatar(file, current_user)
