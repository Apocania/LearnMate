from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.messages.models import UserMessage


class MessageRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def list_messages(self, recipient_id: int) -> list[UserMessage]:
    statement = (
      select(UserMessage)
      .where(UserMessage.recipient_id == recipient_id)
      .order_by(UserMessage.created_at.desc(), UserMessage.id.desc())
    )
    return list(self.db.scalars(statement).all())

  def get_message(self, message_id: int) -> UserMessage | None:
    return self.db.get(UserMessage, message_id)

  def count_unread(self, recipient_id: int) -> int:
    return (
      self.db.scalar(
        select(func.count())
        .select_from(UserMessage)
        .where(UserMessage.recipient_id == recipient_id, UserMessage.is_read.is_(False))
      )
      or 0
    )

  def create_message(
    self,
    recipient_id: int,
    recipient_name: str,
    message_type: str,
    title: str,
    content: str,
    sender_id: int | None = None,
    sender_name: str | None = None,
    source_type: str | None = None,
    source_id: int | None = None,
  ) -> UserMessage:
    message = UserMessage(
      recipient_id=recipient_id,
      recipient_name=recipient_name,
      sender_id=sender_id,
      sender_name=sender_name,
      message_type=message_type,
      title=title,
      content=content,
      source_type=source_type,
      source_id=source_id,
    )
    self.db.add(message)
    self.db.commit()
    self.db.refresh(message)
    return message

  def create_messages(self, messages: list[UserMessage]) -> list[UserMessage]:
    if not messages:
      return []
    self.db.add_all(messages)
    self.db.commit()
    for message in messages:
      self.db.refresh(message)
    return messages

  def mark_as_read(self, message: UserMessage) -> UserMessage:
    if not message.is_read:
      message.is_read = True
      self.db.add(message)
      self.db.commit()
      self.db.refresh(message)
    return message

  def mark_all_as_read(self, recipient_id: int) -> int:
    messages = list(
      self.db.scalars(
        select(UserMessage).where(UserMessage.recipient_id == recipient_id, UserMessage.is_read.is_(False))
      ).all()
    )
    for message in messages:
      message.is_read = True
      self.db.add(message)
    self.db.commit()
    return len(messages)

  def get_user_by_username(self, username: str) -> User | None:
    return self.db.scalar(select(User).where(User.username == username))

  def list_students(self) -> list[User]:
    return list(self.db.scalars(select(User).where(User.role == "student").order_by(User.username.asc())).all())
