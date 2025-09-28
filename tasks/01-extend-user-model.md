# Task 01: Extend User Model for AI Collective Hub

## Objective
Extend the existing User model to include GitHub profile data and expertise tags for the AI Collective Hub MVP.

## Current State
- Basic User model exists with email, password_hash, display_name
- GitHub OAuth is implemented and working
- OAuthAccount model links users to GitHub accounts
- Database migrations are set up with Alembic

## Acceptance Criteria
- [ ] User model includes GitHub profile fields (username, avatar_url, bio, company, location)
- [ ] Expertise tags field for AI topics
- [ ] Migration runs successfully
- [ ] GitHub data populates on OAuth login
- [ ] User profile endpoint returns extended data

## Implementation Details

### 0. Check Existing Codebase
Before implementing, verify current state:

```bash
# Check existing user model
cat apps/api/src/aic_hub/models/user.py

# Check OAuth implementation
cat apps/api/src/aic_hub/routes/auth.py | grep -A 20 "github_callback"

# Check existing migrations
ls -la apps/api/alembic/versions/

# Check GitHub OAuth client
cat apps/api/src/aic_hub/github.py

# Check database configuration
cat apps/api/src/aic_hub/db.py
```

### 1. Extend User Model
Update `apps/api/src/aic_hub/models/user.py`:

```python
from sqlalchemy import Column, String, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__ = "users"

    # Existing fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # New GitHub profile fields
    username = Column(String, unique=True, nullable=True, index=True)
    github_username = Column(String, unique=True, nullable=True)
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)

    # AI expertise tags
    expertise_tags = Column(ARRAY(String), default=[], nullable=False)

    # Relationships (existing)
    oauth_accounts = relationship("OAuthAccount", back_populates="user")
```

### 2. Create Migration
Generate and edit migration:

```bash
cd apps/api
uv run alembic revision --autogenerate -m "Add GitHub profile fields to User"
```

Review and edit the generated migration to ensure:
- New columns are added with proper types
- ARRAY type for expertise_tags
- Indexes on username fields
- Default values where appropriate

### 3. Update GitHub OAuth Callback
Modify `apps/api/src/aic_hub/routes/auth.py` in the `github_callback` function:

```python
# Around line 429 where user is created
if not user:
    display_name = profile.name or profile.login
    user = User(
        email=normalized_email,
        password_hash=None,
        display_name=display_name,
        # Add new fields
        github_username=profile.login,
        username=profile.login,  # Use GitHub username as default
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        company=profile.company,
        location=profile.location,
        expertise_tags=[]  # Empty initially, user can add later
    )
else:
    # Update existing user with GitHub data if not set
    if not user.github_username:
        user.github_username = profile.login
    if not user.username:
        user.username = profile.login
    if not user.avatar_url:
        user.avatar_url = profile.avatar_url
    # Update other fields as needed
```

### 4. Update GitHub Client
Check if `apps/api/src/aic_hub/github.py` fetches all needed fields:

```python
# Ensure GitHubProfile includes all fields
@dataclass
class GitHubProfile:
    id: str
    login: str
    email: str
    name: str | None
    avatar_url: str | None
    bio: str | None
    company: str | None
    location: str | None
```

### 5. Update User Schema
Update `apps/api/src/aic_hub/schemas.py`:

```python
class PublicUser(BaseModel):
    id: UUID
    email: str
    displayName: str | None
    # Add new fields
    username: str | None
    avatarUrl: str | None
    bio: str | None
    company: str | None
    location: str | None
    expertiseTags: list[str]

    class Config:
        alias_generator = to_camel
        populate_by_name = True
```

### 6. Update /me Endpoint
Modify `apps/api/src/aic_hub/routes/me.py`:

```python
@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
) -> PublicUser:
    """Get current authenticated user with extended profile."""
    return PublicUser(
        id=current_user.id,
        email=current_user.email,
        displayName=current_user.display_name,
        username=current_user.username,
        avatarUrl=current_user.avatar_url,
        bio=current_user.bio,
        company=current_user.company,
        location=current_user.location,
        expertiseTags=current_user.expertise_tags or []
    )
```

## Testing Steps

1. **Run Migration**
   ```bash
   cd apps/api
   uv run alembic upgrade head
   ```

2. **Test GitHub OAuth**
   - Clear cookies and database
   - Login with GitHub
   - Check database for populated fields:
   ```sql
   SELECT username, github_username, avatar_url, bio, company, location
   FROM users WHERE email = 'your@email.com';
   ```

3. **Test /me Endpoint**
   ```bash
   curl http://localhost:3000/api/me \
     -H "Cookie: aic_hub_session=..."
   ```

## Success Metrics
- Migration completes without errors
- GitHub profile data populates on OAuth
- /me endpoint returns extended user data
- No existing functionality breaks

## Dependencies
- PostgreSQL with ARRAY support
- Existing auth system working

## Common Issues

### Issue: ARRAY type not working
- Solution: Ensure using PostgreSQL dialect: `from sqlalchemy.dialects.postgresql import ARRAY`

### Issue: GitHub fields not populating
- Solution: Check GitHub OAuth scopes include `read:user`

### Issue: Migration conflicts
- Solution: Check for pending migrations first: `uv run alembic current`

## Notes for AI Agents
- Build on existing auth implementation
- Don't break existing OAuth flow
- Keep expertise_tags as controlled list (see AI_TAGS in PRD)
- Username should be unique but nullable initially