from sqlalchemy.orm import Session
import json

from app.modules.auth.models import User
from app.modules.reports.repository import LearningReportRepository
from app.modules.reports.schemas import LearningProgressItem, MyLearningReport, RecentCourseProgress, TeachingCourseSummary


class LearningReportService:
  def __init__(self, db: Session) -> None:
    self.repository = LearningReportRepository(db)

  def get_my_report(self, current_user: User) -> MyLearningReport:
    enrolled_course_count = self.repository.count_enrolled_courses(current_user.id)
    created_course_count = self.repository.count_created_courses(current_user.id)
    forum_post_count = self.repository.count_forum_posts(current_user.id)
    forum_comment_count = self.repository.count_forum_comments(current_user.id)
    ai_question_count = self.repository.count_ai_questions(current_user.id)
    uploaded_file_count = self.repository.count_uploaded_files(current_user.id)
    learning_event_count = self.repository.count_learning_events(current_user.id)
    student_count = self.repository.count_students_for_teacher(current_user.id) if current_user.role == "mentor" else 0
    chapter_count = self.repository.count_chapters_for_teacher(current_user.id) if current_user.role == "mentor" else 0
    course_summaries = [
      TeachingCourseSummary(**summary)
      for summary in (
        self.repository.list_teaching_course_summaries(current_user.id)
        if current_user.role == "mentor"
        else []
      )
    ]

    interaction_count = forum_post_count + forum_comment_count
    course_count = enrolled_course_count if current_user.role == "student" else created_course_count
    study_hours = round(self.repository.sum_study_seconds(current_user.id) / 3600, 1)

    recent_course_progress = self._build_recent_course_progress(current_user, course_summaries)
    progress = self._build_progress(
      current_user.role,
      course_count,
      interaction_count,
      ai_question_count,
      uploaded_file_count,
      student_count,
      chapter_count,
    )

    recent_activities = self._build_recent_activities(current_user)
    suggestions = self._build_suggestions(
      current_user.role,
      course_count,
      interaction_count,
      uploaded_file_count,
      student_count,
      chapter_count,
    )
    daily_tasks = self._build_daily_tasks(
      current_user.role,
      course_count,
      interaction_count,
      ai_question_count,
      uploaded_file_count,
      student_count,
      chapter_count,
      recent_course_progress,
    )

    return MyLearningReport(
      user_id=current_user.id,
      username=current_user.username,
      role=current_user.role,
      enrolled_course_count=enrolled_course_count,
      created_course_count=created_course_count,
      forum_post_count=forum_post_count,
      forum_comment_count=forum_comment_count,
      ai_question_count=ai_question_count,
      uploaded_file_count=uploaded_file_count,
      learning_event_count=learning_event_count,
      student_count=student_count,
      chapter_count=chapter_count,
      course_summaries=course_summaries,
      study_hours=study_hours,
      progress=progress,
      recent_activities=recent_activities,
      suggestions=suggestions,
      recent_course_progress=recent_course_progress,
      daily_tasks=daily_tasks,
    )

  def _build_progress(
    self,
    role: str,
    course_count: int,
    interaction_count: int,
    ai_question_count: int,
    uploaded_file_count: int,
    student_count: int,
    chapter_count: int,
  ) -> list[LearningProgressItem]:
    if role == "mentor":
      return [
        LearningProgressItem(label="课程建设", percent=min(course_count * 25, 100)),
        LearningProgressItem(label="学生参与", percent=min(student_count * 12, 100)),
        LearningProgressItem(label="章节完善", percent=min(chapter_count * 15, 100)),
        LearningProgressItem(label="资料建设", percent=min(uploaded_file_count * 20, 100)),
      ]

    return [
      LearningProgressItem(label="课程参与", percent=min(course_count * 25, 100)),
      LearningProgressItem(label="讨论互动", percent=min(interaction_count * 15, 100)),
      LearningProgressItem(label="智能伴学", percent=min(ai_question_count * 20, 100)),
      LearningProgressItem(
        label="学习记录",
        percent=min(course_count * 15 + ai_question_count * 10 + interaction_count * 10, 100),
      ),
    ]

  def _build_recent_course_progress(
    self,
    current_user: User,
    course_summaries: list[TeachingCourseSummary],
  ) -> list[RecentCourseProgress]:
    if current_user.role == "mentor":
      return [
        RecentCourseProgress(
          id=summary.id,
          title=summary.title,
          percent=min(summary.chapter_count * 18 + summary.file_count * 16 + summary.enrollment_count * 10, 100),
          status_label=self._mentor_course_status(summary),
        )
        for summary in course_summaries[:3]
      ]

    progress_items: list[RecentCourseProgress] = []
    for summary in self.repository.list_student_course_progress_summaries(current_user.id):
      percent = int(summary["progress_percent"])
      progress_items.append(
        RecentCourseProgress(
          id=summary["id"],
          title=summary["title"],
          percent=percent,
          status_label=self._student_course_status(percent),
        )
      )
    return progress_items

  def _student_course_status(self, percent: int) -> str:
    if percent >= 80:
      return "接近完成"
    if percent >= 45:
      return "进行中"
    if percent > 20:
      return "刚起步"
    return "待开始"

  def _mentor_course_status(self, summary: TeachingCourseSummary) -> str:
    if summary.status == "draft":
      return "草稿建设"
    if summary.enrollment_count == 0:
      return "待招生"
    if summary.chapter_count == 0:
      return "待补章节"
    return "运行中"

  def _build_recent_activities(self, current_user: User) -> list[str]:
    event_activities = self._build_event_activities(current_user.id)
    if event_activities:
      return event_activities

    if current_user.role == "student":
      course_titles = self.repository.list_recent_course_titles(current_user.id)
      activities = [f"加入课程：{title}" for title in course_titles]
    else:
      course_titles = self.repository.list_recent_created_course_titles(current_user.id)
      activities = [f"创建课程：{title}" for title in course_titles]

    if not activities:
      return ["暂无学习轨迹，开始浏览课程或参与讨论后会自动更新。"]
    return activities

  def _build_event_activities(self, user_id: int) -> list[str]:
    labels = {
      "course_enrolled": "加入课程",
      "course_left": "退出课程",
      "chapter_created": "创建章节",
      "file_uploaded": "上传课件",
      "forum_post_created": "发布讨论",
      "forum_comment_created": "参与评论",
      "forum_post_liked": "点赞帖子",
      "assistant_question": "提问智能伴学",
      "course_viewed": "浏览课程",
      "file_downloaded": "下载课件",
    }
    activities: list[str] = []
    for event in self.repository.list_recent_events(user_id):
      try:
        payload = json.loads(event.event_payload or "{}")
      except json.JSONDecodeError:
        payload = {}
      label = labels.get(event.event_type, event.event_type)
      title = (
        payload.get("course_title")
        or payload.get("chapter_title")
        or payload.get("file_name")
        or payload.get("post_title")
        or payload.get("question")
      )
      activities.append(f"{label}{f'：{title}' if title else ''}")
    return activities

  def _build_suggestions(
    self,
    role: str,
    course_count: int,
    interaction_count: int,
    uploaded_file_count: int,
    student_count: int,
    chapter_count: int,
  ) -> list[str]:
    suggestions: list[str] = []
    if course_count == 0:
      suggestions.append("先从课程中心选择或创建一门课程，建立学习起点。")
    if interaction_count == 0:
      suggestions.append("到讨论交流区发帖或评论，让学习记录更完整。")
    if role == "student":
      suggestions.append("使用智能伴学整理课程问题，问答会自动纳入学习轨迹。")
    else:
      if chapter_count == 0:
        suggestions.append("为课程补充章节，学生会更容易按路径学习。")
      if uploaded_file_count == 0:
        suggestions.append("上传课件并绑定课程章节，可以提升智能答疑和学生学习支持质量。")
      if student_count == 0:
        suggestions.append("课程发布后可以引导学生加入，便于查看学生名单和参与情况。")
      suggestions.append("定期查看讨论交流区，及时回复学生的问题和想法。")
    return suggestions

  def _build_daily_tasks(
    self,
    role: str,
    course_count: int,
    interaction_count: int,
    ai_question_count: int,
    uploaded_file_count: int,
    student_count: int,
    chapter_count: int,
    recent_course_progress: list[RecentCourseProgress],
  ) -> list[str]:
    tasks: list[str] = []
    if role == "student":
      if course_count == 0:
        tasks.append("从课程中心加入一门已发布课程，建立今天的学习入口。")
      elif recent_course_progress:
        course = min(recent_course_progress, key=lambda item: item.percent)
        tasks.append(f"继续学习《{course.title}》，把进度从 {course.percent}% 往前推进一步。")
      if ai_question_count == 0:
        tasks.append("向智能伴学提出一个课程问题，形成可回看的问答记录。")
      if interaction_count == 0:
        tasks.append("在讨论交流区发帖或评论一次，把想法沉淀进学习记录。")
      if not tasks:
        tasks.append("复盘最近一次学习记录，整理一个还想继续追问的问题。")
      return tasks[:3]

    if course_count == 0:
      tasks.append("创建第一门课程，并补充清晰的课程简介。")
    if chapter_count == 0:
      tasks.append("给课程添加章节，让学生能按路径学习。")
    if uploaded_file_count == 0:
      tasks.append("上传并绑定课件资料，帮助智能伴学获得课程上下文。")
    if student_count == 0 and course_count > 0:
      tasks.append("引导学生加入课程，后续私信和公告会按课程名单发送。")
    if not tasks:
      tasks.append("查看课程讨论和学生名单，给需要帮助的学生发送课程私信。")
    return tasks[:3]
