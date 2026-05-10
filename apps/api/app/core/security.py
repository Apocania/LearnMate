import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from app.core.config import settings


def get_password_hash(password: str) -> str:
  salt = secrets.token_hex(16)
  password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
  return f"pbkdf2_sha256${salt}${password_hash.hex()}"


def verify_password(plain_password: str, password_hash: str) -> bool:
  try:
    algorithm, salt, expected_hash = password_hash.split("$", 2)
  except ValueError:
    return False

  if algorithm != "pbkdf2_sha256":
    return False

  actual_hash = hashlib.pbkdf2_hmac(
    "sha256",
    plain_password.encode("utf-8"),
    salt.encode("utf-8"),
    120000,
  ).hex()
  return hmac.compare_digest(actual_hash, expected_hash)


def create_access_token(subject: str, expire_minutes: int) -> str:
  expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
  payload = {"sub": subject, "exp": int(expires_at.timestamp())}
  payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
  payload_part = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")
  signature = hmac.new(settings.jwt_secret.encode("utf-8"), payload_part.encode("utf-8"), hashlib.sha256)
  signature_part = base64.urlsafe_b64encode(signature.digest()).decode("utf-8").rstrip("=")
  return f"{payload_part}.{signature_part}"


def decode_access_token(token: str) -> dict[str, str | int] | None:
  try:
    payload_part, signature_part = token.split(".", 1)
  except ValueError:
    return None

  expected_signature = hmac.new(
    settings.jwt_secret.encode("utf-8"),
    payload_part.encode("utf-8"),
    hashlib.sha256,
  )
  expected_signature_part = base64.urlsafe_b64encode(expected_signature.digest()).decode("utf-8").rstrip("=")

  if not hmac.compare_digest(signature_part, expected_signature_part):
    return None

  padded_payload = payload_part + "=" * (-len(payload_part) % 4)
  try:
    payload = json.loads(base64.urlsafe_b64decode(padded_payload.encode("utf-8")))
  except (ValueError, json.JSONDecodeError):
    return None

  expires_at = payload.get("exp")
  if not isinstance(expires_at, int) or expires_at < int(datetime.now(timezone.utc).timestamp()):
    return None

  return payload
