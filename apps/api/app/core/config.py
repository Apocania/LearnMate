from functools import lru_cache

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

  cors_origins_raw: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

  minio_endpoint: str = "http://localhost:9000"
  minio_access_key: str = "minioadmin"
  minio_secret_key: str = "minioadmin"
  minio_bucket: str = "learnmate-materials"

  llm_provider: str = "openai-compatible"
  llm_api_key: str = ""
  llm_base_url: str = ""
  llm_model: str = ""

  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

  @property
  def cors_origins(self) -> list[str]:
    return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
  return Settings()


settings = get_settings()
