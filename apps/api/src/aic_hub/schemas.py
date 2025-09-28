from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PublicUser(BaseModel):
  model_config = ConfigDict(populate_by_name=True)

  id: UUID
  email: EmailStr
  display_name: str | None = Field(default=None, alias="displayName")
