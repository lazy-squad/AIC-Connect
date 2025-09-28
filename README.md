# AIC HUB MVP Scaffolding

Secure onboarding scaffold with a Next.js web front-end and FastAPI backend running on a shared HTTP origin in local development.

## Prerequisites
- **Node.js 20 LTS** (with `corepack` for pnpm) and **pnpm 9+**
- **Python 3.11+** with [`uv`](https://github.com/astral-sh/uv) for dependency management
- Docker + Docker Compose v2 (for Postgres 16)

## Quickstart
1. Install Node dependencies:
   ```bash
   corepack enable
   pnpm install
   ```
2. Ensure `uv` is installed, then install Python deps on demand (no virtualenv needed thanks to `uv`).
3. Copy environment template and adjust secrets as needed:
   ```bash
   cp .env.example .env
   ```
4. Build and start the local stack (Postgres, API, web) over HTTP:
   ```bash
   docker compose -f docker/compose.yaml up -d --build
   ```
5. Inspect logs if something looks off:
   ```bash
   docker compose -f docker/compose.yaml logs -f web
   ```
6. Open the app at [http://localhost:3000](http://localhost:3000). The FastAPI health check is available through the same origin at [http://localhost:3000/api/health](http://localhost:3000/api/health).

## Development Scripts
- `pnpm dev:web` — run only the Next.js dev server on http://localhost:3000.
- `pnpm dev:api` — run only the FastAPI server via `uvicorn` on http://localhost:4000.
- `pnpm lint`, `pnpm format`, `pnpm typecheck`, `pnpm build` — workspace quality gates and web build.
- `pnpm test` — Playwright smoke test (`apps/web`) + Pytest smoke test (`apps/api`).

## Testing Notes
- Playwright runs against `http://localhost:3000`. Install browsers once with `pnpm --filter web exec playwright install --with-deps`.
- Pytest hits `/health` through an HTTP client transport and stubs external integrations.
- All tests assume Postgres is available (connection is verified on startup).

## FastAPI Endpoints
- `GET /health` — returns `{ "status": "ok" }`.
- `GET /auth/login/github` — 501 placeholder.
- `GET /auth/callback/github` — 501 placeholder (logs callback params).
- `POST /auth/email/request` — 501 placeholder (logs requested email).
- `GET /auth/email/verify` — 501 placeholder.
- `GET /me` — returns 401 until session issuance is wired.
- `GET /config/cookie` — exposes secure-cookie defaults (`httpOnly`, `Secure`, `SameSite=Lax`).

The provider callback URL you must register with GitHub is `http://localhost:3000/api/auth/callback/github` with scopes `read:user user:email`.

## CI
- **Web CI**: installs pnpm deps, then runs lint → typecheck → Next.js build.
- **API CI**: installs Python 3.11 + `uv`, then runs Pytest against the HTTP configuration used in development.

## Troubleshooting
- Use `docker compose -f docker/compose.yaml logs -f web` (or `api` / `postgres`) to inspect service readiness.
- Ensure `.env` values point to `http://localhost:3000`; mismatched origins will surface as CORS failures.
- Running `pnpm dev` locally still works if you prefer to run services outside Docker (HTTP only).

## Next Steps
- Implement GitHub OAuth with Authlib using settings from `.env`.
- Issue secure session cookies once token storage is defined.
- Replace console-logged magic links with mail delivery in production environments.
