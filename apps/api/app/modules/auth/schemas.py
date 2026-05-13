from typing import Literal

from pydantic import BaseModel, Field


UserRole = Literal["student", "mentor"]


class UserResponse(BaseModel):
  id: int
  username: str
  role: UserRole
  avatar_url: str | None = None

  model_config = {"from_attributes": True}


class RegisterRequest(BaseModel):
  username: str = Field(min_length=3, max_length=32)
  password: str = Field(min_length=6, max_length=128)
  role: UserRole


class LoginRequest(BaseModel):
  username: str = Field(min_length=3, max_length=32)
  password: str = Field(min_length=6, max_length=128)


class LoginResponse(BaseModel):
  access_token: str
  token_type: str
  user: UserResponse
