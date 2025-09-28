from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import AI_EXPERTISE_TAGS
from ..db import get_db_session
from ..dependencies import get_current_user
from ..models import User
from ..schemas import PrivateUserProfile, PublicUserProfile, UserProfileUpdatePayload
from ..usernames import UsernameValidationError, is_username_generated_from_email, normalize_username

router = APIRouter(prefix="/users", tags=["users"])

_ALLOWED_TAGS = set(AI_EXPERTISE_TAGS)


def _clean_text(value: str | None) -> str | None:
  if value is None:
    return None
  stripped = value.strip()
  return stripped or None


def _validate_expertise_tags(tags: list[str]) -> list[str]:
  normalized: list[str] = []
  seen: set[str] = set()
  invalid: list[str] = []
  for tag in tags:
    if tag not in _ALLOWED_TAGS:
      invalid.append(tag)
      continue
    if tag in seen:
      continue
    normalized.append(tag)
    seen.add(tag)
  if invalid:
    raise HTTPException(
      status.HTTP_400_BAD_REQUEST,
      detail={"message": "Invalid expertise tags", "invalidTags": invalid},
    )
  return normalized


def _to_private_user(user: User, *, username_editable: bool) -> PrivateUserProfile:
  return PrivateUserProfile(
    id=user.id,
    email=user.email,
    username=user.username,
    display_name=user.display_name,
    avatar_url=user.avatar_url,
    bio=user.bio,
    company=user.company,
    location=user.location,
    expertise_tags=list(user.expertise_tags or []),
    created_at=user.created_at,
    updated_at=user.updated_at,
    username_editable=username_editable,
    github_username=user.github_username,
  )


def _to_public_user(user: User) -> PublicUserProfile:
  return PublicUserProfile(
    id=user.id,
    username=user.username,
    display_name=user.display_name,
    avatar_url=user.avatar_url,
    bio=user.bio,
    company=user.company,
    location=user.location,
    expertise_tags=list(user.expertise_tags or []),
    created_at=user.created_at,
    updated_at=user.updated_at,
  )


@router.get("/me", response_model=PrivateUserProfile)
async def get_my_profile(
  current_user: Annotated[User, Depends(get_current_user)],
  session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PrivateUserProfile:
  username_editable = await is_username_generated_from_email(session, current_user)
  return _to_private_user(current_user, username_editable=username_editable)


@router.patch("/me", response_model=PrivateUserProfile)
async def update_my_profile(
  payload: UserProfileUpdatePayload,
  current_user: Annotated[User, Depends(get_current_user)],
  session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PrivateUserProfile:
  mutated = False
  username_editable = await is_username_generated_from_email(session, current_user)

  if payload.display_name is not None:
    cleaned = _clean_text(payload.display_name)
    if cleaned != current_user.display_name:
      current_user.display_name = cleaned
      mutated = True

  if payload.bio is not None:
    cleaned = _clean_text(payload.bio)
    if cleaned != current_user.bio:
      current_user.bio = cleaned
      mutated = True

  if payload.company is not None:
    cleaned = _clean_text(payload.company)
    if cleaned != current_user.company:
      current_user.company = cleaned
      mutated = True

  if payload.location is not None:
    cleaned = _clean_text(payload.location)
    if cleaned != current_user.location:
      current_user.location = cleaned
      mutated = True

  if payload.expertise_tags is not None:
    normalized_tags = _validate_expertise_tags(payload.expertise_tags)
    if normalized_tags != list(current_user.expertise_tags or []):
      current_user.expertise_tags = normalized_tags
      mutated = True

  if payload.username is not None:
    try:
      normalized_username = normalize_username(payload.username)
    except UsernameValidationError as exc:
      raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if normalized_username != current_user.username:
      if not username_editable:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Username can only be set once")

      existing = await session.scalar(
        select(User.id).where(User.username == normalized_username, User.id != current_user.id).limit(1)
      )
      if existing is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Username is already taken")

      current_user.username = normalized_username
      username_editable = False
      mutated = True

  if mutated:
    current_user.updated_at = datetime.now(tz=UTC)
    await session.commit()
    await session.refresh(current_user)

  if username_editable and mutated:
    username_editable = await is_username_generated_from_email(session, current_user)

  return _to_private_user(current_user, username_editable=username_editable)


@router.get("/{username}", response_model=PublicUserProfile)
async def get_public_profile(
  username: str,
  session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PublicUserProfile:
  try:
    normalized = normalize_username(username)
  except UsernameValidationError:
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

  user = await session.scalar(select(User).where(User.username == normalized))
  if user is None:
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

  return _to_public_user(user)


@router.get("", response_model=list[PublicUserProfile])
async def list_users(
  session: Annotated[AsyncSession, Depends(get_db_session)],
  q: str | None = Query(default=None, min_length=2, description="Search by username or display name"),
  tag: str | None = Query(default=None, description="Filter by expertise tag"),
  limit: int = Query(default=20, ge=1, le=50),
  offset: int = Query(default=0, ge=0),
) -> list[PublicUserProfile]:
  stmt = select(User).order_by(User.created_at.desc())

  if q:
    pattern = f"%{q.lower()}%"
    stmt = stmt.where(
      func.lower(User.username).like(pattern) | func.lower(func.coalesce(User.display_name, "")).like(pattern)
    )

  if tag and tag not in _ALLOWED_TAGS:
    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid expertise tag filter")

  users = (await session.scalars(stmt)).all()
  if tag:
    users = [user for user in users if tag in (user.expertise_tags or [])]

  window = users[offset : offset + limit]
  return [_to_public_user(user) for user in window]
