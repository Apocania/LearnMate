from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
def get_current_user() -> dict[str, str]:
  return {"id": "dev-user", "username": "student1", "role": "student"}

