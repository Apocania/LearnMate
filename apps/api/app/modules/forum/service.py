import json
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.auth.models import User
from app.modules.forum.models import ForumComment, ForumPost
from app.modules.forum.repository import ForumRepository
from app.modules.forum.schemas import (
  ForumAttachmentResponse,
  ForumCommentResponse,
  ForumPostCreate,
  ForumPostResponse,
)
from app.modules.messages.service import MessageService

FORUM_ATTACHMENT_DIR = Path(__file__).resolve().parents[3] / "storage" / "forum-attachments"
FORUM_ATTACHMENT_TYPES = settings.upload_allowed_types | {"image/webp", "text/markdown"}
MAX_FORUM_ATTACHMENTS = 5


class ForumService:
  def __init__(self, db: Session) -> None:
    self.repository = ForumRepository(db)
    FORUM_ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)

  def list_posts(self, current_user: User | None = None) -> list[ForumPostResponse]:
    posts = self.repository.list_posts(current_user.id if current_user else None)
    avatar_urls = self.repository.get_user_avatar_urls({post.author_id for post in posts})
    return [self._build_post_response(post, current_user, avatar_urls.get(post.author_id)) for post in posts]

  async def create_post(
    self,
    payload: ForumPostCreate,
    current_user: User,
    uploads: list[UploadFile] | None = None,
  ) -> ForumPostResponse:
    self._ensure_discussion_actor(current_user)
    attachments = await self._store_attachments(uploads or [])
    post = self.repository.create_post(
      title=payload.title,
      content=payload.content,
      author_id=current_user.id,
      author_name=current_user.username,
      course_id=payload.course_id,
      attachments=json.dumps(attachments, ensure_ascii=False),
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
      attachments=self._load_attachments(post.attachments),
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

  async def _store_attachments(self, uploads: list[UploadFile]) -> list[dict[str, str | int]]:
    real_uploads = [upload for upload in uploads if upload.filename]
    if len(real_uploads) > MAX_FORUM_ATTACHMENTS:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"附件最多上传 {MAX_FORUM_ATTACHMENTS} 个")

    attachments: list[dict[str, str | int]] = []
    for upload in real_uploads:
      original_name = upload.filename or "unnamed-file"
      content_type = upload.content_type or "application/octet-stream"
      if content_type not in FORUM_ATTACHMENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"不支持的附件类型：{content_type}")

      content = await upload.read()
      if len(content) > settings.upload_max_size_bytes:
        raise HTTPException(
          status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
          detail=f"单个附件不能超过 {settings.upload_max_size_mb}MB",
        )
      if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="附件文件不能为空")

      suffix = Path(original_name).suffix
      stored_name = f"{uuid4().hex}{suffix}"
      target_path = FORUM_ATTACHMENT_DIR / stored_name
      target_path.write_bytes(content)
      attachments.append(
        {
          "original_name": original_name,
          "stored_name": stored_name,
          "content_type": content_type,
          "size": len(content),
          "url": f"/api/forum/attachments/{stored_name}/download",
        }
      )

    return attachments

  def _load_attachments(self, raw_attachments: str | None) -> list[ForumAttachmentResponse]:
    if not raw_attachments:
      return []
    try:
      attachments = json.loads(raw_attachments)
    except json.JSONDecodeError:
      return []
    if not isinstance(attachments, list):
      return []

    valid_attachments: list[ForumAttachmentResponse] = []
    for attachment in attachments:
      if not isinstance(attachment, dict):
        continue
      try:
        valid_attachments.append(ForumAttachmentResponse.model_validate(attachment))
      except ValueError:
        continue
    return valid_attachments

  def get_attachment_path(self, stored_name: str) -> Path:
    if "/" in stored_name or "\\" in stored_name:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="附件路径无效")
    path = FORUM_ATTACHMENT_DIR / stored_name
    if not path.exists():
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="附件不存在")
    return path
