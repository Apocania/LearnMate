from fastapi import APIRouter

from app.modules.courses.schemas import CourseSummary

router = APIRouter()


@router.get("", response_model=list[CourseSummary])
def list_courses() -> list[CourseSummary]:
  return []


@router.get("/{course_id}")
def get_course(course_id: str) -> dict[str, str]:
  return {"id": course_id, "title": "课程详情占位"}


@router.post("/{course_id}/enroll")
def enroll_course(course_id: str) -> dict[str, str]:
  return {"course_id": course_id, "status": "enrolled"}

