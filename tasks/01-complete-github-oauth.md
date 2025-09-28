# Task 01: Complete GitHub OAuth Implementation

## Objective
Implement the GitHub OAuth flow that's currently stubbed out in the codebase, enabling users to authenticate with their GitHub accounts.

## Current State
- FastAPI routes exist but return 501 Not Implemented
- Frontend has GitHub sign-in button that links to `/api/auth/login/github`
- Database connection is working
- CORS is configured

## Acceptance Criteria
- [ ] GitHub OAuth flow works end-to-end
- [ ] User data from GitHub is stored in database
- [ ] JWT tokens are generated and stored in cookies
- [ ] Protected routes check for valid authentication
- [ ] User can sign out

## Implementation Details

### 0. Check Existing Codebase
Before implementing, verify current state:

```bash
# Check existing auth routes
cat apps/api/src/aic_hub/routes/auth.py

# Check for existing user model
find apps/api -name "*.py" -type f | xargs grep -l "class User"

# Check database configuration
cat apps/api/src/aic_hub/db.py

# Check for existing migrations
ls -la apps/api/alembic/versions/

# Check environment variables
cat .env.example

# Check main app configuration
cat apps/api/src/aic_hub/main.py
cat apps/api/src/aic_hub/config.py
```

### 1. Database Models to Create
Add to `apps/api/alembic/versions/` as a new migration:

```python
# User table
users = Table(
    'users',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column('github_id', String, unique=True, nullable=False),
    Column('username', String, unique=True, nullable=False),
    Column('email', String, unique=True, nullable=True),
    Column('name', String, nullable=False),
    Column('avatar_url', String, nullable=True),
    Column('company', String, nullable=True),
    Column('location', String, nullable=True),
    Column('bio', Text, nullable=True),
    Column('expertise_tags', ARRAY(String), default=[]),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), onupdate=func.now())
)
```

### 2. Update Environment Variables
Add to `.env` (from `.env.example`):
```
GITHUB_CLIENT_ID=your_github_app_client_id
GITHUB_CLIENT_SECRET=your_github_app_client_secret
```

GitHub App Settings:
- Homepage URL: `http://localhost:3000`
- Callback URL: `http://localhost:3000/api/auth/callback/github`

### 3. Implement Auth Routes
Update `apps/api/src/aic_hub/routes/auth.py`:

```python
@router.get("/login/github")
async def github_login():
    """Redirect to GitHub OAuth page"""
    # 1. Generate state token for CSRF protection
    # 2. Build GitHub authorize URL with client_id, redirect_uri, scope, state
    # 3. Return RedirectResponse to GitHub

@router.get("/callback/github")
async def github_callback(code: str, state: str):
    """Handle GitHub OAuth callback"""
    # 1. Verify state token
    # 2. Exchange code for access token via GitHub API
    # 3. Fetch user data from GitHub API
    # 4. Create/update user in database
    # 5. Generate JWT token
    # 6. Set secure cookie with token
    # 7. Redirect to /feed
```

### 4. Add User Model
Create `apps/api/src/aic_hub/models/user.py`:

```python
from sqlalchemy import Column, String, Text, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from ..db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True)
    github_id = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    # ... other fields
```

### 5. Create Auth Dependencies
Create `apps/api/src/aic_hub/dependencies/auth.py`:

```python
from fastapi import Depends, HTTPException, Cookie
from jose import jwt, JWTError

async def get_current_user(session_token: str = Cookie(None)):
    """Validate JWT token and return current user"""
    if not session_token:
        raise HTTPException(status_code=401)
    try:
        # Decode JWT
        # Fetch user from database
        # Return user
    except JWTError:
        raise HTTPException(status_code=401)
```

### 6. Update /me Route
Update `apps/api/src/aic_hub/routes/me.py`:

```python
@router.get("/me")
async def get_current_user(user: User = Depends(get_current_user)):
    """Return current authenticated user"""
    return {
        "id": str(user.id),
        "username": user.username,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "expertise_tags": user.expertise_tags
    }
```

### 7. Frontend Auth Callback Page
Create `apps/web/src/app/auth/callback/page.tsx`:

```tsx
'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Check for error parameter
    const error = searchParams.get('error');
    if (error) {
      router.push(`/?error=${error}`);
      return;
    }

    // Success - redirect to feed
    router.push('/feed');
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p>Authenticating...</p>
    </div>
  );
}
```

## Testing Steps

1. **Setup GitHub OAuth App**
   - Go to GitHub Settings > Developer settings > OAuth Apps
   - Create new OAuth App with callback URL
   - Copy Client ID and Secret to `.env`

2. **Run Database Migration**
   ```bash
   cd apps/api
   uv run alembic upgrade head
   ```

3. **Test Auth Flow**
   - Start services: `docker compose -f docker/compose.yaml up`
   - Click "Sign in with GitHub" on homepage
   - Authorize app on GitHub
   - Should redirect back and create user
   - Check `/api/me` returns user data

4. **Verify Cookie**
   - Open browser DevTools > Application > Cookies
   - Should see secure session cookie
   - Cookie should have httpOnly, secure flags

## Success Metrics
- OAuth flow completes in < 3 seconds
- User data correctly populated from GitHub
- Session persists across page refreshes
- Protected routes return 401 when not authenticated

## Dependencies
- PostgreSQL running (via Docker)
- Valid GitHub OAuth App credentials
- `authlib` and `httpx` Python packages installed

## Common Issues

### Issue: CSRF token mismatch
- Solution: Ensure state parameter is stored and validated properly

### Issue: GitHub API rate limits
- Solution: Cache user data, don't fetch on every request

### Issue: Cookie not setting
- Solution: Check CORS and cookie settings match between frontend/backend

## Notes for AI Agents
- Start with database migration
- Test each step incrementally
- Use existing code patterns from the scaffold
- Keep authentication simple - just JWT in cookies
- Don't implement refresh tokens for MVP