from pydantic import BaseModel


class ForumPostSummary(BaseModel):
  id: str
  title: str
  author_name: str

