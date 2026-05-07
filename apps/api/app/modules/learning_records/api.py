from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_learning_records() -> list[dict[str, str]]:
  return []

