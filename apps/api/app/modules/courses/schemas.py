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

  model_config = {"from_attributes": True}
