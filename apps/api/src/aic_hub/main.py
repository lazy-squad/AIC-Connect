from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from .config import settings
from .db import dispose_engine, verify_database_connection
from .routes.auth import router as auth_router
from .routes.health import router as health_router
from .routes.me import router as me_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
  logger.info("Starting FastAPI application")
  try:
    await verify_database_connection()
    logger.info("Database connection verified")
  except Exception:
    logger.exception("Failed to connect to the database")
    raise
  yield
  await dispose_engine()
  logger.info("FastAPI application shutdown complete")


app = FastAPI(
  title="AIC HUB API",
  version="0.1.0",
  docs_url="/docs",
  redoc_url="/redoc",
  lifespan=lifespan,
)

app.add_middleware(ProxyHeadersMiddleware)
app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.cors_origins,
  allow_credentials=True,
  allow_methods=["GET", "POST", "OPTIONS"],
  allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(me_router)


@app.get("/config/cookie")
async def session_cookie_config() -> dict[str, object]:
  """Expose cookie configuration for client scaffolding."""
  cookie = settings.session_cookie
  return {
    "name": cookie.name,
    "httpOnly": cookie.http_only,
    "secure": cookie.secure,
    "sameSite": cookie.same_site,
    "maxAgeSeconds": cookie.max_age_seconds,
  }
