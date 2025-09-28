# Task 04: User Profiles API

## Objective
Implement user profile endpoints for viewing and editing profiles, with expertise tags and platform-specific bio support.

## Current State
- User model exists with GitHub data (Task 01 & 02)
- Authentication is working
- `/me` endpoint returns 401

## Acceptance Criteria
- [ ] Get current user profile (`/me`)
- [ ] Get any user's public profile
- [ ] Update own profile (bio, expertise, etc.)
- [ ] List users with filtering
- [ ] Expertise tag management

## Implementation Details

### 0. Check Existing Codebase
Before implementing, verify current state:

```bash
# Check existing /me route
cat apps/api/src/aic_hub/routes/me.py

# Check for user-related routes
find apps/api/src -name "*.py" | xargs grep -l "user\|User"

# Check existing schemas
ls -la apps/api/src/aic_hub/schemas/
find apps/api/src -name "*.py" | xargs grep -l "UserProfile\|UserSchema"

# Check authentication setup
cat apps/api/src/aic_hub/dependencies/auth.py 2>/dev/null

# Check if user model exists
cat apps/api/src/aic_hub/models/user.py 2>/dev/null

# Check main app for included routers
cat apps/api/src/aic_hub/main.py | grep -A 5 "include_router"
```

### 1. User Schemas
Create `apps/api/src/aic_hub/schemas/user.py`:

```python
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    name: str
    email: Optional[str] = None  # Only visible to self
    avatar_url: Optional[str]
    bio: Optional[str]
    company: Optional[str]
    location: Optional[str]
    expertise_tags: List[str]
    github_id: str
    created_at: datetime

    # Computed fields
    article_count: int = 0
    space_count: int = 0

class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    company: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    expertise_tags: Optional[List[str]] = Field(None, max_items=10)

    @validator('expertise_tags')
    def validate_expertise_tags(cls, v):
        if v is not None:
            from ..models import AI_TAGS
            return [tag for tag in v if tag in AI_TAGS]
        return v

class UserPublicProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    name: str
    avatar_url: Optional[str]
    bio: Optional[str]
    company: Optional[str]
    location: Optional[str]
    expertise_tags: List[str]
    created_at: datetime
    article_count: int = 0
    space_count: int = 0
```

### 2. Update /me Route
Update `apps/api/src/aic_hub/routes/me.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..dependencies.auth import get_current_user
from ..dependencies.database import get_db
from ..schemas.user import UserProfile, UserProfileUpdate
from ..models import User, Article, space_members

router = APIRouter(tags=["user"])

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user's profile"""
    # Get article count
    article_count = await db.scalar(
        select(func.count(Article.id))
        .where(Article.author_id == current_user.id)
        .where(Article.published == True)
    )

    # Get space count
    space_count = await db.scalar(
        select(func.count(space_members.c.space_id))
        .where(space_members.c.user_id == current_user.id)
    )

    response = UserProfile.model_validate(current_user)
    response.article_count = article_count or 0
    response.space_count = space_count or 0

    return response

@router.patch("/me", response_model=UserProfile)
async def update_current_user_profile(
    updates: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    # Apply updates
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)

    # Get counts for response
    article_count = await db.scalar(
        select(func.count(Article.id))
        .where(Article.author_id == current_user.id)
        .where(Article.published == True)
    )

    space_count = await db.scalar(
        select(func.count(space_members.c.space_id))
        .where(space_members.c.user_id == current_user.id)
    )

    response = UserProfile.model_validate(current_user)
    response.article_count = article_count or 0
    response.space_count = space_count or 0

    return response
```

