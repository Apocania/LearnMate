from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.modules.auth.models import User
from app.modules.auth.repository import AuthRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
  credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
  db: Session = Depends(get_db),
) -> User:
  if credentials is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="未登录",
    )

  payload = decode_access_token(credentials.credentials)
  if payload is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="登录状态已失效",
    )

  subject = payload.get("sub")
  if not isinstance(subject, str) or not subject.isdigit():
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="登录状态无效",
    )

  user = AuthRepository(db).get_by_id(int(subject))
  if user is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="用户不存在",
    )

  return user


def get_optional_current_user(
  credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
  db: Session = Depends(get_db),
) -> User | None:
  if credentials is None:
    return None
  return get_current_user(credentials, db)


def require_roles(current_user: User, allowed_roles: set[str]) -> User:
  if current_user.role not in allowed_roles:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="当前身份没有权限执行此操作",
    )
  return current_user
