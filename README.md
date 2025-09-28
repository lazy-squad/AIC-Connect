# AIC HUB MVP Scaffolding

Secure onboarding scaffold with a Next.js web front-end and FastAPI backend running on a shared HTTP origin in local development. Email + password accounts, session cookies, GitHub OAuth, and editable user profiles are all wired end-to-end.

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
5. Apply database migrations:
   ```bash
   cd apps/api
   uv run alembic upgrade head
   ```
6. Inspect logs if something looks off:
   ```bash
   docker compose -f docker/compose.yaml logs -f web
   ```
7. Open the app at [http://localhost:3000](http://localhost:3000). The FastAPI health check is available through the same origin at [http://localhost:3000/api/health](http://localhost:3000/api/health).

> Local is HTTP-only; set `SESSION_SECURE=false`. In TLS environments, set `SESSION_SECURE=true` so cookies ship with the Secure flag.

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
- `POST /auth/signup` — creates a user, sets the session cookie, responds with the private profile payload.
- `POST /auth/login` — verifies credentials, issues a fresh session cookie.
- `POST /auth/logout` — clears the session cookie.
- `GET /auth/login/github` — redirects to GitHub OAuth with CSRF-protected state.
- `GET /auth/callback/github` — exchanges the code, links or creates the user, and redirects back to `/welcome`.
- `GET /users/me` — returns the authenticated user’s private profile (alias `/me` maintained for backward compatibility).
- `PATCH /users/me` — updates display name, bio, company, location, expertise tags, and (once) username.
- `GET /users/{username}` — public profile without email or session metadata.
- `GET /users` — lists public profiles; supports `q` (username/display name search), `tag` (expertise filter), and `limit`/`offset` pagination.
- `GET /config/cookie` — exposes cookie defaults for the web UI.

## Profile API Usage

- Usernames are lowercase slugs (`a-z`, `0-9`, `-`, length 3–32). New accounts receive an email-derived slug that can be changed once; afterward the field is locked server-side.
- Expertise tags are validated against a fixed list and stored as a Postgres `TEXT[]` (mirrored as JSON when running SQLite-backed tests).
- Private profile responses include `usernameEditable` and `githubUsername` to drive the settings UI.

### Allowed Expertise Tags

`LLMs`, `RAG`, `Agents`, `Fine-tuning`, `Prompting`, `Vector DBs`, `Embeddings`, `Training`, `Inference`, `Ethics`, `Safety`, `Benchmarks`, `Datasets`, `Tools`, `Computer Vision`, `NLP`, `Speech`, `Robotics`, `RL`

### Example Requests

```bash
# Fetch the authenticated profile (replace the cookie placeholder after signing in)
curl http://localhost:3000/api/users/me \
  --cookie "aic_hub_session=<token>"

# Update profile details and username (allowed once per account)
curl http://localhost:3000/api/users/me \
  --cookie "aic_hub_session=<token>" \
  -H "Content-Type: application/json" \
  -X PATCH \
  -d '{
    "displayName": "Builder One",
    "username": "builder-01",
    "bio": "Exploring applied AI.",
    "company": "AIC Ventures",
    "location": "Remote",
    "expertiseTags": ["LLMs", "Agents"]
  }'

# Read a public profile anonymously
curl http://localhost:3000/api/users/builder-01
```

## Authentication

- **Password policy:** minimum 8 characters with at least one letter and one number. Server-side validation returns a generic error to avoid account enumeration.
- **Hashing:** Argon2id (`time_cost=2`, `memory_cost=64MB`, `parallelism=1`).
- **Sessions:** signed tokens stored in an HttpOnly cookie (`SameSite=Lax`, `Secure=false` in local HTTP) with a 7-day lifetime.
- **Rate limiting:** naive per-email and per-IP counters (signup: 5/15 min, login: 10/15 min) backed by Postgres.
- **Logout:** `POST /auth/logout` clears the cookie and updates the header in the web client.

### GitHub OAuth App settings

- Homepage URL: `http://localhost:3000`
- Authorization callback URL: `http://localhost:3000/api/auth/callback/github`
- Scopes: `read:user user:email`

Only the provider account ID is stored; access tokens are discarded after fetching the profile.

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
