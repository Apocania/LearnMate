from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  app_name: str = "LearnMate API"
  app_version: str = "0.1.0"
  app_env: str = "development"

  database_url: str = "postgresql+psycopg://learnmate:learnmate@localhost:5432/learnmate"
  redis_url: str = "redis://localhost:6379/0"

  jwt_secret: str = Field(default="change-me-in-production")
  jwt_expire_minutes: int = 60 * 24 * 7

  cors_origins_raw: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", alias="CORS_ORIGINS")

  minio_endpoint: str = "http://localhost:9000"
  minio_access_key: str = "minioadmin"
  minio_secret_key: str = "minioadmin"
  minio_bucket: str = "learnmate-materials"
  storage_backend: str = "local"
  upload_max_size_mb: int = 200
  upload_allowed_types_raw: str = Field(
    default=(
      "application/pdf,image/png,image/jpeg,image/webp,text/plain,text/markdown,text/csv,application/csv,"
      "application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,"
      "application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation,"
      "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,"
      "application/zip,application/x-zip-compressed,video/mp4"
    ),
    alias="UPLOAD_ALLOWED_TYPES",
  )
  upload_allowed_extensions_raw: str = Field(
    default=".pdf,.png,.jpg,.jpeg,.webp,.txt,.md,.csv,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.zip,.mp4",
    alias="UPLOAD_ALLOWED_EXTENSIONS",
  )

  llm_provider: str = "openai-compatible"
  llm_api_key: str = ""
  llm_base_url: str = ""
  llm_model: str = ""

  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

  @property
  def cors_origins(self) -> list[str]:
    return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

  @property
  def upload_max_size_bytes(self) -> int:
    return self.upload_max_size_mb * 1024 * 1024

  @property
  def upload_allowed_types(self) -> set[str]:
    return {
      content_type.strip().lower()
      for content_type in self.upload_allowed_types_raw.split(",")
      if content_type.strip()
    }

  @property
  def upload_allowed_extensions(self) -> set[str]:
    extensions: set[str] = set()
    for extension in self.upload_allowed_extensions_raw.split(","):
      normalized = extension.strip().lower()
      if not normalized:
        continue
      extensions.add(normalized if normalized.startswith(".") else f".{normalized}")
    return extensions

  def normalize_upload_content_type(self, content_type: str | None) -> str:
    normalized = (content_type or "application/octet-stream").split(";", 1)[0].strip().lower()
    return normalized or "application/octet-stream"

  def is_upload_allowed(self, file_name: str, content_type: str | None) -> bool:
    normalized_type = self.normalize_upload_content_type(content_type)
    suffix = Path(file_name).suffix.lower()
    return normalized_type in self.upload_allowed_types or suffix in self.upload_allowed_extensions


@lru_cache
def get_settings() -> Settings:
  return Settings()


settings = get_settings()
