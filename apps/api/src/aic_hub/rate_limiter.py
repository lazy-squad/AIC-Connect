from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import AuthAction, AuthAttempt


@dataclass(frozen=True)
class RateLimitRule:
  limit: int
  window: timedelta


class RateLimitExceeded(Exception):
  def __init__(self, scope: str) -> None:
    super().__init__(f"Rate limit exceeded for {scope}")
    self.scope = scope


class AuthRateLimiter:
  _rules: dict[AuthAction, dict[str, RateLimitRule]]

  def __init__(self) -> None:
    window = timedelta(minutes=15)
    self._rules = {
      AuthAction.SIGNUP: {
        "email": RateLimitRule(limit=5, window=window),
        "ip": RateLimitRule(limit=5, window=window),
      },
      AuthAction.LOGIN: {
        "email": RateLimitRule(limit=10, window=window),
        "ip": RateLimitRule(limit=10, window=window),
      },
    }

  async def assert_within_limits(
    self,
    session: AsyncSession,
    action: AuthAction,
    *,
    email_hash: str | None,
    ip_address: str | None,
  ) -> None:
    now = datetime.now(tz=UTC)
    rules = self._rules[action]

    async def _count(scope: str, value: str | None) -> int:
      if value is None:
        return 0
      window_start = now - rules[scope].window
      column = AuthAttempt.email_hash if scope == "email" else AuthAttempt.ip_address
      statement = (
        select(func.count())
        .select_from(AuthAttempt)
        .where(
          AuthAttempt.action == action,
          column == value,
          AuthAttempt.created_at >= window_start,
        )
      )
      count = await session.scalar(statement)
      return int(count or 0)

    if email_hash is not None and await _count("email", email_hash) >= rules["email"].limit:
      raise RateLimitExceeded("email")
    if ip_address is not None and await _count("ip", ip_address) >= rules["ip"].limit:
      raise RateLimitExceeded("ip")

  async def record_attempt(
    self,
    session: AsyncSession,
    *,
    action: AuthAction,
    email_hash: str | None,
    ip_address: str | None,
    success: bool,
    reason: str | None,
  ) -> None:
    attempt = AuthAttempt(
      action=action,
      email_hash=email_hash,
      ip_address=ip_address,
      success=success,
      reason=reason,
    )
    session.add(attempt)
    await session.flush()


rate_limiter = AuthRateLimiter()
