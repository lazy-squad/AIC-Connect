"""Search index model for full-text search across the platform."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base
from ..types import GUID


class SearchIndex(Base):
    """Search index for full-text search across articles, spaces, and users."""

    __tablename__ = "search_index"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)  # article, space, user
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    # Note: We'll add the search_vector column in the migration with proper PostgreSQL TSVector type
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Indexes
    __table_args__ = (
        Index('idx_search_entity', 'entity_type', 'entity_id'),
        Index('idx_search_tags', 'tags', postgresql_using='gin'),
    )