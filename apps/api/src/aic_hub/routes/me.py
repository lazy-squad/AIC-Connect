from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import AI_TAGS
from ..db import get_db_session
from ..dependencies import get_current_user
from ..models import User
from ..schemas import PublicUser, UserProfileUpdate

router = APIRouter()


def _to_public_user(user: User) -> PublicUser:
  return PublicUser(
    id=user.id,
    email=user.email,
    displayName=user.display_name,
    username=user.username,
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


@router.get("/me", summary="Current user", response_model=PublicUser)
async def current_user(user: Annotated[User, Depends(get_current_user)]) -> PublicUser:
  """Get current authenticated user's complete profile."""
  return _to_public_user(user)


@router.patch("/me", summary="Update profile", response_model=PublicUser)
async def update_profile(
  updates: UserProfileUpdate,
  user: Annotated[User, Depends(get_current_user)],
  session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PublicUser:
  """Update current user's profile."""

  # Validate expertise tags if provided
  if updates.expertise_tags is not None:
    if len(updates.expertise_tags) > 10:
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Maximum 10 expertise tags allowed"
      )

    invalid_tags = [tag for tag in updates.expertise_tags if tag not in AI_TAGS]
    if invalid_tags:
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid tags: {invalid_tags}. Must be from predefined list."
      )

  # Update user fields
  update_data = updates.model_dump(exclude_unset=True, by_alias=False)
  for field, value in update_data.items():
    if hasattr(user, field):
      setattr(user, field, value)

  session.add(user)
  await session.commit()
  await session.refresh(user)

  return _to_public_user(user)
