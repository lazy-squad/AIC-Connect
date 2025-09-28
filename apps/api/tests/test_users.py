from __future__ import annotations

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aic_hub.constants import AI_EXPERTISE_TAGS
from aic_hub.models import User


@pytest.mark.asyncio
async def test_update_profile_sets_username_and_fields(client: AsyncClient, session: AsyncSession) -> None:
  signup = await client.post(
    "/auth/signup",
    json={"email": "profile@example.com", "password": "Sup3rSecure!", "displayName": "Profile"},
  )
  assert signup.status_code == 201

  patch = await client.patch(
    "/users/me",
    json={
      "displayName": "Updated Name",
      "username": "profile-builder",
      "bio": "Ship, test, iterate.",
      "company": "AIC Labs",
      "location": "Remote",
      "expertiseTags": ["LLMs", "Agents"],
    },
  )
  assert patch.status_code == 200
  payload = patch.json()
  assert payload["username"] == "profile-builder"
  assert payload["displayName"] == "Updated Name"
  assert payload["bio"] == "Ship, test, iterate."
  assert payload["expertiseTags"] == ["LLMs", "Agents"]
  assert payload["usernameEditable"] is False
  assert payload["updatedAt"] is not None

  user = await session.scalar(select(User).where(User.email == "profile@example.com"))
  assert user is not None
  assert user.username == "profile-builder"
  assert user.expertise_tags == ["LLMs", "Agents"]
  assert user.updated_at is not None
  assert user.updated_at.year >= datetime.now(tz=UTC).year - 1

  second_attempt = await client.patch("/users/me", json={"username": "another"})
  assert second_attempt.status_code == 400
  assert second_attempt.json()["detail"] == "Username can only be set once"


@pytest.mark.asyncio
async def test_update_profile_validates_username_and_tags(client: AsyncClient) -> None:
  await client.post(
    "/auth/signup",
    json={"email": "invalid@example.com", "password": "Sup3rSecure!", "displayName": "Invalid"},
  )

  slugified = await client.patch("/users/me", json={"username": "Invalid Upper"})
  assert slugified.status_code == 200
  slug_payload = slugified.json()
  assert slug_payload["username"] == "invalid-upper"
  assert slug_payload["usernameEditable"] is False

  bad_tags = await client.patch("/users/me", json={"expertiseTags": ["LLMs", "Unknown"]})
  assert bad_tags.status_code == 400
  detail = bad_tags.json()["detail"]
  assert detail["message"] == "Invalid expertise tags"
  assert detail["invalidTags"] == ["Unknown"]


@pytest.mark.asyncio
async def test_public_profile_and_listing(client: AsyncClient, session: AsyncSession) -> None:
  user = User(
    email="list@example.com",
    password_hash=None,
    display_name="List User",
    username="list-user",
    expertise_tags=[AI_EXPERTISE_TAGS[0], AI_EXPERTISE_TAGS[1]],
  )
  session.add(user)
  await session.commit()

  public = await client.get("/users/list-user")
  assert public.status_code == 200
  public_payload = public.json()
  assert "email" not in public_payload
  assert public_payload["username"] == "list-user"
  assert public_payload["displayName"] == "List User"
  assert public_payload["expertiseTags"] == [AI_EXPERTISE_TAGS[0], AI_EXPERTISE_TAGS[1]]

  listing = await client.get("/users", params={"tag": AI_EXPERTISE_TAGS[0], "limit": 10})
  assert listing.status_code == 200
  results = listing.json()
  assert any(item["username"] == "list-user" for item in results)

  filtered = await client.get("/users", params={"q": "list"})
  assert filtered.status_code == 200
  filtered_results = filtered.json()
  assert filtered_results[0]["username"] == "list-user"

  invalid_filter = await client.get("/users", params={"tag": "Invalid"})
  assert invalid_filter.status_code == 400
