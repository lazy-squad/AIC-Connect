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
from ..schemas import PublicUser

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


async def _generate_unique_username(session: AsyncSession, preferred_username: str) -> str:
  """Generate a unique username by appending numbers if needed."""
  base_username = preferred_username
  counter = 1

  while True:
    # Check if username is available
    existing = await session.scalar(select(User).where(User.username == preferred_username))
    if not existing:
      return preferred_username

    # Try with a number suffix
    preferred_username = f"{base_username}{counter}"
    counter += 1

    # Safety limit to prevent infinite loops
    if counter > 1000:
      import secrets
      preferred_username = f"{base_username}_{secrets.token_hex(4)}"
      break

  return preferred_username


def _populate_github_profile_data(user: User, profile) -> None:
  """Populate user with GitHub profile data if not already set."""
  # Always update GitHub username
  user.github_username = profile.login

  # Set username if not already set (use GitHub login as default)
  if not user.username:
    user.username = profile.login  # Will be made unique in the callback

  # Update other fields if not set or if they're from GitHub
  if not user.avatar_url:
    user.avatar_url = profile.avatar_url

  if not user.bio:
    user.bio = profile.bio

  if not user.company:
    user.company = profile.company

  if not user.location:
    user.location = profile.location


@router.post("/signup", response_model=PublicUser, status_code=status.HTTP_201_CREATED)
async def signup(
  payload: SignupPayload,
  request: Request,
  response: Response,
  session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PublicUser:
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
  user = User(email=email, password_hash=password_hash, display_name=payload.display_name.strip() if payload.display_name else None)
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
  return _to_public_user(user)


@router.post("/login", response_model=PublicUser)
async def login(
  payload: LoginPayload,
  request: Request,
  response: Response,
  session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PublicUser:
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
  return _to_public_user(user)


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
      unique_username = await _generate_unique_username(session, profile.login)
      user = User(
        email=normalized_email,
        password_hash=None,
        display_name=display_name,
        username=unique_username,
        github_username=profile.login,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        company=profile.company,
        location=profile.location,
        expertise_tags=[]
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

  # Update existing user with latest GitHub data
  _populate_github_profile_data(user, profile)

  # Ensure username is unique if it was updated
  if user.username and user.username == profile.login:
    user.username = await _generate_unique_username(session, profile.login)

  user.last_login = datetime.now(tz=UTC)
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