### 3. Public User Routes
Create `apps/api/src/aic_hub/routes/users.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional

from ..dependencies.database import get_db
from ..schemas.user import UserPublicProfile
from ..models import User, Article, space_members, AI_TAGS

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{username}", response_model=UserPublicProfile)
async def get_user_profile(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a user's public profile"""
    user = await db.scalar(
        select(User).where(User.username == username)
    )

    if not user:
        raise HTTPException(404, "User not found")

    # Get counts
    article_count = await db.scalar(
        select(func.count(Article.id))
        .where(Article.author_id == user.id)
        .where(Article.published == True)
    )

    space_count = await db.scalar(
        select(func.count(space_members.c.space_id))
        .where(space_members.c.user_id == user.id)
    )

    response = UserPublicProfile.model_validate(user)
    response.article_count = article_count or 0
    response.space_count = space_count or 0

    return response

@router.get("/", response_model=List[UserPublicProfile])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    expertise: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List users with optional filters"""
    query = select(User)

    # Apply filters
    filters = []
    if expertise:
        # Users with any of the specified expertise tags
        valid_tags = [tag for tag in expertise if tag in AI_TAGS]
        if valid_tags:
            filters.append(User.expertise_tags.overlap(valid_tags))

    if search:
        # Search in username, name, bio
        search_pattern = f"%{search}%"
        filters.append(
            or_(
                User.username.ilike(search_pattern),
                User.name.ilike(search_pattern),
                User.bio.ilike(search_pattern)
            )
        )

    if filters:
        query = query.where(and_(*filters))

    # Order by creation date (newest first)
    query = query.order_by(User.created_at.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    users = result.scalars().all()

    # Get counts for each user (could be optimized with a join)
    responses = []
    for user in users:
        article_count = await db.scalar(
            select(func.count(Article.id))
            .where(Article.author_id == user.id)
            .where(Article.published == True)
        )

        space_count = await db.scalar(
            select(func.count(space_members.c.space_id))
            .where(space_members.c.user_id == user.id)
        )

        response = UserPublicProfile.model_validate(user)
        response.article_count = article_count or 0
        response.space_count = space_count or 0
        responses.append(response)

    return responses

@router.get("/expertise/stats")
async def get_expertise_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get statistics about expertise tag usage"""
    # Count users per expertise tag
    stats = []
    for tag in AI_TAGS:
        count = await db.scalar(
            select(func.count(User.id))
            .where(User.expertise_tags.contains([tag]))
        )
        if count > 0:
            stats.append({"tag": tag, "user_count": count})

    # Sort by count
    stats.sort(key=lambda x: x["user_count"], reverse=True)
    return stats
```

### 4. Add Routes to Main App
Update `apps/api/src/aic_hub/main.py`:
```python
from .routes.users import router as users_router

app.include_router(users_router)
```

### 5. Update Auth Dependency
Update `apps/api/src/aic_hub/dependencies/auth.py`:

```python
from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from uuid import UUID

from ..config import settings
from ..models import User
from .database import get_db

async def get_current_user(
    session_token: str = Cookie(None, alias=settings.session_cookie.name),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Validate JWT token and return current user"""
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Decode JWT
        payload = jwt.decode(
            session_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id = UUID(payload.get("sub"))

        # Fetch user from database
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
```

## Testing Steps

1. **Get Current User Profile**
   ```bash
   curl http://localhost:3000/api/me \
     -H "Cookie: session=..."
   ```

2. **Update Profile**
   ```bash
   curl -X PATCH http://localhost:3000/api/me \
     -H "Cookie: session=..." \
     -d '{
       "bio": "AI researcher focused on RAG systems",
       "expertise_tags": ["RAG", "LLMs", "Vector DBs"]
     }'
   ```

3. **Get Public Profile**
   ```bash
   curl http://localhost:3000/api/users/johndoe
   ```

4. **Search Users**
   ```bash
   # By expertise
   curl "http://localhost:3000/api/users?expertise=RAG&expertise=LLMs"

   # By search term
   curl "http://localhost:3000/api/users?search=researcher"
   ```

## Success Metrics
- Profile loads in < 100ms
- Updates apply immediately
- Expertise tags properly validated
- Search queries use indexes

## Dependencies
- Task 01 & 02 completed (Auth & Models)
- User exists in database

## Common Issues

### Issue: Email exposed in public profile
- Solution: UserPublicProfile schema excludes email

### Issue: Invalid expertise tags saved
- Solution: Validator filters against AI_TAGS

### Issue: Count queries slow
- Solution: Consider denormalizing counts in User table

## Notes for AI Agents
- Keep profile data minimal for MVP
- Don't expose sensitive data (email, github_id) publicly
- Validate all expertise tags against fixed list
- Consider caching user counts for performance