from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base
from ..types import GUID


class AuthAction(str, enum.Enum):
  SIGNUP = "signup"
  LOGIN = "login"


class AuthAttempt(Base):
  __tablename__ = "auth_attempts"

  id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
  action: Mapped[AuthAction] = mapped_column(Enum(AuthAction, name="auth_action"), nullable=False)
  email_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
  ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
  success: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
  reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
