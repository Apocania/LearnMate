from pydantic import BaseModel


class LearningReportSummary(BaseModel):
  id: str
  title: str
  summary: str

