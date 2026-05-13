from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  username: Mapped[str] = mapped_column(unique=True, index=True)
  password_hash: Mapped[str]
  role: Mapped[str]
  avatar_url: Mapped[str | None] = mapped_column(nullable=True)
