from app.core.database import Base, engine
from app.modules.assistant import models as assistant_models  # noqa: F401
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.courses import models as course_models  # noqa: F401
from app.modules.files import models as file_models  # noqa: F401
from app.modules.forum import models as forum_models  # noqa: F401
from app.modules.learning_records import models as learning_record_models  # noqa: F401
from app.modules.messages import models as message_models  # noqa: F401
from app.modules.reports import models as report_models  # noqa: F401


def init_db() -> None:
  Base.metadata.create_all(bind=engine)
  _ensure_development_columns()


def _ensure_development_columns() -> None:
  statements = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR",
    "ALTER TABLE courses ADD COLUMN IF NOT EXISTS teacher_name VARCHAR NOT NULL DEFAULT 'unknown'",
    "ALTER TABLE courses ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT now()",
    "ALTER TABLE courses ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()",
    "CREATE TABLE IF NOT EXISTS course_enrollments (id SERIAL PRIMARY KEY, course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE, student_id INTEGER NOT NULL, student_name VARCHAR NOT NULL, created_at TIMESTAMP WITH TIME ZONE DEFAULT now())",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_course_enrollment_course_student ON course_enrollments (course_id, student_id)",
    "CREATE INDEX IF NOT EXISTS ix_course_enrollments_course_id ON course_enrollments (course_id)",
    "CREATE INDEX IF NOT EXISTS ix_course_enrollments_student_id ON course_enrollments (student_id)",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS author_name VARCHAR NOT NULL DEFAULT 'unknown'",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS course_id INTEGER",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT now()",
    "CREATE TABLE IF NOT EXISTS user_messages (id SERIAL PRIMARY KEY, recipient_id INTEGER NOT NULL, recipient_name VARCHAR NOT NULL, sender_id INTEGER, sender_name VARCHAR, message_type VARCHAR NOT NULL, title VARCHAR NOT NULL, content TEXT NOT NULL, source_type VARCHAR, source_id INTEGER, is_read BOOLEAN NOT NULL DEFAULT false, created_at TIMESTAMP WITH TIME ZONE DEFAULT now())",
    "CREATE INDEX IF NOT EXISTS ix_user_messages_recipient_id ON user_messages (recipient_id)",
    "CREATE INDEX IF NOT EXISTS ix_user_messages_sender_id ON user_messages (sender_id)",
    "CREATE INDEX IF NOT EXISTS ix_user_messages_message_type ON user_messages (message_type)",
    "CREATE INDEX IF NOT EXISTS ix_user_messages_source_type ON user_messages (source_type)",
    "CREATE INDEX IF NOT EXISTS ix_user_messages_source_id ON user_messages (source_id)",
  ]

  with engine.begin() as connection:
    for statement in statements:
      connection.exec_driver_sql(statement)
