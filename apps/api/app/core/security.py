from datetime import datetime, timedelta, timezone


def get_password_hash(password: str) -> str:
  # TODO: Replace with passlib/bcrypt before implementing real authentication.
  return f"dev-hash:{password}"


def verify_password(plain_password: str, password_hash: str) -> bool:
  return get_password_hash(plain_password) == password_hash


def create_access_token(subject: str, expire_minutes: int) -> str:
  # TODO: Replace with signed JWT before production use.
  expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
  return f"dev-token:{subject}:{int(expires_at.timestamp())}"

