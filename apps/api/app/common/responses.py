from typing import Any


def success(data: Any = None, message: str = "ok") -> dict[str, Any]:
  return {"success": True, "data": data, "message": message}

