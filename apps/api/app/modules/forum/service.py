from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.forum.models import ForumComment, ForumPost
from app.modules.forum.repository import ForumRepository
from app.modules.forum.schemas import ForumCommentResponse, ForumPostCreate, ForumPostResponse
from app.modules.messages.service import MessageService


class ForumService:
  def __init__(self, db: Session) -> None:
    self.repository = ForumRepository(db)

  def list_posts(self, current_user: User | None = None) -> list[ForumPostResponse]:
    posts = self.repository.list_posts(current_user.id if current_user else None)
    avatar_urls = self.repository.get_user_avatar_urls({post.author_id for post in posts})
    return [self._build_post_response(post, current_user, avatar_urls.get(post.author_id)) for post in posts]

  def create_post(self, payload: ForumPostCreate, current_user: User) -> ForumPostResponse:
    self._ensure_discussion_actor(current_user)
    post = self.repository.create_post(
      title=payload.title,
      content=payload.content,
      author_id=current_user.id,
      author_name=current_user.username,
      course_id=payload.course_id,
    )
    return self._build_post_response(post, current_user, current_user.avatar_url)

  def list_comments(self, post_id: int, current_user: User | None = None) -> list[ForumCommentResponse]:
    self._get_post_or_404(post_id)
    comments = self.repository.list_comments(post_id)
    avatar_urls = self.repository.get_user_avatar_urls({comment.author_id for comment in comments})
    return [
      self._build_comment_response(comment, avatar_urls.get(comment.author_id), current_user)
      for comment in comments
    ]

  def create_comment(self, post_id: int, content: str, current_user: User) -> ForumCommentResponse:
    self._ensure_discussion_actor(current_user)
    post = self._get_post_or_404(post_id)
    comment = self.repository.create_comment(post_id, current_user.id, current_user.username, content)
    MessageService(self.repository.db).notify_post_commented(post, comment, current_user)
    return self._build_comment_response(comment, current_user.avatar_url, current_user)

  def toggle_like(self, post_id: int, current_user: User) -> tuple[bool, int]:
    self._ensure_discussion_actor(current_user)
    post = self._get_post_or_404(post_id)
    liked = self.repository.toggle_like(post_id, current_user.id)
    if liked:
      MessageService(self.repository.db).notify_post_liked(post, current_user)
    return liked, self.repository.count_likes(post_id)

  def delete_comment(self, comment_id: int, current_user: User) -> None:
    comment = self.repository.get_comment(comment_id)
    if comment is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    if current_user.role != "mentor" and comment.author_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能删除自己的评论")
    self.repository.delete_comment(comment)

  def delete_post(self, post_id: int, current_user: User) -> None:
    self._ensure_mentor(current_user)
    post = self._get_post_or_404(post_id)
    self.repository.delete_post(post)

  def _get_post_or_404(self, post_id: int) -> ForumPost:
    post = self.repository.get_post(post_id)
    if post is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")
    return post

  def _build_post_response(
    self,
    post: ForumPost,
    current_user: User | None = None,
    author_avatar_url: str | None = None,
  ) -> ForumPostResponse:
    liked_by_me = False
    if current_user:
      liked_by_me = self.repository.get_like(post.id, current_user.id) is not None

    return ForumPostResponse(
      id=post.id,
      title=post.title,
      content=post.content,
      author_id=post.author_id,
      author_name=post.author_name,
      author_avatar_url=author_avatar_url,
      course_id=post.course_id,
      created_at=post.created_at,
      like_count=self.repository.count_likes(post.id),
      comment_count=self.repository.count_comments(post.id),
      liked_by_me=liked_by_me,
    )

  def _build_comment_response(
    self,
    comment: ForumComment,
    author_avatar_url: str | None = None,
    current_user: User | None = None,
  ) -> ForumCommentResponse:
    can_delete = False
    if current_user:
      can_delete = current_user.role == "mentor" or current_user.id == comment.author_id

    return ForumCommentResponse(
      id=comment.id,
      post_id=comment.post_id,
      author_id=comment.author_id,
      author_name=comment.author_name,
      author_avatar_url=author_avatar_url,
      content=comment.content,
      created_at=comment.created_at,
      can_delete=can_delete,
    )

  def _ensure_discussion_actor(self, current_user: User) -> None:
    if current_user.role not in {"student", "mentor"}:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前身份不能参与讨论")

  def _ensure_mentor(self, current_user: User) -> None:
    if current_user.role != "mentor":
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有伴学师可以管理交流区")
