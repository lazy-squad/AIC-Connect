from __future__ import annotations

import logging
import secrets
from datetime import UTC, datetime
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import get_db_session
from ..github import github_oauth_client
from ..models import AuthAction, OAuthAccount, OAuthProvider, User
from ..rate_limiter import RateLimitExceeded, rate_limiter
from ..security import (
  constant_time_compare,
  generate_request_id,
  hash_email,
  hash_password,
  normalize_email,
  session_tokens,
  verify_password,
)
from ..schemas import PrivateUserProfile
from ..usernames import generate_unique_username, is_username_generated_from_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

INVALID_CREDENTIALS = "Invalid credentials"
SIGNUP_GENERIC_ERROR = "Unable to complete signup"
RATE_LIMIT_ERROR = "Too many attempts. Please try again later"
STATE_COOKIE_NAME = "aic_hub_oauth_state"
STATE_MAX_AGE_SECONDS = 600

_state_serializer = URLSafeTimedSerializer(settings.secret_key.get_secret_value(), salt="aic-hub-oauth-state")


class SignupPayload(BaseModel):
  model_config = ConfigDict(populate_by_name=True)

  email: EmailStr
  password: SecretStr
  display_name: str | None = Field(default=None, alias="displayName")


class LoginPayload(BaseModel):
  email: EmailStr
  password: SecretStr


def _password_strength_ok(password: str) -> bool:
  if len(password) < settings.password_min_length:
    return False
  has_alpha = any(ch.isalpha() for ch in password)
  has_digit = any(ch.isdigit() for ch in password)
  return has_alpha and has_digit


def _ensure_request_id(request: Request) -> str:
  request_id = getattr(request.state, "request_id", None)
  if request_id is None:
    request_id = request.headers.get("x-request-id") or generate_request_id()
    request.state.request_id = request_id
  return request_id


def _client_ip(request: Request) -> str | None:
  return request.client.host if request.client else None


def _set_session_cookie(response: Response, token: str) -> None:
  cookie_settings = settings.session_cookie_kwargs
  response.set_cookie(settings.session_cookie.name, token, **cookie_settings)
  response.headers["Cache-Control"] = "no-store"


def _clear_session_cookie(response: Response) -> None:
  response.delete_cookie(
    settings.session_cookie.name,
    path="/",
    samesite=settings.session_cookie.same_site,
    secure=settings.session_cookie.secure,
    domain=None,
  )
  response.headers["Cache-Control"] = "no-store"


def _encode_state(state: str) -> str:
  return _state_serializer.dumps({"state": state})


def _decode_state(raw: str) -> str:
  data = _state_serializer.loads(raw, max_age=STATE_MAX_AGE_SECONDS)
  return data["state"]


async def _to_private_user(session: AsyncSession, user: User) -> PrivateUserProfile:
  username_editable = await is_username_generated_from_email(session, user)
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


@router.post("/signup", response_model=PrivateUserProfile, status_code=status.HTTP_201_CREATED)
async def signup(
  payload: SignupPayload,
  request: Request,
  response: Response,
  session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PrivateUserProfile:
  request_id = _ensure_request_id(request)
  email = normalize_email(payload.email)
  email_hash = hash_email(email)
  client_ip = _client_ip(request)
  password = payload.password.get_secret_value()

  logger.info(
    "signup_attempt",
    extra={"event": "signup_attempt", "request_id": request_id, "email_hash": email_hash, "ip": client_ip},
  )

  if not _password_strength_ok(password):
    logger.warning(
      "signup_fail",
      extra={
        "event": "signup_fail",
        "request_id": request_id,
        "email_hash": email_hash,
        "ip": client_ip,
        "reason": "weak_password",
      },
    )
    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=SIGNUP_GENERIC_ERROR)

  try:
    await rate_limiter.assert_within_limits(
      session,
      AuthAction.SIGNUP,
      email_hash=email_hash,
      ip_address=client_ip,
    )
  except RateLimitExceeded as exc:
    await rate_limiter.record_attempt(
      session,
      action=AuthAction.SIGNUP,
      email_hash=email_hash,
      ip_address=client_ip,
      success=False,
      reason=f"rate_limit_{exc.scope}",
    )
    await session.commit()
    logger.warning(
      "signup_fail",
      extra={
        "event": "signup_fail",
        "request_id": request_id,
        "email_hash": email_hash,
        "ip": client_ip,
        "reason": f"rate_limit_{exc.scope}",
      },
    )
    raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail=RATE_LIMIT_ERROR)

  existing = await session.scalar(select(User).where(User.email == email))
  if existing is not None:
    await rate_limiter.record_attempt(
      session,
      action=AuthAction.SIGNUP,
      email_hash=email_hash,
      ip_address=client_ip,
      success=False,
      reason="duplicate_email",
    )
    await session.commit()
    logger.warning(
      "signup_fail",
      extra={
        "event": "signup_fail",
        "request_id": request_id,
        "email_hash": email_hash,
        "ip": client_ip,
        "reason": "duplicate_email",
      },
    )
    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=SIGNUP_GENERIC_ERROR)

  password_hash = hash_password(password)
  generated_username = await generate_unique_username(session, email)
  user = User(
    email=email,
    password_hash=password_hash,
    display_name=payload.display_name.strip() if payload.display_name else None,
    username=generated_username,
  )
  session.add(user)
  await session.flush()

  token, _ = session_tokens.issue(user.id)
  user.last_login = datetime.now(tz=UTC)

  await rate_limiter.record_attempt(
    session,
    action=AuthAction.SIGNUP,
    email_hash=email_hash,
    ip_address=client_ip,
    success=True,
    reason="created",
  )
  await session.commit()

  logger.info(
    "signup_success",
    extra={"event": "signup_success", "request_id": request_id, "email_hash": email_hash, "ip": client_ip},
  )

  _set_session_cookie(response, token)
  await session.refresh(user)
  return await _to_private_user(session, user)


