from pydantic import BaseModel


class CourseSummary(BaseModel):
  id: str
  title: str
  description: str
  teacher_name: str

