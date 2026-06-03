import json
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infrastructure.object_storage import ObjectStorageClient
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
from app.modules.learning_records.service import LearningRecordService

FORUM_ATTACHMENT_PREFIX = "forum-attachments"
LEGACY_FORUM_ATTACHMENT_DIR = Path(__file__).resolve().parents[3] / "storage" / "forum-attachments"
MAX_FORUM_ATTACHMENTS = 5


class ForumService:
  def __init__(self, db: Session) -> None:
    self.repository = ForumRepository(db)
    self.storage = ObjectStorageClient()

  def list_posts(
    self,
    current_user: User | None = None,
    course_id: int | None = None,
    keyword: str | None = None,
    status_filter: str | None = "active",
    page: int = 1,
    page_size: int = 20,
  ):
    if status_filter == "all" and current_user and current_user.role != "mentor":
      status_filter = "active"
    if not current_user or current_user.role != "mentor":
      status_filter = "active"

    page = max(page, 1)
    page_size = min(max(page_size, 1), 50)
    posts = self.repository.list_posts(
      course_id=course_id,
      keyword=keyword,
      status=status_filter,
      current_user=current_user,
      offset=(page - 1) * page_size,
      limit=page_size,
    )
    total = self.repository.count_posts(
      course_id=course_id,
      keyword=keyword,
      status=status_filter,
      current_user=current_user,
    )
    avatar_urls = self.repository.get_user_avatar_urls({post.author_id for post in posts})
    course_titles = self.repository.get_course_titles({post.course_id for post in posts if post.course_id})
    from app.modules.forum.schemas import ForumPostPage

    return ForumPostPage(
      items=[
        self._build_post_response(post, current_user, avatar_urls.get(post.author_id), course_titles.get(post.course_id or 0))
        for post in posts
      ],
      total=total,
      page=page,
      page_size=page_size,
    )

  async def create_post(
    self,
    payload: ForumPostCreate,
    current_user: User,
    uploads: list[UploadFile] | None = None,
  ) -> ForumPostResponse:
    self._ensure_discussion_actor(current_user)
    self._ensure_course_can_receive_post(payload.course_id, current_user)
    attachments = await self._store_attachments(uploads or [])
    post = self.repository.create_post(
      title=payload.title,
      content=payload.content,
      author_id=current_user.id,
      author_name=current_user.username,
      course_id=payload.course_id,
      attachments=json.dumps(attachments, ensure_ascii=False),
    )
    LearningRecordService(self.repository.db).record_event(
      current_user,
      "forum_post_created",
      course_id=payload.course_id,
      metadata={"post_title": post.title},
    )
    return self._build_post_response(post, current_user, current_user.avatar_url)

  def list_comments(self, post_id: int, current_user: User | None = None) -> list[ForumCommentResponse]:
    self._get_visible_post_or_404(post_id, current_user)
    comments = self.repository.list_comments(post_id)
    avatar_urls = self.repository.get_user_avatar_urls({comment.author_id for comment in comments})
    return [
      self._build_comment_response(comment, avatar_urls.get(comment.author_id), current_user)
      for comment in comments
    ]

  def create_comment(self, post_id: int, content: str, current_user: User) -> ForumCommentResponse:
    self._ensure_discussion_actor(current_user)
    post = self._get_visible_post_or_404(post_id, current_user)
    comment = self.repository.create_comment(post_id, current_user.id, current_user.username, content)
    MessageService(self.repository.db).notify_post_commented(post, comment, current_user)
    LearningRecordService(self.repository.db).record_event(
      current_user,
      "forum_comment_created",
      course_id=post.course_id,
      metadata={"post_title": post.title},
    )
    return self._build_comment_response(comment, current_user.avatar_url, current_user)

  def toggle_like(self, post_id: int, current_user: User) -> tuple[bool, int]:
    self._ensure_discussion_actor(current_user)
    post = self._get_visible_post_or_404(post_id, current_user)
    liked = self.repository.toggle_like(post_id, current_user.id)
    if liked:
      MessageService(self.repository.db).notify_post_liked(post, current_user)
      LearningRecordService(self.repository.db).record_event(
        current_user,
        "forum_post_liked",
        course_id=post.course_id,
        metadata={"post_title": post.title},
      )
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
    post = self._get_visible_post_or_404(post_id, current_user)
    self.repository.delete_post(post)

  def update_post_status(self, post_id: int, next_status: str, current_user: User) -> ForumPostResponse:
    self._ensure_mentor(current_user)
    if next_status not in {"active", "hidden"}:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="帖子状态无效")
    post = self._get_visible_post_or_404(post_id, current_user)
    updated_post = self.repository.update_post_status(post, next_status, current_user.id)
    return self._build_post_response(updated_post, current_user, None)

  def _get_post_or_404(self, post_id: int) -> ForumPost:
    post = self.repository.get_post(post_id)
    if post is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")
    return post

  def _get_visible_post_or_404(self, post_id: int, current_user: User | None = None) -> ForumPost:
    post = self._get_post_or_404(post_id)
    if not self._is_course_visible(post.course_id, current_user):
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")
    return post

  def _build_post_response(
    self,
    post: ForumPost,
    current_user: User | None = None,
    author_avatar_url: str | None = None,
    course_title: str | None = None,
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
      course_title=course_title,
      status=post.status,
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
      content_type = settings.normalize_upload_content_type(upload.content_type)
      if not settings.is_upload_allowed(original_name, content_type):
        raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail=f"不支持的附件类型：{content_type}",
        )

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
      stored_object = self.storage.put_object(f"{FORUM_ATTACHMENT_PREFIX}/{stored_name}", content, content_type)
      attachments.append(
        {
          "original_name": original_name,
          "stored_name": stored_name,
          "storage_provider": stored_object.provider,
          "object_key": stored_object.object_key,
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

  def get_attachment(self, stored_name: str, current_user: User | None = None) -> tuple[bytes, str, str]:
    if "/" in stored_name or "\\" in stored_name:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="附件路径无效")
    post = self.repository.find_post_by_attachment(stored_name)
    if post and not self._is_course_visible(post.course_id, current_user):
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="附件不存在")
    attachment = self._find_attachment_metadata(post, stored_name) if post else None
    object_key = (
      str(attachment.get("object_key"))
      if attachment and attachment.get("object_key")
      else f"{FORUM_ATTACHMENT_PREFIX}/{stored_name}"
    )
    storage_provider = str(attachment.get("storage_provider")) if attachment else None
    content_type = str(attachment.get("content_type")) if attachment else "application/octet-stream"
    original_name = str(attachment.get("original_name")) if attachment else stored_name
    if storage_provider is None:
      legacy_path = LEGACY_FORUM_ATTACHMENT_DIR / stored_name
      if legacy_path.exists():
        return legacy_path.read_bytes(), content_type, original_name
    return self.storage.read_object(object_key, storage_provider), content_type, original_name

  def _ensure_course_can_receive_post(self, course_id: int | None, current_user: User) -> None:
    if course_id is None:
      return
    course = self.repository.get_course(course_id)
    if course is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    if course.status == "published":
      return
    if current_user.role == "mentor" and course.teacher_id == current_user.id:
      return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")

  def _is_course_visible(self, course_id: int | None, current_user: User | None) -> bool:
    if course_id is None:
      return True
    course = self.repository.get_course(course_id)
    if course is None:
      return False
    if course.status == "published":
      return True
    return bool(current_user and current_user.role == "mentor" and course.teacher_id == current_user.id)

  def _find_attachment_metadata(self, post: ForumPost, stored_name: str) -> dict[str, str | int] | None:
    try:
      attachments = json.loads(post.attachments or "[]")
    except json.JSONDecodeError:
      return None
    if not isinstance(attachments, list):
      return None
    for attachment in attachments:
      if isinstance(attachment, dict) and attachment.get("stored_name") == stored_name:
        return attachment
    return None
