from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

import httpx

from .config import settings

_GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
_GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
_GITHUB_API_BASE = "https://api.github.com"
_USER_AGENT = "AIC-HUB-FastAPI/1.0"


@dataclass(slots=True)
class GitHubProfile:
  id: str
  email: str
  login: str
  name: str | None
  avatar_url: str | None = None


class GitHubOAuthClient:
  def __init__(self) -> None:
    self._client_id = settings.github_client_id
    self._client_secret = settings.github_client_secret
    base_url = str(settings.api_base_url).rstrip("/")
    self._redirect_uri = f"{base_url}/auth/callback/github"

  def _ensure_configured(self) -> None:
    if not self._client_id or not self._client_secret:
      raise RuntimeError("GitHub OAuth client is not configured")

  def build_authorize_url(self, state: str) -> str:
    self._ensure_configured()
    params = {
      "client_id": self._client_id,
      "redirect_uri": self._redirect_uri,
      "scope": "user:email",
      "state": state,
      "allow_signup": "false",
    }
    return f"{_GITHUB_AUTHORIZE_URL}?{urlencode(params)}"

  async def exchange_code(self, code: str) -> str:
    self._ensure_configured()
    async with httpx.AsyncClient(timeout=10.0, headers={"Accept": "application/json", "User-Agent": _USER_AGENT}) as client:
      response = await client.post(
        _GITHUB_TOKEN_URL,
        data={
          "client_id": self._client_id,
          "client_secret": self._client_secret,
          "code": code,
          "redirect_uri": self._redirect_uri,
        },
      )
      response.raise_for_status()
      data = response.json()
    access_token = data.get("access_token")
    if not access_token:
      raise RuntimeError("GitHub token exchange failed")
    return access_token

  async def fetch_profile(self, access_token: str) -> GitHubProfile:
    self._ensure_configured()
    headers = {
      "Authorization": f"Bearer {access_token}",
      "Accept": "application/vnd.github+json",
      "User-Agent": _USER_AGENT,
    }
    async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
      user_resp = await client.get(f"{_GITHUB_API_BASE}/user")
      user_resp.raise_for_status()
      user_data = user_resp.json()

      email = user_data.get("email")
      if not email:
        emails_resp = await client.get(f"{_GITHUB_API_BASE}/user/emails")
        emails_resp.raise_for_status()
        emails = emails_resp.json()
        primary_email = next((item.get("email") for item in emails if item.get("primary") and item.get("verified")), None)
        if not primary_email:
          primary_email = next((item.get("email") for item in emails if item.get("verified")), None)
        email = primary_email

    if not email:
      raise RuntimeError("GitHub profile missing email")

    return GitHubProfile(
      id=str(user_data.get("id")),
      email=str(email),
      login=str(user_data.get("login")),
      name=user_data.get("name"),
      avatar_url=user_data.get("avatar_url"),
    )


github_oauth_client = GitHubOAuthClient()
