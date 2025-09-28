"""Tag usage tracking model for the AIC Hub."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class TagUsage(Base):
    """Track tag usage statistics across the platform."""

    __tablename__ = "tag_usage"

    tag: Mapped[str] = mapped_column(String(50), primary_key=True)
    article_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    space_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Users with this expertise
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trending_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    week_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Usage this week
    month_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Usage this month

    # Indexes
    __table_args__ = (
        Index('idx_tag_usage_trending', 'trending_score'),
        Index('idx_tag_usage_counts', 'article_count', 'space_count', 'user_count'),
    )