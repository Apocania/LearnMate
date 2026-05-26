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
    "CREATE TABLE IF NOT EXISTS course_chapters (id SERIAL PRIMARY KEY, course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE, title VARCHAR NOT NULL, description TEXT NOT NULL DEFAULT '', sort_order INTEGER NOT NULL DEFAULT 1, created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), updated_at TIMESTAMP WITH TIME ZONE DEFAULT now())",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_course_chapter_course_sort ON course_chapters (course_id, sort_order)",
    "CREATE INDEX IF NOT EXISTS ix_course_chapters_course_id ON course_chapters (course_id)",
    "CREATE INDEX IF NOT EXISTS ix_course_chapters_title ON course_chapters (title)",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS author_name VARCHAR NOT NULL DEFAULT 'unknown'",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS course_id INTEGER",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS attachments TEXT NOT NULL DEFAULT '[]'",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS status VARCHAR NOT NULL DEFAULT 'active'",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS reviewed_by INTEGER",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP WITH TIME ZONE",
    "ALTER TABLE forum_posts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT now()",
    "CREATE INDEX IF NOT EXISTS ix_forum_posts_status ON forum_posts (status)",
    "CREATE INDEX IF NOT EXISTS ix_forum_posts_reviewed_by ON forum_posts (reviewed_by)",
    "ALTER TABLE file_assets ADD COLUMN IF NOT EXISTS course_id INTEGER",
    "ALTER TABLE file_assets ADD COLUMN IF NOT EXISTS chapter_id INTEGER",
    "ALTER TABLE file_assets ADD COLUMN IF NOT EXISTS storage_provider VARCHAR NOT NULL DEFAULT 'local'",
    "ALTER TABLE file_assets ADD COLUMN IF NOT EXISTS object_key VARCHAR",
    "UPDATE file_assets SET object_key = stored_name WHERE object_key IS NULL",
    "ALTER TABLE file_assets ALTER COLUMN object_key SET NOT NULL",
    "ALTER TABLE file_assets ADD COLUMN IF NOT EXISTS public_url VARCHAR",
    "CREATE INDEX IF NOT EXISTS ix_file_assets_course_id ON file_assets (course_id)",
    "CREATE INDEX IF NOT EXISTS ix_file_assets_chapter_id ON file_assets (chapter_id)",
    "ALTER TABLE learning_events ADD COLUMN IF NOT EXISTS event_payload TEXT NOT NULL DEFAULT '{}'",
    "ALTER TABLE learning_events ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT now()",
    "CREATE INDEX IF NOT EXISTS ix_learning_events_user_id ON learning_events (user_id)",
    "CREATE INDEX IF NOT EXISTS ix_learning_events_course_id ON learning_events (course_id)",
    "CREATE INDEX IF NOT EXISTS ix_learning_events_event_type ON learning_events (event_type)",
    "CREATE TABLE IF NOT EXISTS course_learning_progress (id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL, progress_percent INTEGER NOT NULL DEFAULT 0, study_seconds INTEGER NOT NULL DEFAULT 0, last_position VARCHAR NOT NULL DEFAULT '', created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), updated_at TIMESTAMP WITH TIME ZONE DEFAULT now())",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_course_learning_progress_user_course ON course_learning_progress (user_id, course_id)",
    "CREATE INDEX IF NOT EXISTS ix_course_learning_progress_user_id ON course_learning_progress (user_id)",
    "CREATE INDEX IF NOT EXISTS ix_course_learning_progress_course_id ON course_learning_progress (course_id)",
    "CREATE TABLE IF NOT EXISTS user_messages (id SERIAL PRIMARY KEY, recipient_id INTEGER NOT NULL, recipient_name VARCHAR NOT NULL, sender_id INTEGER, sender_name VARCHAR, message_type VARCHAR NOT NULL, title VARCHAR NOT NULL, content TEXT NOT NULL, source_type VARCHAR, source_id INTEGER, is_read BOOLEAN NOT NULL DEFAULT false, created_at TIMESTAMP WITH TIME ZONE DEFAULT now())",
    "CREATE INDEX IF NOT EXISTS ix_user_messages_recipient_id ON user_messages (recipient_id)",
    "CREATE INDEX IF NOT EXISTS ix_user_messages_sender_id ON user_messages (sender_id)",
    "CREATE INDEX IF NOT EXISTS ix_user_messages_message_type ON user_messages (message_type)",
    "CREATE INDEX IF NOT EXISTS ix_user_messages_source_type ON user_messages (source_type)",
    "CREATE INDEX IF NOT EXISTS ix_user_messages_source_id ON user_messages (source_id)",
    "ALTER TABLE assistant_sessions ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT now()",
    "ALTER TABLE assistant_sessions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()",
    "CREATE INDEX IF NOT EXISTS ix_assistant_sessions_user_id ON assistant_sessions (user_id)",
    "CREATE INDEX IF NOT EXISTS ix_assistant_sessions_course_id ON assistant_sessions (course_id)",
    "CREATE TABLE IF NOT EXISTS assistant_messages (id SERIAL PRIMARY KEY, session_id INTEGER REFERENCES assistant_sessions(id) ON DELETE SET NULL, user_id INTEGER NOT NULL, course_id INTEGER, role VARCHAR NOT NULL, content TEXT NOT NULL, citations TEXT NOT NULL DEFAULT '[]', created_at TIMESTAMP WITH TIME ZONE DEFAULT now())",
    "CREATE INDEX IF NOT EXISTS ix_assistant_messages_session_id ON assistant_messages (session_id)",
    "CREATE INDEX IF NOT EXISTS ix_assistant_messages_user_id ON assistant_messages (user_id)",
    "CREATE INDEX IF NOT EXISTS ix_assistant_messages_course_id ON assistant_messages (course_id)",
    "CREATE INDEX IF NOT EXISTS ix_assistant_messages_role ON assistant_messages (role)",
    "CREATE TABLE IF NOT EXISTS knowledge_chunks (id SERIAL PRIMARY KEY, file_asset_id INTEGER REFERENCES file_assets(id) ON DELETE CASCADE, course_id INTEGER, chapter_id INTEGER, document_id VARCHAR NOT NULL, title VARCHAR NOT NULL, chunk_index INTEGER NOT NULL, content TEXT NOT NULL, keywords TEXT NOT NULL DEFAULT '', source_url VARCHAR, created_at TIMESTAMP WITH TIME ZONE DEFAULT now())",
    "ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS embedding TEXT NOT NULL DEFAULT '[]'",
    "CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_file_asset_id ON knowledge_chunks (file_asset_id)",
    "CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_course_id ON knowledge_chunks (course_id)",
    "CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_chapter_id ON knowledge_chunks (chapter_id)",
    "CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_document_id ON knowledge_chunks (document_id)",
  ]

  with engine.begin() as connection:
    for statement in statements:
      connection.exec_driver_sql(statement)
