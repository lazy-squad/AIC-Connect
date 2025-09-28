from __future__ import annotations

import re
import unicodedata
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 32
USERNAME_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{1,30})[a-z0-9]$")


class UsernameValidationError(ValueError):
  """Raised when a username candidate is invalid."""


def _basic_slugify(value: str) -> str:
  normalized = unicodedata.normalize("NFKD", value)
  ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
  lowered = ascii_only.lower()
  sanitized = re.sub(r"[^a-z0-9-]", "-", lowered)
  sanitized = re.sub(r"-+", "-", sanitized).strip("-")
  if not sanitized:
    sanitized = "user"
  if len(sanitized) < USERNAME_MIN_LENGTH:
    sanitized = (sanitized + ("x" * USERNAME_MIN_LENGTH))[:USERNAME_MIN_LENGTH]
  return sanitized[:USERNAME_MAX_LENGTH]


def normalize_username(value: str) -> str:
  candidate = _basic_slugify(value.strip())
  if not USERNAME_PATTERN.fullmatch(candidate):
    raise UsernameValidationError("Username must be 3-32 characters of lowercase letters, numbers, or hyphens")
  return candidate


def _apply_suffix(base: str, suffix: int) -> str:
  suffix_str = f"-{suffix}"
  allowed_length = USERNAME_MAX_LENGTH - len(suffix_str)
  trimmed_base = base[:allowed_length].rstrip("-")
  if not trimmed_base:
    trimmed_base = base[:allowed_length]
  candidate = f"{trimmed_base}{suffix_str}"
  if len(candidate) < USERNAME_MIN_LENGTH:
    candidate = (candidate + ("x" * USERNAME_MIN_LENGTH))[:USERNAME_MIN_LENGTH]
  if not USERNAME_PATTERN.fullmatch(candidate):
    raise UsernameValidationError("Generated username does not meet format requirements")
  return candidate


async def generate_unique_username(
  session: AsyncSession,
  email: str,
  *,
  exclude_user_id: UUID | None = None,
) -> str:
  local_part = email.split("@", 1)[0]
  base = normalize_username(local_part)
  candidate = base
  suffix = 1
  while True:
    stmt = select(User.id).where(User.username == candidate)
    if exclude_user_id:
      stmt = stmt.where(User.id != exclude_user_id)
    exists = await session.scalar(stmt.limit(1))
    if exists is None:
      return candidate
    candidate = _apply_suffix(base, suffix)
    suffix += 1


async def is_username_generated_from_email(session: AsyncSession, user: User) -> bool:
  expected = await generate_unique_username(session, user.email, exclude_user_id=user.id)
  return expected == user.username
