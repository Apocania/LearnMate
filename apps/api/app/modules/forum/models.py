from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ForumPost(Base):
  __tablename__ = "forum_posts"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  title: Mapped[str]
  content: Mapped[str]
  author_id: Mapped[int]

