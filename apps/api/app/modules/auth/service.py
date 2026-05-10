from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import LoginResponse, UserRole


class AuthService:
  def __init__(self, db: Session) -> None:
    self.repository = AuthRepository(db)

  def register(self, username: str, password: str, role: UserRole) -> LoginResponse:
    existing_user = self.repository.get_by_username(username)
    if existing_user:
      raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="用户名已存在",
      )

    user = self.repository.create_user(
      username=username,
      password_hash=get_password_hash(password),
      role=role,
    )
    token = create_access_token(str(user.id), settings.jwt_expire_minutes)
    return LoginResponse(access_token=token, token_type="bearer", user=user)

  def login(self, username: str, password: str) -> LoginResponse:
    user = self.repository.get_by_username(username)
    if not user or not verify_password(password, user.password_hash):
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户名或密码错误",
      )

    token = create_access_token(str(user.id), settings.jwt_expire_minutes)
    return LoginResponse(access_token=token, token_type="bearer", user=user)
