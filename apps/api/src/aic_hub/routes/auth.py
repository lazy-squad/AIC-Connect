from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


class EmailMagicLinkRequest(BaseModel):
  email: EmailStr


def _not_implemented(action: str) -> JSONResponse:
  return JSONResponse(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    content={
      "detail": f"{action} is not implemented yet.",
      "sessionCookie": {
        "name": settings.session_cookie.name,
        "httpOnly": settings.session_cookie.http_only,
        "secure": settings.session_cookie.secure,
        "sameSite": settings.session_cookie.same_site,
      },
    },
  )


@router.get("/login/github")
async def github_login() -> JSONResponse:
  return _not_implemented("GitHub OAuth login")


@router.get("/callback/github")
async def github_callback(
  code: Annotated[str | None, Query()] = None,
  state: Annotated[str | None, Query()] = None,
) -> JSONResponse:
  logger.info("Received GitHub callback with code=%s state=%s", code, state)
  return _not_implemented("GitHub OAuth callback")


@router.post("/email/request")
async def request_email_link(payload: EmailMagicLinkRequest) -> JSONResponse:
  logger.info("Magic link requested for %s", payload.email)
  return _not_implemented("Email magic link request")


@router.get("/email/verify")
async def verify_email(token: Annotated[str | None, Query()] = None) -> JSONResponse:
  logger.info("Magic link verification attempted token=%s", token)
  return _not_implemented("Email magic link verification")
