from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserProfileBase(BaseModel):
  model_config = ConfigDict(populate_by_name=True, from_attributes=True)

  id: UUID
  username: str
  display_name: str | None = Field(default=None, alias="displayName")
  avatar_url: str | None = Field(default=None, alias="avatarUrl")
  bio: str | None = None
  company: str | None = None
  location: str | None = None
  expertise_tags: list[str] = Field(default_factory=list, alias="expertiseTags")
  created_at: datetime = Field(alias="createdAt")
  updated_at: datetime | None = Field(default=None, alias="updatedAt")


class PrivateUserProfile(UserProfileBase):
  email: EmailStr
  username_editable: bool = Field(default=False, alias="usernameEditable")
  github_username: str | None = Field(default=None, alias="githubUsername")


class PublicUserProfile(UserProfileBase):
  pass


class UserProfileUpdatePayload(BaseModel):
  model_config = ConfigDict(populate_by_name=True)

  display_name: str | None = Field(default=None, alias="displayName")
  username: str | None = None
  bio: str | None = None
  company: str | None = None
  location: str | None = None
  expertise_tags: list[str] | None = Field(default=None, alias="expertiseTags")
