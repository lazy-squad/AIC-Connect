from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import get_db_session
from .models import User
from .security import session_tokens


async def get_current_user(
  request: Request,
  session: AsyncSession = Depends(get_db_session),
) -> User:
  token = request.cookies.get(settings.session_cookie.name)
  if not token:
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

  claims = session_tokens.verify(token)
  if claims is None:
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

  user = await session.get(User, claims.user_id)
  if user is None:
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

  return user
