from __future__ import annotations

import uuid

from typing import Any, Iterable

from sqlalchemy import types
from sqlalchemy.dialects import postgresql


def _coerce_string_list(value: Any) -> list[str]:
  """Normalize persisted values into a list of strings."""
  if value is None:
    return []
  if isinstance(value, list | tuple | set):
    return [str(item) for item in value]
  if isinstance(value, str):
    if value in {"", "{}", "[]"}:
      return []
    if value.startswith("{") and value.endswith("}"):
      # PostgreSQL array literal
      inner = value[1:-1]
      if not inner:
        return []
      return [part.strip().strip('"') for part in inner.split(",")]
    return [value]
  # Fallback for iterables that aren't common sequence types
  if isinstance(value, Iterable):  # pragma: no cover - defensive
    return [str(item) for item in value]
  return [str(value)]


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


class StringList(types.TypeDecorator):
  """PostgreSQL TEXT[] with JSON fallback for SQLite-based tests."""

  impl = types.JSON
  cache_ok = True

  def load_dialect_impl(self, dialect):  # type: ignore[override]
    if dialect.name == "postgresql":
      return dialect.type_descriptor(postgresql.ARRAY(types.String()))
    return dialect.type_descriptor(types.JSON())

  def process_bind_param(self, value, dialect):  # type: ignore[override]
    if value is None:
      return [] if dialect.name != "postgresql" else []
    coerced = _coerce_string_list(value)
    return coerced

  def process_result_value(self, value, dialect):  # type: ignore[override]
    if value is None:
      return []
    if isinstance(value, list):
      return [str(item) for item in value]
    if dialect.name == "postgresql" and isinstance(value, str):
      return _coerce_string_list(value)
    if isinstance(value, str):
      return _coerce_string_list(value)
    if isinstance(value, Iterable):  # pragma: no cover - defensive
      return [str(item) for item in value]
    return [str(value)]
