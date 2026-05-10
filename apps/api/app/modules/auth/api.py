from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.schemas import LoginRequest, LoginResponse, RegisterRequest
from app.modules.auth.service import AuthService

router = APIRouter()


@router.post("/register", response_model=LoginResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> LoginResponse:
  return AuthService(db).register(payload.username, payload.password, payload.role)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
  return AuthService(db).login(payload.username, payload.password)
