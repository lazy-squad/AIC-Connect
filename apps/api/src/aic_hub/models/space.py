from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from ..types import GUID

# Association table for space members
from sqlalchemy import Column

space_members = Table(
    "space_members",
    Base.metadata,
    Column("space_id", UUID(as_uuid=True), ForeignKey("spaces.id"), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("role", String(20), default="member", nullable=False),
    Column("joined_at", DateTime(timezone=True), server_default=func.now()),
    Index("idx_space_members_user", "user_id"),
    CheckConstraint("role IN ('owner', 'moderator', 'member')", name="check_member_role"),
)


class Space(Base):
    __tablename__ = "spaces"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    visibility: Mapped[str] = mapped_column(String(20), default="public", nullable=False)

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    member_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    article_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("User", secondary=space_members, back_populates="spaces")
    space_articles = relationship("SpaceArticle", back_populates="space", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_spaces_visibility_created", "visibility", "created_at"),
        Index("idx_spaces_tags", "tags", postgresql_using="gin"),
        CheckConstraint("visibility IN ('public', 'private')", name="check_visibility"),
    )


class SpaceArticle(Base):
    __tablename__ = "space_articles"

    space_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("spaces.id"), primary_key=True
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id"), primary_key=True
    )
    added_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    space = relationship("Space", back_populates="space_articles")
    article = relationship("Article")
    user = relationship("User", foreign_keys=[added_by])

    __table_args__ = (
        Index("idx_space_articles_added", "space_id", "added_at"),
    )