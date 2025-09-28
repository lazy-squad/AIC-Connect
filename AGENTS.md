# Repository Guidelines

> This repository implements the AIC HUB MVP described in `prd.md`. Use this guide for day-to-day development, reviews, and automation.

## Project Structure & Module Organization
- `apps/web` — Next.js (App Router, Tailwind) PWA served over HTTP with rewrites to the API during development.
- `apps/api` — FastAPI (Python 3.11+, uv, SQLAlchemy 2) REST gateway with placeholder auth endpoints.
- `packages/*` — shared TypeScript libraries (reserved for future work).
- `docker/` — Docker Compose for the local Postgres stack.
- `tests/` — reserved for cross-package end-to-end fixtures when needed (current smoke tests live beside each app).
- `scripts/` — developer and ops helpers (e.g., mkcert bootstrap).

## Build, Test, and Development Commands
- Install toolchain: `corepack enable && pnpm install --frozen-lockfile` plus `uv` for Python dependencies.
- Local stack: `docker compose -f docker/compose.yaml up -d`; logs with `docker compose -f docker/compose.yaml logs -f postgres`.
- Development:
  - `pnpm dev` — runs HTTP web (3000) and API (4000) concurrently.
  - `pnpm dev:web` — Next.js dev server on http://localhost:3000 with rewrites to the API.
  - `pnpm dev:api` — uvicorn FastAPI server on http://localhost:4000 (`apps/api`).
- Quality gates: `pnpm lint`, `pnpm format`, `pnpm typecheck`, `pnpm build` (web bundle).
- Tests: `pnpm test` (Playwright smoke + Pytest). Run individually with `pnpm --filter web test` and `pnpm test:api`.

## Coding Style & Naming Conventions
- Frontend language: TypeScript (strict). Backend: Python 3.11+ (PEP 8, type hints encouraged).
- Indentation: 2 spaces for TS/JS, 4 spaces for Python.
- Imports sorted automatically via tooling (ESLint/Prettier on TS, `isort` not configured yet—keep blocks grouped manually).
- React components use PascalCase; files use `kebab-case.tsx`. Python modules use `snake_case`.

## Testing Guidelines
- API: Pytest (async) in `apps/api/tests`. Keep HTTP clients on the HTTP scheme and stub external integrations.
- Web: Playwright smoke specs in `apps/web/tests`. Exercise routes over `http://localhost:3000` and rely on `/api` rewrites.
- Aim for ≥80% coverage once features mature. Run `pnpm test -- --coverage` when coverage gates are reintroduced.
- Seed deterministic data in Postgres fixtures (none required yet). Avoid external network calls.

## Commit & Pull Request Guidelines
- Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`).
- PRs must describe What/Why, include test plan, screenshots for UI, and reference relevant `prd.md` sections.
- Keep changes focused; ensure CI (`Web CI`, `API CI`) passes before review.
- Update the `prd.md` decision log whenever scope changes materially.

## Security & Configuration Tips
- Never commit secrets. Use `.env`/`.env.local`; keep `.env.example` current when adding vars.
- Expected envs: `WEB_BASE_URL`, `API_BASE_URL`, `ALLOWED_ORIGIN`, `DATABASE_URL`, `SECRET_KEY`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `TOKEN_EXP_MINUTES`, `SESSION_MAX_AGE_DAYS`, `NEXT_PUBLIC_API_BASE_URL`, `API_INTERNAL_URL`.
- Local dev uses HTTP only; same-origin via Next.js rewrites; no Redis, no WebSockets, no TLS in app.
- Dev cookies must remain `httpOnly`, `Secure`, `SameSite=Lax`. HSTS stays disabled for local.
- Backend currently depends only on Postgres (no Redis/WebSockets/SMTP in MVP); magic links log to console during development.

## Agent-Specific Instructions
- Scope: this file applies repo-wide; nested `AGENTS.md` (if any) takes precedence.
- Before large edits: share a brief plan, prefer minimal diffs, and update docs/tests alongside code.
- Use `rg` for search; read files in ≤250-line chunks; keep patches surgical.
