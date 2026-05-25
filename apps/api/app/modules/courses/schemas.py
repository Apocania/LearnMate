from datetime import datetime

from pydantic import BaseModel


class CourseCreate(BaseModel):
  title: str
  description: str
  status: str = "published"


class CourseUpdate(BaseModel):
  title: str | None = None
  description: str | None = None
  status: str | None = None


class CourseResponse(BaseModel):
  id: int
  title: str
  description: str
  teacher_id: int
  teacher_name: str
  status: str
  enrollment_count: int = 0
  joined_by_me: bool = False

  model_config = {"from_attributes": True}


class CourseChapterCreate(BaseModel):
  title: str
  description: str = ""
  sort_order: int = 1


class CourseChapterUpdate(BaseModel):
  title: str | None = None
  description: str | None = None
  sort_order: int | None = None


class CourseChapterResponse(BaseModel):
  id: int
  course_id: int
  title: str
  description: str
  sort_order: int

  model_config = {"from_attributes": True}


class CourseEnrollmentResponse(BaseModel):
  id: int
  course_id: int
  student_id: int
  student_name: str
  created_at: datetime

  model_config = {"from_attributes": True}
