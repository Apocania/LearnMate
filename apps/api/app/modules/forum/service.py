from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.forum.models import ForumComment, ForumPost
from app.modules.forum.repository import ForumRepository
from app.modules.forum.schemas import ForumPostCreate, ForumPostResponse


class ForumService:
  def __init__(self, db: Session) -> None:
    self.repository = ForumRepository(db)

  def list_posts(self, current_user: User | None = None) -> list[ForumPostResponse]:
    posts = self.repository.list_posts(current_user.id if current_user else None)
    return [self._build_post_response(post, current_user) for post in posts]

  def create_post(self, payload: ForumPostCreate, current_user: User) -> ForumPostResponse:
    post = self.repository.create_post(
      title=payload.title,
      content=payload.content,
      author_id=current_user.id,
      author_name=current_user.username,
      course_id=payload.course_id,
    )
    return self._build_post_response(post, current_user)

  def list_comments(self, post_id: int) -> list[ForumComment]:
    self._get_post_or_404(post_id)
    return self.repository.list_comments(post_id)

  def create_comment(self, post_id: int, content: str, current_user: User) -> ForumComment:
    self._get_post_or_404(post_id)
    return self.repository.create_comment(post_id, current_user.id, current_user.username, content)

  def toggle_like(self, post_id: int, current_user: User) -> tuple[bool, int]:
    self._get_post_or_404(post_id)
    liked = self.repository.toggle_like(post_id, current_user.id)
    return liked, self.repository.count_likes(post_id)

  def _get_post_or_404(self, post_id: int) -> ForumPost:
    post = self.repository.get_post(post_id)
    if post is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")
    return post

  def _build_post_response(self, post: ForumPost, current_user: User | None = None) -> ForumPostResponse:
    liked_by_me = False
    if current_user:
      liked_by_me = self.repository.get_like(post.id, current_user.id) is not None

    return ForumPostResponse(
      id=post.id,
      title=post.title,
      content=post.content,
      author_id=post.author_id,
      author_name=post.author_name,
      course_id=post.course_id,
      created_at=post.created_at,
      like_count=self.repository.count_likes(post.id),
      comment_count=self.repository.count_comments(post.id),
      liked_by_me=liked_by_me,
    )
