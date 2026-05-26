from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.courses.models import Course, CourseChapter, CourseEnrollment
from app.modules.forum.models import ForumComment, ForumPost
from app.modules.assistant.models import AssistantMessage
from app.modules.files.models import FileAsset
from app.modules.learning_records.models import CourseLearningProgress, LearningEvent


class LearningReportRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def count_enrolled_courses(self, user_id: int) -> int:
    return self.db.scalar(
      select(func.count()).select_from(CourseEnrollment).where(CourseEnrollment.student_id == user_id)
    ) or 0

  def count_created_courses(self, user_id: int) -> int:
    return self.db.scalar(select(func.count()).select_from(Course).where(Course.teacher_id == user_id)) or 0

  def count_students_for_teacher(self, user_id: int) -> int:
    return (
      self.db.scalar(
        select(func.count(func.distinct(CourseEnrollment.student_id)))
        .select_from(CourseEnrollment)
        .join(Course, Course.id == CourseEnrollment.course_id)
        .where(Course.teacher_id == user_id)
      )
      or 0
    )

  def count_chapters_for_teacher(self, user_id: int) -> int:
    return (
      self.db.scalar(
        select(func.count())
        .select_from(CourseChapter)
        .join(Course, Course.id == CourseChapter.course_id)
        .where(Course.teacher_id == user_id)
      )
      or 0
    )

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

  def sum_study_seconds(self, user_id: int) -> int:
    return (
      self.db.scalar(
        select(func.coalesce(func.sum(CourseLearningProgress.study_seconds), 0)).where(
          CourseLearningProgress.user_id == user_id
        )
      )
      or 0
    )

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

  def list_student_course_progress_summaries(self, user_id: int, limit: int = 3):
    enrollments = list(
      self.db.scalars(
        select(CourseEnrollment)
        .where(CourseEnrollment.student_id == user_id)
        .order_by(CourseEnrollment.created_at.desc(), CourseEnrollment.id.desc())
        .limit(limit)
      ).all()
    )
    if not enrollments:
      return []

    course_ids = [enrollment.course_id for enrollment in enrollments]
    courses = list(self.db.scalars(select(Course).where(Course.id.in_(course_ids))).all())
    chapter_rows = self.db.execute(
      select(CourseChapter.course_id, func.count())
      .where(CourseChapter.course_id.in_(course_ids))
      .group_by(CourseChapter.course_id)
    ).all()
    event_rows = self.db.execute(
      select(LearningEvent.course_id, func.count())
      .where(LearningEvent.user_id == user_id, LearningEvent.course_id.in_(course_ids))
      .group_by(LearningEvent.course_id)
    ).all()
    question_rows = self.db.execute(
      select(AssistantMessage.course_id, func.count())
      .where(
        AssistantMessage.user_id == user_id,
        AssistantMessage.role == "user",
        AssistantMessage.course_id.in_(course_ids),
      )
      .group_by(AssistantMessage.course_id)
    ).all()
    progress_rows = self.db.execute(
      select(CourseLearningProgress.course_id, CourseLearningProgress.progress_percent)
      .where(CourseLearningProgress.user_id == user_id, CourseLearningProgress.course_id.in_(course_ids))
    ).all()

    course_by_id = {course.id: course for course in courses}
    chapter_count_by_course = {course_id: count for course_id, count in chapter_rows}
    event_count_by_course = {course_id: count for course_id, count in event_rows}
    question_count_by_course = {course_id: count for course_id, count in question_rows}
    progress_by_course = {course_id: percent for course_id, percent in progress_rows}

    return [
      {
        "id": enrollment.course_id,
        "title": course_by_id[enrollment.course_id].title,
        "chapter_count": chapter_count_by_course.get(enrollment.course_id, 0),
        "event_count": event_count_by_course.get(enrollment.course_id, 0),
        "question_count": question_count_by_course.get(enrollment.course_id, 0),
        "progress_percent": progress_by_course.get(enrollment.course_id, 0),
      }
      for enrollment in enrollments
      if enrollment.course_id in course_by_id
    ]

  def list_recent_created_course_titles(self, user_id: int, limit: int = 3) -> list[str]:
    return list(
      self.db.scalars(
        select(Course.title).where(Course.teacher_id == user_id).order_by(Course.id.desc()).limit(limit)
      ).all()
    )

  def list_teaching_course_summaries(self, user_id: int, limit: int = 5):
    courses = list(
      self.db.scalars(select(Course).where(Course.teacher_id == user_id).order_by(Course.id.desc()).limit(limit)).all()
    )
    if not courses:
      return []

    course_ids = [course.id for course in courses]
    enrollment_rows = self.db.execute(
      select(CourseEnrollment.course_id, func.count())
      .where(CourseEnrollment.course_id.in_(course_ids))
      .group_by(CourseEnrollment.course_id)
    ).all()
    chapter_rows = self.db.execute(
      select(CourseChapter.course_id, func.count())
      .where(CourseChapter.course_id.in_(course_ids))
      .group_by(CourseChapter.course_id)
    ).all()
    file_rows = self.db.execute(
      select(FileAsset.course_id, func.count())
      .where(FileAsset.course_id.in_(course_ids))
      .group_by(FileAsset.course_id)
    ).all()

    enrollment_count_by_course = {course_id: count for course_id, count in enrollment_rows}
    chapter_count_by_course = {course_id: count for course_id, count in chapter_rows}
    file_count_by_course = {course_id: count for course_id, count in file_rows}

    return [
      {
        "id": course.id,
        "title": course.title,
        "status": course.status,
        "enrollment_count": enrollment_count_by_course.get(course.id, 0),
        "chapter_count": chapter_count_by_course.get(course.id, 0),
        "file_count": file_count_by_course.get(course.id, 0),
      }
      for course in courses
    ]

  def list_recent_events(self, user_id: int, limit: int = 5) -> list[LearningEvent]:
    return list(
      self.db.scalars(
        select(LearningEvent)
        .where(LearningEvent.user_id == user_id)
        .order_by(LearningEvent.created_at.desc(), LearningEvent.id.desc())
        .limit(limit)
      ).all()
    )
