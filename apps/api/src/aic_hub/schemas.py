from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PublicUser(BaseModel):
  model_config = ConfigDict(populate_by_name=True)

  id: UUID
  email: EmailStr
  display_name: str | None = Field(default=None, alias="displayName")
  username: str | None = None
  avatar_url: str | None = Field(default=None, alias="avatarUrl")
  bio: str | None = None
  company: str | None = None
  location: str | None = None
  expertise_tags: list[str] = Field(default_factory=list, alias="expertiseTags")
  github_username: str | None = Field(default=None, alias="githubUsername")
  created_at: datetime = Field(alias="createdAt")
  article_count: int = Field(default=0, alias="articleCount")
  space_count: int = Field(default=0, alias="spaceCount")


class UserSummary(BaseModel):
  model_config = ConfigDict(populate_by_name=True)

  id: UUID
  username: str | None = Field(default=None)
  display_name: str | None = Field(default=None, alias="displayName")
  avatar_url: str | None = Field(default=None, alias="avatarUrl")


class UserPublicProfile(BaseModel):
  """Public user profile visible to other users (no email)."""
  model_config = ConfigDict(populate_by_name=True)

  id: UUID
  username: str | None = None
  display_name: str | None = Field(default=None, alias="displayName")
  avatar_url: str | None = Field(default=None, alias="avatarUrl")
  bio: str | None = None
  company: str | None = None
  location: str | None = None
  expertise_tags: list[str] = Field(default_factory=list, alias="expertiseTags")
  github_username: str | None = Field(default=None, alias="githubUsername")
  created_at: datetime = Field(alias="createdAt")
  article_count: int = Field(default=0, alias="articleCount")
  space_count: int = Field(default=0, alias="spaceCount")


class UserProfileUpdate(BaseModel):
  """Schema for updating user profile."""
  model_config = ConfigDict(populate_by_name=True)

  display_name: str | None = Field(default=None, max_length=100, alias="displayName")
  bio: str | None = Field(default=None, max_length=500)
  company: str | None = Field(default=None, max_length=100)
  location: str | None = Field(default=None, max_length=100)
  expertise_tags: list[str] | None = Field(default=None, max_length=10, alias="expertiseTags")


class UsernameCheck(BaseModel):
  """Schema for username availability check."""
  username: str = Field(..., min_length=1, max_length=50)


class UsernameCheckResponse(BaseModel):
  """Response for username availability check."""
  available: bool
  suggestion: str | None = None


class UserSearchResponse(BaseModel):
  """Response for user search/list endpoints."""
  users: list[UserPublicProfile]
  total: int
  skip: int
  limit: int


class ArticleBase(BaseModel):
  title: str = Field(..., max_length=255)
  summary: str | None = Field(default=None, max_length=500)
  content: str
  tags: list[str] = Field(default_factory=list)


class ArticleCreate(ArticleBase):
  pass


class ArticleUpdate(BaseModel):
  title: str | None = Field(default=None, max_length=255)
  summary: str | None = Field(default=None, max_length=500)
  content: str | None = None
  tags: list[str] | None = None
  status: Literal["draft", "published", "archived"] | None = None


class ArticleSummary(BaseModel):
  model_config = ConfigDict(from_attributes=True, populate_by_name=True)

  id: UUID
  title: str
  slug: str
  summary: str | None
  tags: list[str]
  author: UserSummary
  view_count: int = Field(default=0, alias="viewCount")
  like_count: int = Field(default=0, alias="likeCount")
  published_at: datetime | None = Field(default=None, alias="publishedAt")
  created_at: datetime = Field(alias="createdAt")


class Article(ArticleSummary):
  """Full article with content."""
  content: str
  status: str
  updated_at: datetime | None = Field(default=None, alias="updatedAt")
  is_author: bool | None = Field(default=None, alias="isAuthor")


class ArticleListResponse(BaseModel):
  """Response for article list endpoints."""
  articles: list[ArticleSummary]
  total: int
  skip: int
  limit: int


class SpaceBase(BaseModel):
  name: str = Field(..., min_length=1, max_length=100)
  description: str | None = Field(default=None, max_length=500)
  tags: list[str] = Field(default_factory=list, max_length=5)
  visibility: Literal["public", "private"] = Field(default="public")


class SpaceCreate(SpaceBase):
  pass


class SpaceUpdate(BaseModel):
  name: str | None = Field(default=None, min_length=1, max_length=100)
  description: str | None = Field(default=None, max_length=500)
  tags: list[str] | None = Field(default=None, max_length=5)
  visibility: Literal["public", "private"] | None = None


class SpaceSummary(BaseModel):
  model_config = ConfigDict(from_attributes=True, populate_by_name=True)

  id: UUID
  name: str
  slug: str
  description: str | None
  tags: list[str]
  visibility: str
  member_count: int = Field(alias="memberCount")
  article_count: int = Field(alias="articleCount")
  created_at: datetime = Field(alias="createdAt")
  owner: UserSummary
  is_member: bool | None = Field(default=None, alias="isMember")
  member_role: str | None = Field(default=None, alias="memberRole")


class Space(SpaceSummary):
  updated_at: datetime | None = Field(default=None, alias="updatedAt")


class SpaceMember(BaseModel):
  model_config = ConfigDict(from_attributes=True, populate_by_name=True)

  user: UserSummary
  role: Literal["owner", "moderator", "member"]
  joined_at: datetime = Field(alias="joinedAt")


class SpaceArticle(BaseModel):
  model_config = ConfigDict(from_attributes=True, populate_by_name=True)

  article: ArticleSummary
  added_by: UserSummary = Field(alias="addedBy")
  pinned: bool
  added_at: datetime = Field(alias="addedAt")


class SpaceListResponse(BaseModel):
  spaces: list[SpaceSummary]
  total: int
  skip: int
  limit: int


class MemberListResponse(BaseModel):
  members: list[SpaceMember]
  total: int
  skip: int
  limit: int


class SpaceArticleListResponse(BaseModel):
  articles: list[SpaceArticle]
  total: int
  skip: int
  limit: int
