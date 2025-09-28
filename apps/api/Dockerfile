FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

RUN pip install --no-cache-dir uv

COPY apps/api/pyproject.toml apps/api/uv.lock apps/api/README.md ./

RUN uv sync --frozen --no-dev --python 3.11

COPY apps/api /app

CMD ["uv", "run", "--directory", "/app", "--", "uvicorn", "aic_hub.main:app", "--host", "0.0.0.0", "--port", "4000"]
