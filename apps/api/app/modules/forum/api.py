from fastapi import APIRouter

router = APIRouter()


@router.get("/posts")
def list_posts() -> list[dict[str, str]]:
  return []

