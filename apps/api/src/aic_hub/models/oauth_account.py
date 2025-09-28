from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from ..types import GUID


class OAuthProvider(str, enum.Enum):
  GITHUB = "github"


class OAuthAccount(Base):
  __tablename__ = "oauth_accounts"
  __table_args__ = (
    UniqueConstraint("provider", "provider_account_id", name="uq_oauth_provider_account"),
  )

  id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
  user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  provider: Mapped[OAuthProvider] = mapped_column(Enum(OAuthProvider, name="oauth_provider"), nullable=False)
  provider_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

  user = relationship("User", back_populates="oauth_accounts", lazy="joined")
