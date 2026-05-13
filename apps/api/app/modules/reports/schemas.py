from pydantic import BaseModel


class LearningProgressItem(BaseModel):
  label: str
  percent: int


class MyLearningReport(BaseModel):
  user_id: int
  username: str
  role: str
  enrolled_course_count: int
  created_course_count: int
  forum_post_count: int
  forum_comment_count: int
  ai_question_count: int
  estimated_study_hours: float
  progress: list[LearningProgressItem]
  recent_activities: list[str]
  suggestions: list[str]
