from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SessionCookieConfig(BaseSettings):
  name: str = Field(default="aic_hub_session")
  secure: bool = Field(default=True)
  http_only: bool = Field(default=True, serialization_alias="httpOnly")
  same_site: Literal["lax", "strict", "none"] = Field(default="lax")
  max_age_seconds: int = Field(default=60 * 60 * 24 * 7)

  model_config = SettingsConfigDict(env_prefix="SESSION_", extra="ignore")


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=(".env", ".env.local", "../../.env", "../../.env.local"),
    env_file_encoding="utf-8",
    extra="ignore",
  )

  environment: str = Field(default="development", alias="ENVIRONMENT")
  web_base_url: AnyHttpUrl = Field(default="http://localhost:3000", alias="WEB_BASE_URL")
  api_base_url: AnyHttpUrl = Field(default="http://localhost:3000", alias="API_BASE_URL")
  allowed_origin: AnyHttpUrl = Field(default="http://localhost:3000", alias="ALLOWED_ORIGIN")

  database_url: str = Field(default="postgresql://postgres:postgres@localhost:5432/aic_hub", alias="DATABASE_URL")
  secret_key: SecretStr = Field(default=SecretStr("change-me"), alias="SECRET_KEY")

  github_client_id: str = Field(default="", alias="GITHUB_CLIENT_ID")
  github_client_secret: str = Field(default="", alias="GITHUB_CLIENT_SECRET")

  token_exp_minutes: int = Field(default=15, alias="TOKEN_EXP_MINUTES")
  session_max_age_days: int = Field(default=7, alias="SESSION_MAX_AGE_DAYS")

  session_cookie: SessionCookieConfig = SessionCookieConfig()

  @property
  def async_database_url(self) -> str:
    if self.database_url.startswith("postgresql+asyncpg://"):
      return self.database_url
    if self.database_url.startswith("postgresql://"):
      return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return self.database_url

  @property
  def cors_origins(self) -> list[str]:
    return [str(self.allowed_origin)]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
  return Settings()


settings = get_settings()
