"""initial schema

Revision ID: 20260520_0001
Revises:
Create Date: 2026-05-20
"""
from alembic import op
import sqlalchemy as sa

revision = "20260520_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    "users",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("username", sa.String(), nullable=False),
    sa.Column("password_hash", sa.String(), nullable=False),
    sa.Column("role", sa.String(), nullable=False),
    sa.Column("avatar_url", sa.String(), nullable=True),
  )
  op.create_index("ix_users_id", "users", ["id"])
  op.create_index("ix_users_username", "users", ["username"], unique=True)

  op.create_table(
    "courses",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("title", sa.String(), nullable=False),
    sa.Column("description", sa.Text(), nullable=False),
    sa.Column("teacher_id", sa.Integer(), nullable=False),
    sa.Column("teacher_name", sa.String(), nullable=False),
    sa.Column("status", sa.String(), nullable=False, server_default="published"),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
  )
  op.create_index("ix_courses_id", "courses", ["id"])
  op.create_index("ix_courses_title", "courses", ["title"])
  op.create_index("ix_courses_teacher_id", "courses", ["teacher_id"])

  op.create_table(
    "course_enrollments",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
    sa.Column("student_id", sa.Integer(), nullable=False),
    sa.Column("student_name", sa.String(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.UniqueConstraint("course_id", "student_id", name="uq_course_enrollment_course_student"),
  )
  op.create_index("ix_course_enrollments_course_id", "course_enrollments", ["course_id"])
  op.create_index("ix_course_enrollments_student_id", "course_enrollments", ["student_id"])

  op.create_table(
    "course_chapters",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
    sa.Column("title", sa.String(), nullable=False),
    sa.Column("description", sa.Text(), nullable=False, server_default=""),
    sa.Column("sort_order", sa.Integer(), nullable=False, server_default="1"),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.UniqueConstraint("course_id", "sort_order", name="uq_course_chapter_course_sort"),
  )
  op.create_index("ix_course_chapters_course_id", "course_chapters", ["course_id"])
  op.create_index("ix_course_chapters_title", "course_chapters", ["title"])

  op.create_table(
    "file_assets",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("original_name", sa.String(), nullable=False),
    sa.Column("stored_name", sa.String(), nullable=False),
    sa.Column("content_type", sa.String(), nullable=False),
    sa.Column("size", sa.Integer(), nullable=False),
    sa.Column("course_id", sa.Integer(), nullable=True),
    sa.Column("chapter_id", sa.Integer(), nullable=True),
    sa.Column("storage_provider", sa.String(), nullable=False, server_default="local"),
    sa.Column("object_key", sa.String(), nullable=False),
    sa.Column("public_url", sa.String(), nullable=True),
    sa.Column("uploader_id", sa.Integer(), nullable=False),
    sa.Column("uploader_name", sa.String(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
  )
  op.create_index("ix_file_assets_id", "file_assets", ["id"])
  op.create_index("ix_file_assets_course_id", "file_assets", ["course_id"])
  op.create_index("ix_file_assets_chapter_id", "file_assets", ["chapter_id"])
  op.create_index("ix_file_assets_uploader_id", "file_assets", ["uploader_id"])

  op.create_table(
    "forum_posts",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("title", sa.String(), nullable=False),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("attachments", sa.Text(), nullable=False, server_default="[]"),
    sa.Column("author_id", sa.Integer(), nullable=False),
    sa.Column("author_name", sa.String(), nullable=False),
    sa.Column("course_id", sa.Integer(), nullable=True),
    sa.Column("status", sa.String(), nullable=False, server_default="active"),
    sa.Column("reviewed_by", sa.Integer(), nullable=True),
    sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
  )
  op.create_index("ix_forum_posts_id", "forum_posts", ["id"])
  op.create_index("ix_forum_posts_title", "forum_posts", ["title"])
  op.create_index("ix_forum_posts_author_id", "forum_posts", ["author_id"])
  op.create_index("ix_forum_posts_course_id", "forum_posts", ["course_id"])
  op.create_index("ix_forum_posts_status", "forum_posts", ["status"])

  op.create_table(
    "forum_comments",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("post_id", sa.Integer(), sa.ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=False),
    sa.Column("author_id", sa.Integer(), nullable=False),
    sa.Column("author_name", sa.String(), nullable=False),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
  )
  op.create_index("ix_forum_comments_id", "forum_comments", ["id"])
  op.create_index("ix_forum_comments_post_id", "forum_comments", ["post_id"])
  op.create_index("ix_forum_comments_author_id", "forum_comments", ["author_id"])

  op.create_table(
    "forum_likes",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("post_id", sa.Integer(), sa.ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=False),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.UniqueConstraint("post_id", "user_id", name="uq_forum_like_post_user"),
  )
  op.create_index("ix_forum_likes_id", "forum_likes", ["id"])
  op.create_index("ix_forum_likes_post_id", "forum_likes", ["post_id"])
  op.create_index("ix_forum_likes_user_id", "forum_likes", ["user_id"])

  op.create_table(
    "learning_events",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("course_id", sa.Integer(), nullable=True),
    sa.Column("event_type", sa.String(), nullable=False),
    sa.Column("event_payload", sa.Text(), nullable=False, server_default="{}"),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
  )
  op.create_index("ix_learning_events_id", "learning_events", ["id"])
  op.create_index("ix_learning_events_user_id", "learning_events", ["user_id"])
  op.create_index("ix_learning_events_course_id", "learning_events", ["course_id"])
  op.create_index("ix_learning_events_event_type", "learning_events", ["event_type"])

  op.create_table(
    "learning_reports",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("course_id", sa.Integer(), nullable=True),
    sa.Column("summary", sa.String(), nullable=False),
  )
  op.create_index("ix_learning_reports_id", "learning_reports", ["id"])

  op.create_table(
    "assistant_sessions",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("course_id", sa.Integer(), nullable=True),
    sa.Column("title", sa.String(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
  )
  op.create_index("ix_assistant_sessions_id", "assistant_sessions", ["id"])
  op.create_index("ix_assistant_sessions_user_id", "assistant_sessions", ["user_id"])
  op.create_index("ix_assistant_sessions_course_id", "assistant_sessions", ["course_id"])

  op.create_table(
    "assistant_messages",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("session_id", sa.Integer(), sa.ForeignKey("assistant_sessions.id", ondelete="SET NULL"), nullable=True),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("course_id", sa.Integer(), nullable=True),
    sa.Column("role", sa.String(), nullable=False),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("citations", sa.Text(), nullable=False, server_default="[]"),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
  )
  op.create_index("ix_assistant_messages_id", "assistant_messages", ["id"])
  op.create_index("ix_assistant_messages_session_id", "assistant_messages", ["session_id"])
  op.create_index("ix_assistant_messages_user_id", "assistant_messages", ["user_id"])
  op.create_index("ix_assistant_messages_course_id", "assistant_messages", ["course_id"])
  op.create_index("ix_assistant_messages_role", "assistant_messages", ["role"])

  op.create_table(
    "knowledge_chunks",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("file_asset_id", sa.Integer(), sa.ForeignKey("file_assets.id", ondelete="CASCADE"), nullable=True),
    sa.Column("course_id", sa.Integer(), nullable=True),
    sa.Column("chapter_id", sa.Integer(), nullable=True),
    sa.Column("document_id", sa.String(), nullable=False),
    sa.Column("title", sa.String(), nullable=False),
    sa.Column("chunk_index", sa.Integer(), nullable=False),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("keywords", sa.Text(), nullable=False, server_default=""),
    sa.Column("embedding", sa.Text(), nullable=False, server_default="[]"),
    sa.Column("source_url", sa.String(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
  )
  op.create_index("ix_knowledge_chunks_id", "knowledge_chunks", ["id"])
  op.create_index("ix_knowledge_chunks_file_asset_id", "knowledge_chunks", ["file_asset_id"])
  op.create_index("ix_knowledge_chunks_course_id", "knowledge_chunks", ["course_id"])
  op.create_index("ix_knowledge_chunks_chapter_id", "knowledge_chunks", ["chapter_id"])
  op.create_index("ix_knowledge_chunks_document_id", "knowledge_chunks", ["document_id"])

  op.create_table(
    "user_messages",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("recipient_id", sa.Integer(), nullable=False),
    sa.Column("recipient_name", sa.String(), nullable=False),
    sa.Column("sender_id", sa.Integer(), nullable=True),
    sa.Column("sender_name", sa.String(), nullable=True),
    sa.Column("message_type", sa.String(), nullable=False),
    sa.Column("title", sa.String(), nullable=False),
    sa.Column("content", sa.Text(), nullable=False),
    sa.Column("source_type", sa.String(), nullable=True),
    sa.Column("source_id", sa.Integer(), nullable=True),
    sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
  )
  op.create_index("ix_user_messages_id", "user_messages", ["id"])
  op.create_index("ix_user_messages_recipient_id", "user_messages", ["recipient_id"])
  op.create_index("ix_user_messages_sender_id", "user_messages", ["sender_id"])
  op.create_index("ix_user_messages_message_type", "user_messages", ["message_type"])
  op.create_index("ix_user_messages_source_type", "user_messages", ["source_type"])
  op.create_index("ix_user_messages_source_id", "user_messages", ["source_id"])


def downgrade() -> None:
  for table in [
    "user_messages",
    "knowledge_chunks",
    "assistant_messages",
    "assistant_sessions",
    "learning_reports",
    "learning_events",
    "forum_likes",
    "forum_comments",
    "forum_posts",
    "file_assets",
    "course_chapters",
    "course_enrollments",
    "courses",
    "users",
  ]:
    op.drop_table(table)
