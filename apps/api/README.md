# AIC HUB API

FastAPI backend for the AIC HUB MVP. It now ships fully functional email/password auth, Argon2id hashing, signed
session cookies, GitHub OAuth, and Postgres-backed rate limiting.

## Key Features
-	`POST /auth/signup` creates users, hashes passwords, and issues session cookies.
-	`POST /auth/login` verifies passwords and updates last-login timestamps.
-	`POST /auth/logout` clears the session cookie (HttpOnly, SameSite=Lax).
-	GitHub OAuth callback links existing users by email or provisions a new account.
-	`GET /me` requires a valid session and returns the public profile.

Run the test suite with:

```bash
uv run --extra dev pytest
```

Apply migrations with:

```bash
uv run alembic upgrade head
```
