from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from aic_hub.main import app


@pytest.fixture(autouse=True)
def _stub_db(monkeypatch: pytest.MonkeyPatch) -> None:
  async def _noop() -> None:  # pragma: no cover - simple stub
    return None

  monkeypatch.setattr("aic_hub.main.verify_database_connection", _noop)
  monkeypatch.setattr("aic_hub.main.dispose_engine", _noop)


@pytest.mark.asyncio
async def test_health_endpoint_returns_ok() -> None:
  transport = ASGITransport(app=app)
  async with AsyncClient(transport=transport, base_url="http://testserver") as client:
    response = await client.get("/health")

  assert response.status_code == 200
  assert response.json() == {"status": "ok"}
