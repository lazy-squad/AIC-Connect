from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from aic_hub.config import settings
from aic_hub.github import GitHubProfile, GitHubOAuthClient, github_oauth_client
from aic_hub.models import AuthAttempt, OAuthAccount, OAuthProvider, User
from aic_hub.routes import auth as auth_routes
from aic_hub.security import hash_password


@pytest.mark.asyncio
async def test_signup_and_me_flow(client: AsyncClient, session: AsyncSession) -> None:
  response = await client.post(
    "/auth/signup",
    json={"email": "signup@example.com", "password": "Sup3rSecure!", "displayName": "Sign Up"},
  )
  assert response.status_code == 201
  payload = response.json()
  assert payload["email"] == "signup@example.com"
  assert payload["displayName"] == "Sign Up"
  assert client.cookies.get(settings.session_cookie.name) is not None

  me_response = await client.get("/me")
  assert me_response.status_code == 200
  me_payload = me_response.json()
  assert me_payload["email"] == "signup@example.com"

  # Ensure database user exists
  user_count = await session.scalar(select(func.count()).select_from(User))
  assert user_count == 1


@pytest.mark.asyncio
async def test_duplicate_signup_rejected(client: AsyncClient, session: AsyncSession) -> None:
  await client.post(
    "/auth/signup",
    json={"email": "dup@example.com", "password": "Sup3rSecure!", "displayName": "First"},
  )
  duplicate = await client.post(
    "/auth/signup",
    json={"email": "dup@example.com", "password": "Sup3rSecure!", "displayName": "Second"},
  )
  assert duplicate.status_code == 400
  assert duplicate.json()["detail"] == auth_routes.SIGNUP_GENERIC_ERROR

  user_count = await session.scalar(select(func.count()).select_from(User))
  assert user_count == 1


@pytest.mark.asyncio
async def test_login_success_and_logout(client: AsyncClient) -> None:
  await client.post(
    "/auth/signup",
    json={"email": "login@example.com", "password": "Sup3rSecure!", "displayName": "New"},
  )

  await client.post("/auth/logout")
  assert client.cookies.get(settings.session_cookie.name) is None

  login_response = await client.post(
    "/auth/login",
    json={"email": "login@example.com", "password": "Sup3rSecure!"},
  )
  assert login_response.status_code == 200
  assert login_response.json()["email"] == "login@example.com"
  assert client.cookies.get(settings.session_cookie.name) is not None

  logout_response = await client.post("/auth/logout")
  assert logout_response.status_code == 204
  assert client.cookies.get(settings.session_cookie.name) is None

  me_after_logout = await client.get("/me")
  assert me_after_logout.status_code == 401


@pytest.mark.asyncio
async def test_login_rate_limit_after_failed_attempts(client: AsyncClient, session: AsyncSession) -> None:
  # Intentionally using a non-existent account to trigger failures and rate limiting
  for _ in range(10):
    response = await client.post(
      "/auth/login",
      json={"email": "ratelimit@example.com", "password": "WrongPass1"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == auth_routes.INVALID_CREDENTIALS

  rate_limited = await client.post(
    "/auth/login",
    json={"email": "ratelimit@example.com", "password": "WrongPass1"},
  )
  assert rate_limited.status_code == 429
  assert rate_limited.json()["detail"] == auth_routes.RATE_LIMIT_ERROR

  attempts = await session.scalar(select(func.count()).select_from(AuthAttempt))
  assert attempts == 11


@pytest.mark.asyncio
async def test_github_callback_links_existing_user(
  client: AsyncClient,
  session: AsyncSession,
  monkeypatch: pytest.MonkeyPatch,
) -> None:
  settings.github_client_id = "client-id"
  settings.github_client_secret = "client-secret"
  github_oauth_client._client_id = "client-id"
  github_oauth_client._client_secret = "client-secret"

  existing_user = User(
    email="oauth@example.com",
    password_hash=hash_password("Sup3rSecure!"),
    display_name="Existing",
  )
  session.add(existing_user)
  await session.commit()

  state_value = "state-token"
  signed_state = auth_routes._encode_state(state_value)
  client.cookies.set(auth_routes.STATE_COOKIE_NAME, signed_state, path="/")

  async def fake_exchange(self: GitHubOAuthClient, code: str) -> str:  # pragma: no cover - simple stub
    assert code == "oauth-code"
    return "token"

  async def fake_fetch(self: GitHubOAuthClient, token: str) -> GitHubProfile:  # pragma: no cover - simple stub
    assert token == "token"
    return GitHubProfile(id="123", email="oauth@example.com", login="oauth", name="OAuth User")

  monkeypatch.setattr(GitHubOAuthClient, "exchange_code", fake_exchange)
  monkeypatch.setattr(GitHubOAuthClient, "fetch_profile", fake_fetch)

  response = await client.get("/auth/callback/github", params={"code": "oauth-code", "state": state_value})
  assert response.status_code == 302
  assert response.headers["location"] == "http://localhost:3000/welcome"
  assert client.cookies.get(settings.session_cookie.name) is not None

  oauth_account = await session.scalar(select(OAuthAccount).where(OAuthAccount.provider == OAuthProvider.GITHUB))
  assert oauth_account is not None
  assert oauth_account.user_id == existing_user.id


@pytest.mark.asyncio
async def test_github_callback_creates_user_when_missing(
  client: AsyncClient,
  session: AsyncSession,
  monkeypatch: pytest.MonkeyPatch,
) -> None:
  settings.github_client_id = "client-id"
  settings.github_client_secret = "client-secret"
  github_oauth_client._client_id = "client-id"
  github_oauth_client._client_secret = "client-secret"

  state_value = "state-create"
  signed_state = auth_routes._encode_state(state_value)
  client.cookies.set(auth_routes.STATE_COOKIE_NAME, signed_state, path="/")

  async def fake_exchange(self: GitHubOAuthClient, code: str) -> str:
    return "token-create"

  async def fake_fetch(self: GitHubOAuthClient, token: str) -> GitHubProfile:
    return GitHubProfile(id="456", email="new-oauth@example.com", login="new", name="New OAuth")

  monkeypatch.setattr(GitHubOAuthClient, "exchange_code", fake_exchange)
  monkeypatch.setattr(GitHubOAuthClient, "fetch_profile", fake_fetch)

  response = await client.get("/auth/callback/github", params={"code": "code-create", "state": state_value})
  assert response.status_code == 302
  assert client.cookies.get(settings.session_cookie.name) is not None

  new_user = await session.scalar(select(User).where(User.email == "new-oauth@example.com"))
  assert new_user is not None

  oauth_account = await session.scalar(select(OAuthAccount).where(OAuthAccount.provider_account_id == "456"))
  assert oauth_account is not None
  assert oauth_account.user_id == new_user.id
