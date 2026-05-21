from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, get_optional_current_user
from app.modules.auth.models import User
from app.modules.courses.schemas import (
  CourseChapterCreate,
  CourseChapterResponse,
  CourseChapterUpdate,
  CourseCreate,
  CourseResponse,
  CourseUpdate,
)
from app.modules.courses.service import CourseService

router = APIRouter()


@router.get("", response_model=list[CourseResponse])
def list_courses(
  db: Session = Depends(get_db),
  current_user: User | None = Depends(get_optional_current_user),
) -> list[CourseResponse]:
  return CourseService(db).list_courses(current_user)


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
  payload: CourseCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> CourseResponse:
  return CourseService(db).create_course(payload, current_user)


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
  course_id: int,
  db: Session = Depends(get_db),
  current_user: User | None = Depends(get_optional_current_user),
) -> CourseResponse:
  return CourseService(db).get_course(course_id, current_user)


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
  course_id: int,
  payload: CourseUpdate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> CourseResponse:
  return CourseService(db).update_course(course_id, payload, current_user)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
  course_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> Response:
  CourseService(db).delete_course(course_id, current_user)
  return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{course_id}/enroll", response_model=CourseResponse)
def enroll_course(
  course_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> CourseResponse:
  return CourseService(db).enroll_course(course_id, current_user)


@router.delete("/{course_id}/enroll", response_model=CourseResponse)
def leave_course(
  course_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> CourseResponse:
  return CourseService(db).leave_course(course_id, current_user)


@router.get("/{course_id}/chapters", response_model=list[CourseChapterResponse])
def list_course_chapters(course_id: int, db: Session = Depends(get_db)) -> list[CourseChapterResponse]:
  return CourseService(db).list_chapters(course_id)


@router.post("/{course_id}/chapters", response_model=CourseChapterResponse, status_code=status.HTTP_201_CREATED)
def create_course_chapter(
  course_id: int,
  payload: CourseChapterCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> CourseChapterResponse:
  return CourseService(db).create_chapter(course_id, payload, current_user)


@router.put("/{course_id}/chapters/{chapter_id}", response_model=CourseChapterResponse)
def update_course_chapter(
  course_id: int,
  chapter_id: int,
  payload: CourseChapterUpdate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> CourseChapterResponse:
  return CourseService(db).update_chapter(course_id, chapter_id, payload, current_user)


@router.delete("/{course_id}/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course_chapter(
  course_id: int,
  chapter_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> Response:
  CourseService(db).delete_chapter(course_id, chapter_id, current_user)
  return Response(status_code=status.HTTP_204_NO_CONTENT)
