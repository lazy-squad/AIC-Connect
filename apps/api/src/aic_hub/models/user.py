from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func, text
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from ..types import GUID, StringList


class User(Base):
  __tablename__ = "users"

  id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
  email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
  password_hash: Mapped[str | None] = mapped_column(String(512), nullable=True)
  display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
  username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
  github_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
  avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
  bio: Mapped[str | None] = mapped_column(Text, nullable=True)
  company: Mapped[str | None] = mapped_column(String(255), nullable=True)
  location: Mapped[str | None] = mapped_column(String(255), nullable=True)
  expertise_tags: Mapped[list[str]] = mapped_column(
    MutableList.as_mutable(StringList()),
    nullable=False,
    default=list,
    server_default=text("'{}'"),
  )
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
  last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

  oauth_accounts = relationship(
    "OAuthAccount",
    back_populates="user",
    cascade="all, delete-orphan",
    lazy="selectin",
  )
