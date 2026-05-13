from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.forum.models import ForumComment, ForumLike, ForumPost


class ForumRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def list_posts(self, current_user_id: int | None = None) -> list[ForumPost]:
    return list(self.db.scalars(select(ForumPost).order_by(ForumPost.id.desc())).all())

  def get_post(self, post_id: int) -> ForumPost | None:
    return self.db.get(ForumPost, post_id)

  def get_comment(self, comment_id: int) -> ForumComment | None:
    return self.db.get(ForumComment, comment_id)

  def get_user_avatar_urls(self, user_ids: set[int]) -> dict[int, str | None]:
    if not user_ids:
      return {}
    rows = self.db.execute(select(User.id, User.avatar_url).where(User.id.in_(user_ids))).all()
    return {user_id: avatar_url for user_id, avatar_url in rows}

  def create_post(self, title: str, content: str, author_id: int, author_name: str, course_id: int | None) -> ForumPost:
    post = ForumPost(
      title=title,
      content=content,
      author_id=author_id,
      author_name=author_name,
      course_id=course_id,
    )
    self.db.add(post)
    self.db.commit()
    self.db.refresh(post)
    return post

  def list_comments(self, post_id: int) -> list[ForumComment]:
    return list(self.db.scalars(select(ForumComment).where(ForumComment.post_id == post_id).order_by(ForumComment.id.asc())).all())

  def create_comment(self, post_id: int, author_id: int, author_name: str, content: str) -> ForumComment:
    comment = ForumComment(post_id=post_id, author_id=author_id, author_name=author_name, content=content)
    self.db.add(comment)
    self.db.commit()
    self.db.refresh(comment)
    return comment

  def get_like(self, post_id: int, user_id: int) -> ForumLike | None:
    return self.db.scalar(select(ForumLike).where(ForumLike.post_id == post_id, ForumLike.user_id == user_id))

  def toggle_like(self, post_id: int, user_id: int) -> bool:
    like = self.get_like(post_id, user_id)
    if like:
      self.db.delete(like)
      self.db.commit()
      return False

    self.db.add(ForumLike(post_id=post_id, user_id=user_id))
    self.db.commit()
    return True

  def delete_comment(self, comment: ForumComment) -> None:
    self.db.delete(comment)
    self.db.commit()

  def count_likes(self, post_id: int) -> int:
    return self.db.scalar(select(func.count()).select_from(ForumLike).where(ForumLike.post_id == post_id)) or 0

  def count_comments(self, post_id: int) -> int:
    return self.db.scalar(select(func.count()).select_from(ForumComment).where(ForumComment.post_id == post_id)) or 0

  def delete_post_related(self, post_id: int) -> None:
    self.db.execute(delete(ForumLike).where(ForumLike.post_id == post_id))
    self.db.execute(delete(ForumComment).where(ForumComment.post_id == post_id))
    self.db.commit()

  def delete_post(self, post: ForumPost) -> None:
    self.delete_post_related(post.id)
    self.db.delete(post)
    self.db.commit()
