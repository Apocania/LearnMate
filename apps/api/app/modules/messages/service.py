from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.forum.models import ForumComment, ForumPost
from app.modules.messages.models import UserMessage
from app.modules.messages.repository import MessageRepository
from app.modules.messages.schemas import (
  AnnouncementCreate,
  AnnouncementResult,
  PrivateMessageCreate,
  StudentRecipientResponse,
  UserMessageResponse,
)


class MessageService:
  def __init__(self, db: Session) -> None:
    self.repository = MessageRepository(db)

  def list_my_messages(self, current_user: User) -> list[UserMessageResponse]:
    return [self._to_response(message) for message in self.repository.list_messages(current_user.id)]

  def get_unread_count(self, current_user: User) -> int:
    return self.repository.count_unread(current_user.id)

  def list_student_recipients(self, current_user: User) -> list[StudentRecipientResponse]:
    self._ensure_mentor(current_user)
    return [
      StudentRecipientResponse(
        id=student.id,
        username=student.username,
        avatar_url=student.avatar_url,
        course_id=course_id,
        course_title=course_title,
      )
      for student, course_id, course_title in self.repository.list_students_for_teacher_courses(current_user.id)
    ]

  def mark_as_read(self, message_id: int, current_user: User) -> UserMessageResponse:
    message = self.repository.get_message(message_id)
    if message is None or message.recipient_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")
    return self._to_response(self.repository.mark_as_read(message))

  def mark_all_as_read(self, current_user: User) -> None:
    self.repository.mark_all_as_read(current_user.id)

  def send_private_message(self, payload: PrivateMessageCreate, current_user: User) -> UserMessageResponse:
    self._ensure_mentor(current_user)
    if payload.course_id is None:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请选择课程后再发送私信")
    course = self.repository.get_owned_course(payload.course_id, current_user.id)
    if course is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在或无权发送")
    recipient = self.repository.get_user_by_username(payload.recipient_username.strip().lower())
    if recipient is None or recipient.role != "student":
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生不存在")
    if self.repository.get_student_enrollment(course.id, recipient.id) is None:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能给本课程学生发送私信")

    message = self.repository.create_message(
      recipient_id=recipient.id,
      recipient_name=recipient.username,
      sender_id=current_user.id,
      sender_name=current_user.username,
      message_type="private",
      title=payload.title,
      content=payload.content,
      source_type="course_private",
      source_id=course.id,
    )
    return self._to_response(message)

  def send_announcement(self, payload: AnnouncementCreate, current_user: User) -> AnnouncementResult:
    self._ensure_mentor(current_user)
    if payload.course_id is None:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请选择课程后再发布公告")
    course = self.repository.get_owned_course(payload.course_id, current_user.id)
    if course is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在或无权发送")
    students = self.repository.list_students_for_course(course.id, current_user.id)
    messages = [
      UserMessage(
        recipient_id=student.id,
        recipient_name=student.username,
        sender_id=current_user.id,
        sender_name=current_user.username,
        message_type="announcement",
        title=payload.title,
        content=payload.content,
        source_type="course_announcement",
        source_id=course.id,
      )
      for student in students
    ]
    self.repository.create_messages(messages)
    return AnnouncementResult(created_count=len(messages))

  def notify_post_liked(self, post: ForumPost, actor: User) -> None:
    if post.author_id == actor.id:
      return
    self.repository.create_message(
      recipient_id=post.author_id,
      recipient_name=post.author_name,
      sender_id=actor.id,
      sender_name=actor.username,
      message_type="like",
      title="你的帖子收到点赞",
      content=f"{actor.username} 点赞了《{post.title}》。",
      source_type="forum_post",
      source_id=post.id,
    )

  def notify_post_commented(self, post: ForumPost, comment: ForumComment, actor: User) -> None:
    if post.author_id == actor.id:
      return
    preview = comment.content.strip()
    if len(preview) > 80:
      preview = f"{preview[:80]}..."
    self.repository.create_message(
      recipient_id=post.author_id,
      recipient_name=post.author_name,
      sender_id=actor.id,
      sender_name=actor.username,
      message_type="comment",
      title="你的帖子收到评论",
      content=f"{actor.username} 评论了《{post.title}》：{preview}",
      source_type="forum_post",
      source_id=post.id,
    )

  def _to_response(self, message: UserMessage) -> UserMessageResponse:
    return UserMessageResponse.model_validate(message)

  def _ensure_mentor(self, current_user: User) -> None:
    if current_user.role != "mentor":
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有伴学师可以发送消息")
