"""Article model for the AIC Hub."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from ..types import GUID


class Article(Base):
    """Article model for blog posts and technical articles."""

    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Will store JSON as text for now
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")  # draft, published
    author_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id"), nullable=False
    )
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationships
    author = relationship("User", back_populates="articles")

    @property
    def published(self) -> bool:
        """Check if article is published."""
        return self.status == "published"