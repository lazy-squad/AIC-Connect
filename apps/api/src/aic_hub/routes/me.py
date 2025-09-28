from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db_session
from ..dependencies import get_current_user
from ..models import User
from ..schemas import PrivateUserProfile
from . import users as users_routes

router = APIRouter()


@router.get("/me", summary="Current user", response_model=PrivateUserProfile)
async def current_user(
  user: Annotated[User, Depends(get_current_user)],
  session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PrivateUserProfile:
  return await users_routes.get_my_profile(current_user=user, session=session)