@router.post("/login", response_model=PrivateUserProfile)
async def login(
  payload: LoginPayload,
  request: Request,
  response: Response,
  session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PrivateUserProfile:
  request_id = _ensure_request_id(request)
  email = normalize_email(payload.email)
  email_hash = hash_email(email)
  client_ip = _client_ip(request)
  password = payload.password.get_secret_value()

  logger.info(
    "login_attempt",
    extra={"event": "login_attempt", "request_id": request_id, "email_hash": email_hash, "ip": client_ip},
  )

  try:
    await rate_limiter.assert_within_limits(
      session,
      AuthAction.LOGIN,
      email_hash=email_hash,
      ip_address=client_ip,
    )
  except RateLimitExceeded as exc:
    await rate_limiter.record_attempt(
      session,
      action=AuthAction.LOGIN,
      email_hash=email_hash,
      ip_address=client_ip,
      success=False,
      reason=f"rate_limit_{exc.scope}",
    )
    await session.commit()
    logger.warning(
      "login_fail",
      extra={
        "event": "login_fail",
        "request_id": request_id,
        "email_hash": email_hash,
        "ip": client_ip,
        "reason": f"rate_limit_{exc.scope}",
      },
    )
    raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail=RATE_LIMIT_ERROR)

  user = await session.scalar(select(User).where(User.email == email))
  if user is None or user.password_hash is None or not verify_password(user.password_hash, password):
    await rate_limiter.record_attempt(
      session,
      action=AuthAction.LOGIN,
      email_hash=email_hash,
      ip_address=client_ip,
      success=False,
      reason="invalid_credentials",
    )
    await session.commit()
    logger.warning(
      "login_fail",
      extra={
        "event": "login_fail",
        "request_id": request_id,
        "email_hash": email_hash,
        "ip": client_ip,
        "reason": "invalid_credentials",
      },
    )
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)

  user.last_login = datetime.now(tz=UTC)
  token, _ = session_tokens.issue(user.id)

  await rate_limiter.record_attempt(
    session,
    action=AuthAction.LOGIN,
    email_hash=email_hash,
    ip_address=client_ip,
    success=True,
    reason="authenticated",
  )
  await session.commit()

  logger.info(
    "login_success",
    extra={"event": "login_success", "request_id": request_id, "email_hash": email_hash, "ip": client_ip},
  )

  _set_session_cookie(response, token)
  await session.refresh(user)
  return await _to_private_user(session, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> Response:
  _clear_session_cookie(response)
  response.status_code = status.HTTP_204_NO_CONTENT
  return response


@router.get("/login/github")
async def github_login(request: Request) -> RedirectResponse:
  request_id = _ensure_request_id(request)
  state_value = secrets.token_urlsafe(16)
  signed_state = _encode_state(state_value)
  try:
    authorize_url = github_oauth_client.build_authorize_url(state_value)
  except RuntimeError as exc:
    logger.error(
      "oauth_error",
      extra={"event": "oauth_error", "request_id": request_id, "reason": "configuration", "detail": str(exc)},
    )
    raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail="GitHub OAuth is not configured")

  response = RedirectResponse(url=authorize_url, status_code=status.HTTP_302_FOUND)
  response.set_cookie(
    STATE_COOKIE_NAME,
    signed_state,
    max_age=STATE_MAX_AGE_SECONDS,
    httponly=True,
    secure=settings.session_cookie.secure,
    samesite="lax",
    path="/api/auth",
  )
  return response


