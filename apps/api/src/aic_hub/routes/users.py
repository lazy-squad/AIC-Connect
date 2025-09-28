from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db_session
from ..dependencies import get_current_user_optional
from ..models import User
from ..schemas import (
  UsernameCheck,
  UsernameCheckResponse,
  UserPublicProfile,
  UserSearchResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


def _to_public_profile(user: User) -> UserPublicProfile:
  """Convert User model to public profile (no email)."""
  return UserPublicProfile(
    id=user.id,
    username=user.username,
    displayName=user.display_name,
    avatarUrl=user.avatar_url,
    bio=user.bio,
    company=user.company,
    location=user.location,
    expertiseTags=user.expertise_tags or [],
    githubUsername=user.github_username,
    createdAt=user.created_at,
    articleCount=0,  # TODO: Count actual articles when articles are implemented
    spaceCount=0,    # TODO: Count actual spaces when spaces are implemented
  )


@router.get("/{username}", summary="Get user profile", response_model=UserPublicProfile)
async def get_user_profile(
  username: str,
  session: Annotated[AsyncSession, Depends(get_db_session)],
  current_user: Annotated[User | None, Depends(get_current_user_optional)] = None,
) -> UserPublicProfile:
  """Get public user profile by username."""
  user = await session.scalar(select(User).where(User.username == username))

  if not user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="User not found"
    )

  return _to_public_profile(user)


@router.get("", summary="Search users", response_model=UserSearchResponse)
async def search_users(
  session: Annotated[AsyncSession, Depends(get_db_session)],
  q: str | None = Query(default=None, description="Search query"),
  expertise: list[str] | None = Query(default=None, description="Filter by expertise tags"),
  skip: int = Query(default=0, ge=0, description="Pagination offset"),
  limit: int = Query(default=20, ge=1, le=100, description="Page size"),
  current_user: Annotated[User | None, Depends(get_current_user_optional)] = None,
) -> UserSearchResponse:
  """Search and list users with optional filters."""

  query = select(User).where(User.username.isnot(None))

  # Apply text search if provided
  if q:
    search_filter = or_(
      User.username.ilike(f"%{q}%"),
      User.display_name.ilike(f"%{q}%"),
      User.bio.ilike(f"%{q}%"),
    )
    query = query.where(search_filter)

  # Apply expertise filter if provided
  if expertise:
    # Use PostgreSQL array overlap operator
    query = query.where(User.expertise_tags.op("&&")(expertise))

  # Get total count
  count_query = select(func.count()).select_from(query.subquery())
  total = await session.scalar(count_query) or 0

  # Apply pagination and ordering
  query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)

  # Execute query
  result = await session.execute(query)
  users = result.scalars().all()

  return UserSearchResponse(
    users=[_to_public_profile(user) for user in users],
    total=total,
    skip=skip,
    limit=limit,
  )


@router.post("/check-username", summary="Check username availability", response_model=UsernameCheckResponse)
async def check_username(
  payload: UsernameCheck,
  session: Annotated[AsyncSession, Depends(get_db_session)],
  current_user: Annotated[User | None, Depends(get_current_user_optional)] = None,
) -> UsernameCheckResponse:
  """Check if username is available."""

  # Check if username is already taken
  existing = await session.scalar(
    select(User).where(User.username == payload.username)
  )

  if existing:
    # Generate suggestion by appending numbers
    base_username = payload.username
    counter = 1
    suggestion = None

    for i in range(1, 100):  # Try up to 99 variations
      candidate = f"{base_username}{i}"
      existing_candidate = await session.scalar(
        select(User).where(User.username == candidate)
      )
      if not existing_candidate:
        suggestion = candidate
        break

    return UsernameCheckResponse(available=False, suggestion=suggestion)

  return UsernameCheckResponse(available=True, suggestion=None)