from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.init_db import init_db
from app.modules.assistant.api import router as assistant_router
from app.modules.auth.api import router as auth_router
from app.modules.courses.api import router as courses_router
from app.modules.files.api import router as files_router
from app.modules.forum.api import router as forum_router
from app.modules.learning_records.api import router as learning_records_router
from app.modules.messages.api import router as messages_router
from app.modules.reports.api import router as reports_router
from app.modules.users.api import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
  if settings.app_env != "test":
    init_db()
  yield


def create_app() -> FastAPI:
  app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
  avatar_static_dir = Path(__file__).resolve().parents[1] / "storage" / "avatars"
  avatar_static_dir.mkdir(parents=True, exist_ok=True)

  app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )

  @app.get("/api/health", tags=["system"])
  def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}

  app.mount("/static/avatars", StaticFiles(directory=avatar_static_dir), name="avatars")

  app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
  app.include_router(users_router, prefix="/api/users", tags=["users"])
  app.include_router(courses_router, prefix="/api/courses", tags=["courses"])
  app.include_router(forum_router, prefix="/api/forum", tags=["forum"])
  app.include_router(files_router, prefix="/api/files", tags=["files"])
  app.include_router(assistant_router, prefix="/api/assistant", tags=["assistant"])
  app.include_router(learning_records_router, prefix="/api/learning-records", tags=["learning-records"])
  app.include_router(messages_router, prefix="/api/messages", tags=["messages"])
  app.include_router(reports_router, prefix="/api/reports", tags=["reports"])

  return app


app = create_app()