@router.get("/callback/github")
async def github_callback(
  request: Request,
  session: Annotated[AsyncSession, Depends(get_db_session)],
  code: str | None = None,
  state: str | None = None,
) -> RedirectResponse:
  request_id = _ensure_request_id(request)
  client_ip = _client_ip(request)
  if not code or not state:
    logger.warning(
      "oauth_error",
      extra={"event": "oauth_error", "request_id": request_id, "ip": client_ip, "reason": "missing_params"},
    )
    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth callback")

  state_cookie = request.cookies.get(STATE_COOKIE_NAME)
  if not state_cookie:
    logger.warning(
      "oauth_error",
      extra={"event": "oauth_error", "request_id": request_id, "ip": client_ip, "reason": "missing_state_cookie"},
    )
    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")

  try:
    expected_state = _decode_state(state_cookie)
  except (BadSignature, BadTimeSignature):
    logger.warning(
      "oauth_error",
      extra={"event": "oauth_error", "request_id": request_id, "ip": client_ip, "reason": "invalid_state_cookie"},
    )
    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")

  if not constant_time_compare(expected_state, state):
    logger.warning(
      "oauth_error",
      extra={"event": "oauth_error", "request_id": request_id, "ip": client_ip, "reason": "state_mismatch"},
    )
    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")

  try:
    token = await github_oauth_client.exchange_code(code)
    profile = await github_oauth_client.fetch_profile(token)
  except (RuntimeError, httpx.HTTPError) as exc:
    logger.exception(
      "oauth_error",
      extra={"event": "oauth_error", "request_id": request_id, "ip": client_ip, "reason": "github_request"},
    )
    raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail="GitHub authentication failed") from exc

  normalized_email = normalize_email(profile.email)
  email_hash = hash_email(normalized_email)
  logger.info(
    "oauth_callback",
    extra={
      "event": "oauth_callback",
      "request_id": request_id,
      "ip": client_ip,
      "email_hash": email_hash,
      "provider": "github",
      "provider_account_id": profile.id,
    },
  )

  oauth_account = await session.scalar(
    select(OAuthAccount).where(
      OAuthAccount.provider == OAuthProvider.GITHUB,
      OAuthAccount.provider_account_id == profile.id,
    )
  )

  if oauth_account:
    user = oauth_account.user
    action = "oauth_linked"
  else:
    user = await session.scalar(select(User).where(User.email == normalized_email))
    if user:
      oauth_account = OAuthAccount(
        user_id=user.id,
        provider=OAuthProvider.GITHUB,
        provider_account_id=profile.id,
      )
      session.add(oauth_account)
      action = "oauth_linked"
    else:
      display_name = profile.name or profile.login
      generated_username = await generate_unique_username(session, normalized_email)
      user = User(
        email=normalized_email,
        password_hash=None,
        display_name=display_name,
        username=generated_username,
        github_username=profile.login,
        avatar_url=profile.avatar_url,
      )
      session.add(user)
      await session.flush()
      oauth_account = OAuthAccount(
        user_id=user.id,
        provider=OAuthProvider.GITHUB,
        provider_account_id=profile.id,
      )
      session.add(oauth_account)
      action = "oauth_created"

  # Update GitHub-linked profile data on each callback.
  profile_mutated = False
  if profile.login and user.github_username != profile.login:
    user.github_username = profile.login
    profile_mutated = True
  if profile.avatar_url and user.avatar_url != profile.avatar_url:
    user.avatar_url = profile.avatar_url
    profile_mutated = True
  if profile.name and not user.display_name:
    user.display_name = profile.name
    profile_mutated = True

  user.last_login = datetime.now(tz=UTC)
  if profile_mutated:
    user.updated_at = datetime.now(tz=UTC)
  await session.flush()
  await session.commit()

  logger.info(
    action,
    extra={
      "event": action,
      "request_id": request_id,
      "ip": client_ip,
      "email_hash": email_hash,
      "provider_account_id": profile.id,
    },
  )

  redirect_url = f"{str(settings.web_base_url).rstrip('/')}/welcome"
  redirect = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
  session_token, _ = session_tokens.issue(user.id)
  _set_session_cookie(redirect, session_token)
  redirect.delete_cookie(
    STATE_COOKIE_NAME,
    path="/api/auth",
    httponly=True,
    secure=settings.session_cookie.secure,
    samesite="lax",
    domain=None,
  )
  return redirect
