from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.reports.schemas import MyLearningReport
from app.modules.reports.service import LearningReportService

router = APIRouter()


@router.get("/me", response_model=MyLearningReport)
def get_my_report(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> MyLearningReport:
  return LearningReportService(db).get_my_report(current_user)
