# Repository Guidelines

> This repository implements the AIC HUB MVP described in `prd.md`. Use this guide for day‑to‑day development, reviews, and automation.

## Project Structure & Module Organization
- `apps/web` — Next.js PWA (App Router, shadcn/ui, Radix).
- `apps/api` — Node/TypeScript REST + WebSocket gateway.
- `packages/*` — shared TypeScript libs (e.g., `ui`, `config`, `db`).
- `docker/` — Dockerfiles and `compose.yaml` for local stack (Postgres, Redis, object storage).
- `tests/` — e2e, fixtures, seed data.
- `scripts/` — developer and ops helpers.

## Build, Test, and Development Commands
- Install toolchain: `corepack enable && pnpm i` (workspace install).
- Run full dev (web+api): `pnpm dev` or per app: `pnpm -F web dev`, `pnpm -F api dev`.
- Local stack: `docker compose up -d`; logs: `docker compose logs -f api`.
- Lint/format: `pnpm lint && pnpm format`; build: `pnpm build` (or `pnpm -F web build`).
- Tests: `pnpm test` (all) or filtered: `pnpm -F api test`.

## Coding Style & Naming Conventions
- Language: TypeScript (strict). Indentation: 2 spaces. Imports sorted.
- Formatting: Prettier; Linting: ESLint (`@typescript-eslint`, Next.js).
- Naming: files `kebab-case.ts(x)`; React components `PascalCase`; vars/functions `camelCase`.
- API routes: plural REST (`/api/posts`); WS endpoint `/ws`.

## Testing Guidelines
- Unit/integration: Vitest. E2E: Playwright under `tests/e2e`.
- File names: unit `*.test.ts`; integration `*.spec.ts`; e2e `*.e2e.ts`.
- Coverage target: ≥80% lines. Run with `pnpm test -- --coverage`.
- Seed deterministic data for e2e; avoid external network.

## Commit & Pull Request Guidelines
- Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`.
- PRs include: What/Why, test plan, screenshots (UI), linked issue/PRD section.
- Keep changes small and focused; CI must pass; update `prd.md` decision log when scope changes.

## Security & Configuration Tips
- Never commit secrets. Use `.env`/`.env.local`; update `.env.example` when adding vars.
- Expected envs: `DATABASE_URL`, `REDIS_URL`, `OBJECT_STORAGE_*`, `MAIL_*`, `ALLOWED_ORIGIN`.
- MVP runs behind AWS ALB on HTTP:80; enable HTTPS (ACM) and HSTS post‑MVP.

## Agent‑Specific Instructions
- Scope: this file applies repo‑wide; nested `AGENTS.md` (if any) takes precedence.
- Before large edits: share a brief plan, prefer minimal diffs, and update docs/tests with code.
- Use `rg` for search; read files in ≤250‑line chunks; keep patches surgical.
