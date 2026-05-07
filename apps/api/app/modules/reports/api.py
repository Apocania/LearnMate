from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
def get_my_reports() -> list[dict[str, str]]:
  return []

