from __future__ import annotations

import hmac
import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer

from .config import settings


# Tune Argon2id parameters for API runtime. Memory cost ~64MB keeps brute force expensive
# while remaining reasonable for the FastAPI worker footprint. Expose overrides via env by
# respecting standard PasswordHasher keyword defaults if parameters are provided later.
_password_hasher = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=1)


def normalize_email(email: str) -> str:
  return email.strip().lower()


def hash_email(email: str) -> str:
  normalized = normalize_email(email)
  return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def generate_request_id() -> str:
  return uuid.uuid4().hex


def constant_time_compare(val_a: str | bytes, val_b: str | bytes) -> bool:
  if isinstance(val_a, str):
    val_a = val_a.encode("utf-8")
  if isinstance(val_b, str):
    val_b = val_b.encode("utf-8")
  return hmac.compare_digest(val_a, val_b)


def hash_password(password: str) -> str:
  return _password_hasher.hash(password)


def verify_password(stored_hash: str, password: str) -> bool:
  try:
    return _password_hasher.verify(stored_hash, password)
  except VerifyMismatchError:
    return False


@dataclass(slots=True)
class SessionClaims:
  user_id: uuid.UUID
  issued_at: datetime
  expires_at: datetime


class SessionTokenManager:
  def __init__(self) -> None:
    secret = settings.secret_key.get_secret_value()
    self._serializer = URLSafeTimedSerializer(secret_key=secret, salt="aic-hub-session")
    self._max_age_seconds = settings.session_cookie.max_age_seconds

  def _serialize_payload(self, payload: dict[str, Any]) -> str:
    return self._serializer.dumps(payload)

  def _deserialize_payload(self, token: str) -> dict[str, Any]:
    return self._serializer.loads(token, max_age=self._max_age_seconds)

  def issue(self, user_id: uuid.UUID) -> tuple[str, SessionClaims]:
    issued_at = datetime.now(tz=UTC)
    expires_at = issued_at + timedelta(seconds=self._max_age_seconds)
    payload = {
      "user_id": str(user_id),
      "iat": int(issued_at.timestamp()),
      "exp": int(expires_at.timestamp()),
      "nonce": secrets.token_urlsafe(8),
    }
    token = self._serialize_payload(payload)
    claims = SessionClaims(user_id=user_id, issued_at=issued_at, expires_at=expires_at)
    return token, claims

  def verify(self, token: str) -> SessionClaims | None:
    try:
      payload = self._deserialize_payload(token)
    except (BadSignature, BadTimeSignature):
      return None

    issued_at = datetime.fromtimestamp(payload["iat"], tz=UTC)
    expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)
    if expires_at < datetime.now(tz=UTC):
      return None

    return SessionClaims(user_id=uuid.UUID(payload["user_id"]), issued_at=issued_at, expires_at=expires_at)


def session_token_manager() -> SessionTokenManager:
  return SessionTokenManager()


session_tokens = session_token_manager()
