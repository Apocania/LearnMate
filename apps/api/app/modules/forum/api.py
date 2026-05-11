from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, get_optional_current_user
from app.modules.auth.models import User
from app.modules.forum.schemas import (
  ForumCommentCreate,
  ForumCommentResponse,
  ForumLikeResponse,
  ForumPostCreate,
  ForumPostResponse,
)
from app.modules.forum.service import ForumService

router = APIRouter()


@router.get("/posts", response_model=list[ForumPostResponse])
def list_posts(
  db: Session = Depends(get_db),
  current_user: User | None = Depends(get_optional_current_user),
) -> list[ForumPostResponse]:
  return ForumService(db).list_posts(current_user)


@router.post("/posts", response_model=ForumPostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
  payload: ForumPostCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> ForumPostResponse:
  return ForumService(db).create_post(payload, current_user)


@router.get("/posts/{post_id}/comments", response_model=list[ForumCommentResponse])
def list_comments(post_id: int, db: Session = Depends(get_db)) -> list[ForumCommentResponse]:
  return ForumService(db).list_comments(post_id)


@router.post("/posts/{post_id}/comments", response_model=ForumCommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
  post_id: int,
  payload: ForumCommentCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> ForumCommentResponse:
  return ForumService(db).create_comment(post_id, payload.content, current_user)


@router.post("/posts/{post_id}/like", response_model=ForumLikeResponse)
def toggle_like(
  post_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> ForumLikeResponse:
  liked, like_count = ForumService(db).toggle_like(post_id, current_user)
  return ForumLikeResponse(liked=liked, like_count=like_count)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
  post_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> Response:
  ForumService(db).delete_post(post_id, current_user)
  return Response(status_code=status.HTTP_204_NO_CONTENT)
