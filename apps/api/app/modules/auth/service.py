import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import LoginResponse, UserRole

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


class AuthService:
  def __init__(self, db: Session) -> None:
    self.repository = AuthRepository(db)

  def register(self, username: str, password: str, role: UserRole) -> LoginResponse:
    normalized_username = username.strip().lower()
    if not USERNAME_PATTERN.fullmatch(normalized_username):
      raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="用户名只能包含英文字母、数字和下划线，长度为 3-32 位",
      )

    existing_user = self.repository.get_by_username(normalized_username)
    if existing_user:
      raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="用户名已存在",
      )

    user = self.repository.create_user(
      username=normalized_username,
      password_hash=get_password_hash(password),
      role=role,
    )
    token = create_access_token(str(user.id), settings.jwt_expire_minutes)
    return LoginResponse(access_token=token, token_type="bearer", user=user)

  def login(self, username: str, password: str) -> LoginResponse:
    user = self.repository.get_by_username(username.strip().lower())
    if not user or not verify_password(password, user.password_hash):
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户名或密码错误",
      )

    token = create_access_token(str(user.id), settings.jwt_expire_minutes)
    return LoginResponse(access_token=token, token_type="bearer", user=user)
