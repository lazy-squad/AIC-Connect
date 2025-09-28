from __future__ import annotations

import uuid

from aic_hub.security import hash_password, normalize_email, session_tokens, verify_password


def test_password_hash_roundtrip() -> None:
  password = "Str0ngPassw0rd"
  hashed = hash_password(password)

  assert hashed != password
  assert verify_password(hashed, password)
  assert not verify_password(hashed, "WrongPass123")


def test_email_normalization() -> None:
  assert normalize_email("  User@Example.COM ") == "user@example.com"


def test_session_token_issue_and_verify() -> None:
  token, claims = session_tokens.issue(uuid.uuid4())
  verified = session_tokens.verify(token)

  assert verified is not None
  assert verified.user_id == claims.user_id
  assert verified.expires_at > verified.issued_at
