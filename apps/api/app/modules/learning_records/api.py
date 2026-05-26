from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.learning_records.schemas import (
  CourseProgressResponse,
  CourseProgressUpdateRequest,
  LearningEventRequest,
  LearningEventResponse,
)
from app.modules.learning_records.service import LearningRecordService

router = APIRouter()


@router.get("", response_model=list[LearningEventResponse])
def list_learning_records(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> list[LearningEventResponse]:
  return LearningRecordService(db).list_my_events(current_user)


@router.post("", response_model=LearningEventResponse, status_code=status.HTTP_201_CREATED)
def create_learning_record(
  payload: LearningEventRequest,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> LearningEventResponse:
  return LearningRecordService(db).create_event(payload, current_user)


@router.post("/course-progress", response_model=CourseProgressResponse)
def update_course_progress(
  payload: CourseProgressUpdateRequest,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> CourseProgressResponse:
  return LearningRecordService(db).update_course_progress(payload, current_user)
