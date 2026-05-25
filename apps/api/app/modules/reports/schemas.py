from pydantic import BaseModel


class LearningProgressItem(BaseModel):
  label: str
  percent: int


class TeachingCourseSummary(BaseModel):
  id: int
  title: str
  status: str
  enrollment_count: int
  chapter_count: int
  file_count: int


class MyLearningReport(BaseModel):
  user_id: int
  username: str
  role: str
  enrolled_course_count: int
  created_course_count: int
  forum_post_count: int
  forum_comment_count: int
  ai_question_count: int
  uploaded_file_count: int = 0
  learning_event_count: int = 0
  student_count: int = 0
  chapter_count: int = 0
  course_summaries: list[TeachingCourseSummary] = []
  estimated_study_hours: float
  progress: list[LearningProgressItem]
  recent_activities: list[str]
  suggestions: list[str]
