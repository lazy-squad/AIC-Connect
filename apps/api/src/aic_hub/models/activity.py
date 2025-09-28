"""Activity model for tracking user actions and generating activity feeds."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from ..types import GUID


class Activity(Base):
    """Activity tracking for user actions in the system."""

    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # article_published, space_created, user_joined_space
    target_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # article, space, user
    target_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False)
    activity_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationships
    actor = relationship("User")

    __table_args__ = (
        Index("idx_activities_actor_created", "actor_id", "created_at"),
        Index("idx_activities_target", "target_type", "target_id"),
    )