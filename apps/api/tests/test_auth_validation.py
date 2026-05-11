from fastapi.testclient import TestClient

from app.main import app


def test_register_rejects_invalid_username() -> None:
  client = TestClient(app)
  response = client.post(
    "/api/auth/register",
    json={"username": "bad name", "password": "password123", "role": "student"},
  )

  assert response.status_code == 422
