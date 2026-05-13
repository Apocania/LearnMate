from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.reports.repository import LearningReportRepository
from app.modules.reports.schemas import LearningProgressItem, MyLearningReport


class LearningReportService:
  def __init__(self, db: Session) -> None:
    self.repository = LearningReportRepository(db)

  def get_my_report(self, current_user: User) -> MyLearningReport:
    enrolled_course_count = self.repository.count_enrolled_courses(current_user.id)
    created_course_count = self.repository.count_created_courses(current_user.id)
    forum_post_count = self.repository.count_forum_posts(current_user.id)
    forum_comment_count = self.repository.count_forum_comments(current_user.id)
    ai_question_count = 0

    interaction_count = forum_post_count + forum_comment_count
    course_count = enrolled_course_count if current_user.role == "student" else created_course_count
    estimated_study_hours = round(course_count * 1.5 + interaction_count * 0.25, 1)

    progress = [
      LearningProgressItem(label="课程参与", percent=min(course_count * 25, 100)),
      LearningProgressItem(label="讨论互动", percent=min(interaction_count * 15, 100)),
      LearningProgressItem(label="AI 伴学", percent=min(ai_question_count * 20, 100)),
    ]

    recent_activities = self._build_recent_activities(current_user)
    suggestions = self._build_suggestions(current_user.role, course_count, interaction_count)

    return MyLearningReport(
      user_id=current_user.id,
      username=current_user.username,
      role=current_user.role,
      enrolled_course_count=enrolled_course_count,
      created_course_count=created_course_count,
      forum_post_count=forum_post_count,
      forum_comment_count=forum_comment_count,
      ai_question_count=ai_question_count,
      estimated_study_hours=estimated_study_hours,
      progress=progress,
      recent_activities=recent_activities,
      suggestions=suggestions,
    )

  def _build_recent_activities(self, current_user: User) -> list[str]:
    if current_user.role == "student":
      course_titles = self.repository.list_recent_course_titles(current_user.id)
      activities = [f"加入课程：{title}" for title in course_titles]
    else:
      course_titles = self.repository.list_recent_created_course_titles(current_user.id)
      activities = [f"创建课程：{title}" for title in course_titles]

    if not activities:
      return ["暂无学习轨迹，开始浏览课程或参与讨论后会自动更新。"]
    return activities

  def _build_suggestions(self, role: str, course_count: int, interaction_count: int) -> list[str]:
    suggestions: list[str] = []
    if course_count == 0:
      suggestions.append("先从课程中心选择或创建一门课程，建立学习起点。")
    if interaction_count == 0:
      suggestions.append("到讨论交流区发帖或评论，让学习记录更完整。")
    if role == "student":
      suggestions.append("使用 AI 伴学整理课程问题，后续会纳入问答统计。")
    else:
      suggestions.append("上传课件并维护讨论区，可以提升学生学习支持质量。")
    return suggestions
