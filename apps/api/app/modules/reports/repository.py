from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.courses.models import Course, CourseEnrollment
from app.modules.forum.models import ForumComment, ForumPost
from app.modules.assistant.models import AssistantMessage
from app.modules.files.models import FileAsset
from app.modules.learning_records.models import LearningEvent


class LearningReportRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def count_enrolled_courses(self, user_id: int) -> int:
    return self.db.scalar(
      select(func.count()).select_from(CourseEnrollment).where(CourseEnrollment.student_id == user_id)
    ) or 0

  def count_created_courses(self, user_id: int) -> int:
    return self.db.scalar(select(func.count()).select_from(Course).where(Course.teacher_id == user_id)) or 0

  def count_forum_posts(self, user_id: int) -> int:
    return self.db.scalar(select(func.count()).select_from(ForumPost).where(ForumPost.author_id == user_id)) or 0

  def count_forum_comments(self, user_id: int) -> int:
    return self.db.scalar(select(func.count()).select_from(ForumComment).where(ForumComment.author_id == user_id)) or 0

  def count_ai_questions(self, user_id: int) -> int:
    return (
      self.db.scalar(
        select(func.count())
        .select_from(AssistantMessage)
        .where(AssistantMessage.user_id == user_id, AssistantMessage.role == "user")
      )
      or 0
    )

  def count_uploaded_files(self, user_id: int) -> int:
    return self.db.scalar(select(func.count()).select_from(FileAsset).where(FileAsset.uploader_id == user_id)) or 0

  def count_learning_events(self, user_id: int) -> int:
    return self.db.scalar(select(func.count()).select_from(LearningEvent).where(LearningEvent.user_id == user_id)) or 0

  def list_recent_course_titles(self, user_id: int, limit: int = 3) -> list[str]:
    course_ids = list(
      self.db.scalars(
        select(CourseEnrollment.course_id)
        .where(CourseEnrollment.student_id == user_id)
        .order_by(CourseEnrollment.id.desc())
        .limit(limit)
      ).all()
    )
    if not course_ids:
      return []

    courses = self.db.scalars(select(Course).where(Course.id.in_(course_ids))).all()
    title_by_id = {course.id: course.title for course in courses}
    return [title_by_id[course_id] for course_id in course_ids if course_id in title_by_id]

  def list_recent_created_course_titles(self, user_id: int, limit: int = 3) -> list[str]:
    return list(
      self.db.scalars(
        select(Course.title).where(Course.teacher_id == user_id).order_by(Course.id.desc()).limit(limit)
      ).all()
    )

  def list_recent_events(self, user_id: int, limit: int = 5) -> list[LearningEvent]:
    return list(
      self.db.scalars(
        select(LearningEvent)
        .where(LearningEvent.user_id == user_id)
        .order_by(LearningEvent.created_at.desc(), LearningEvent.id.desc())
        .limit(limit)
      ).all()
    )
