from app.core.database import Base, engine
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.courses import models as course_models  # noqa: F401
from app.modules.files import models as file_models  # noqa: F401
from app.modules.forum import models as forum_models  # noqa: F401


def init_db() -> None:
  Base.metadata.create_all(bind=engine)
  _ensure_development_columns()


def _ensure_development_columns() -> None:
  statements = [
    "ALTER TABLE courses ADD COLUMN IF NOT EXISTS teacher_name VARCHAR NOT NULL DEFAULT 'unknown'",
    "ALTER TABLE courses ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT now()",
    "ALTER TABLE courses ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS author_name VARCHAR NOT NULL DEFAULT 'unknown'",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS course_id INTEGER",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT now()",
  ]

  with engine.begin() as connection:
    for statement in statements:
      connection.exec_driver_sql(statement)
