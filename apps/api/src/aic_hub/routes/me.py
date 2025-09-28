from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/me", summary="Current user")
async def current_user() -> None:
  raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
