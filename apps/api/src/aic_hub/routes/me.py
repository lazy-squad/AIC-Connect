from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from ..dependencies import get_current_user
from ..models import User
from ..schemas import PublicUser

router = APIRouter()


def _to_public_user(user: User) -> PublicUser:
  return PublicUser(id=user.id, email=user.email, displayName=user.display_name)


@router.get("/me", summary="Current user", response_model=PublicUser)
async def current_user(user: Annotated[User, Depends(get_current_user)]) -> PublicUser:
  return _to_public_user(user)
