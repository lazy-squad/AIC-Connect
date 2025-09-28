from __future__ import annotations

import uuid

from sqlalchemy import types
from sqlalchemy.dialects import postgresql


class GUID(types.TypeDecorator):
  """Platform-independent GUID type.

  Falls back to CHAR(36) for non-PostgreSQL dialects to support in-memory tests.
  """

  impl = types.CHAR
  cache_ok = True

  def load_dialect_impl(self, dialect):  # type: ignore[override]
    if dialect.name == "postgresql":
      return dialect.type_descriptor(postgresql.UUID(as_uuid=True))
    return dialect.type_descriptor(types.CHAR(36))

  def process_bind_param(self, value, dialect):  # type: ignore[override]
    if value is None:
      return value
    if isinstance(value, uuid.UUID):
      return str(value)
    return str(uuid.UUID(str(value)))

  def process_result_value(self, value, dialect):  # type: ignore[override]
    if value is None:
      return value
    if isinstance(value, uuid.UUID):
      return value
    return uuid.UUID(str(value))
