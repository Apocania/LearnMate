from fastapi import APIRouter

from app.core.config import settings
from app.core.security import create_access_token
from app.modules.auth.schemas import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
  token = create_access_token(payload.username, settings.jwt_expire_minutes)
  return LoginResponse(access_token=token, token_type="bearer")

