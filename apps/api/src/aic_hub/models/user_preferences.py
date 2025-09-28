"""User preferences model for feed personalization."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from ..types import GUID


class UserPreferences(Base):
    """User preferences for feed personalization."""

    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id"), primary_key=True
    )
    preferred_tags: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    feed_view: Mapped[str] = mapped_column(
        String(20), default="latest", nullable=False
    )  # latest, trending, following
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="preferences")