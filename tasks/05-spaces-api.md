# Task 05: Collaboration Spaces API

## Objective
Build API endpoints for creating and managing collaboration spaces where users can share articles and discussions around specific AI topics.

## Current State
- Database models defined (Task 02)
- User authentication working
- Articles API exists

## Acceptance Criteria
- [ ] Create and manage spaces
- [ ] Join/leave spaces
- [ ] Share articles to spaces
- [ ] List space members
- [ ] Space-specific article feeds
- [ ] Owner/member permissions

## Implementation Details

### 0. Check Existing Codebase
Before implementing, verify current state:

```bash
# Check for existing space-related code
find apps/api/src -name "*.py" | xargs grep -l "space\|Space"

# Check existing routes structure
ls -la apps/api/src/aic_hub/routes/

# Check if space model exists from Task 02
cat apps/api/src/aic_hub/models/space.py 2>/dev/null

# Check for association tables
find apps/api/src -name "*.py" | xargs grep -l "space_members\|SpaceArticle"

# Check existing service layer
ls -la apps/api/src/aic_hub/services/

# Check for slug utilities
grep -r "slugify" apps/api/src/

# Check database relationships
find apps/api/src -name "*.py" | xargs grep -l "relationship\|secondary"
```

### 1. Space Schemas
Create `apps/api/src/aic_hub/schemas/space.py`:

```python
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import List, Optional, Literal
from datetime import datetime
from uuid import UUID

class SpaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tags: List[str] = Field(default_factory=list, max_items=5)
    visibility: Literal["public", "private"] = "public"

    @validator('tags')
    def validate_tags(cls, v):
        from ..models import AI_TAGS
        return [tag for tag in v if tag in AI_TAGS]

class SpaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = Field(None, max_items=5)
    visibility: Optional[Literal["public", "private"]] = None

class SpaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: Optional[str]
    tags: List[str]
    visibility: str
    owner_id: UUID
    member_count: int
    article_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    # Nested owner info
    owner: "UserSummary"
    # User's membership status (computed)
    is_member: bool = False
    member_role: Optional[str] = None

class SpaceMember(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    username: str
    name: str
    avatar_url: Optional[str]
    role: str
    joined_at: datetime

class SpaceArticle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    article_id: UUID
    title: str
    slug: str
    summary: Optional[str]
    author: "UserSummary"
    pinned: bool
    added_at: datetime

from ..schemas.user import UserSummary  # Import from user schemas
```

### 2. Space Service
Create `apps/api/src/aic_hub/services/space.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from typing import List, Optional
from uuid import UUID
import slugify

from ..models import Space, User, space_members, SpaceArticle, Article

class SpaceService:
    @staticmethod
    async def create_space(
        db: AsyncSession,
        space_data: SpaceCreate,
        owner_id: UUID
    ) -> Space:
        # Generate unique slug
        base_slug = slugify.slugify(space_data.name)
        slug = await SpaceService._generate_unique_slug(db, base_slug)

        space = Space(
            name=space_data.name,
            slug=slug,
            description=space_data.description,
            tags=space_data.tags,
            visibility=space_data.visibility,
            owner_id=owner_id,
            member_count=1
        )

        db.add(space)
        await db.flush()

        # Add owner as first member
        stmt = space_members.insert().values(
            space_id=space.id,
            user_id=owner_id,
            role="owner"
        )
        await db.execute(stmt)

        await db.commit()
        await db.refresh(space)
        return space

    @staticmethod
    async def join_space(
        db: AsyncSession,
        space_id: UUID,
        user_id: UUID,
        role: str = "member"
    ) -> bool:
        # Check if already member
        existing = await db.scalar(
            select(space_members.c.user_id)
            .where(and_(
                space_members.c.space_id == space_id,
                space_members.c.user_id == user_id
            ))
        )
        if existing:
            return False

        # Add membership
        stmt = space_members.insert().values(
            space_id=space_id,
            user_id=user_id,
            role=role
        )
        await db.execute(stmt)

        # Update member count
        stmt = (
            update(Space)
            .where(Space.id == space_id)
            .values(member_count=Space.member_count + 1)
        )
        await db.execute(stmt)

        await db.commit()
        return True

    @staticmethod
    async def leave_space(
        db: AsyncSession,
        space_id: UUID,
        user_id: UUID
    ) -> bool:
        # Check if owner
        space = await db.get(Space, space_id)
        if space.owner_id == user_id:
            raise ValueError("Owner cannot leave space")

        # Remove membership
        stmt = delete(space_members).where(and_(
            space_members.c.space_id == space_id,
            space_members.c.user_id == user_id
        ))
        result = await db.execute(stmt)

        if result.rowcount > 0:
            # Update member count
            stmt = (
                update(Space)
                .where(Space.id == space_id)
                .values(member_count=Space.member_count - 1)
            )
            await db.execute(stmt)
            await db.commit()
            return True

        return False

    @staticmethod
    async def add_article_to_space(
        db: AsyncSession,
        space_id: UUID,
        article_id: UUID,
        user_id: UUID
    ) -> SpaceArticle:
        # Verify user is member
        is_member = await db.scalar(
            select(space_members.c.user_id)
            .where(and_(
                space_members.c.space_id == space_id,
                space_members.c.user_id == user_id
            ))
        )
        if not is_member:
            raise ValueError("User is not a member of this space")

        # Check if article already in space
        existing = await db.get(SpaceArticle, {"space_id": space_id, "article_id": article_id})
        if existing:
            raise ValueError("Article already in space")

        # Add article to space
        space_article = SpaceArticle(
            space_id=space_id,
            article_id=article_id,
            pinned=False
        )
        db.add(space_article)

        # Update article count
        stmt = (
            update(Space)
            .where(Space.id == space_id)
            .values(article_count=Space.article_count + 1)
        )
        await db.execute(stmt)

        await db.commit()
        await db.refresh(space_article)
        return space_article
```

### 3. Space Routes
Create `apps/api/src/aic_hub/routes/spaces.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID

from ..dependencies.auth import get_current_user, get_optional_user
from ..dependencies.database import get_db
from ..services.space import SpaceService
from ..schemas.space import SpaceCreate, SpaceUpdate, SpaceResponse, SpaceMember, SpaceArticle
from ..models import Space, User, space_members, Article

router = APIRouter(prefix="/spaces", tags=["spaces"])

@router.post("/", response_model=SpaceResponse)
async def create_space(
    space_data: SpaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new collaboration space"""
    space = await SpaceService.create_space(db, space_data, current_user.id)

    # Load owner info
    await db.refresh(space, ["owner"])

    response = SpaceResponse.model_validate(space)
    response.is_member = True
    response.member_role = "owner"
    return response

@router.get("/", response_model=List[SpaceResponse])
async def list_spaces(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tags: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None),
    my_spaces: bool = Query(False),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """List spaces with optional filters"""
    query = select(Space).options(selectinload(Space.owner))

    filters = []

    # Filter by visibility (only show private if member)
    if not my_spaces:
        filters.append(Space.visibility == "public")

    # Filter by tags
    if tags:
        filters.append(Space.tags.overlap(tags))

    # Search in name and description
    if search:
        search_pattern = f"%{search}%"
        filters.append(
            or_(
                Space.name.ilike(search_pattern),
                Space.description.ilike(search_pattern)
            )
        )

    # My spaces only
    if my_spaces and current_user:
        subquery = select(space_members.c.space_id).where(
            space_members.c.user_id == current_user.id
        )
        filters.append(Space.id.in_(subquery))

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Space.member_count.desc(), Space.created_at.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    spaces = result.scalars().all()

    # Add membership info if user is authenticated
    responses = []
    for space in spaces:
        response = SpaceResponse.model_validate(space)

        if current_user:
            # Check membership
            membership = await db.execute(
                select(space_members.c.role)
                .where(and_(
                    space_members.c.space_id == space.id,
                    space_members.c.user_id == current_user.id
                ))
            )
            role = membership.scalar_one_or_none()
            response.is_member = role is not None
            response.member_role = role

        responses.append(response)

    return responses

@router.get("/{slug}", response_model=SpaceResponse)
async def get_space(
    slug: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """Get space details by slug"""
    space = await db.scalar(
        select(Space)
        .options(selectinload(Space.owner))
        .where(Space.slug == slug)
    )

    if not space:
        raise HTTPException(404, "Space not found")

    # Check access for private spaces
    if space.visibility == "private":
        if not current_user:
            raise HTTPException(403, "Authentication required")

        is_member = await db.scalar(
            select(space_members.c.user_id)
            .where(and_(
                space_members.c.space_id == space.id,
                space_members.c.user_id == current_user.id
            ))
        )
        if not is_member:
            raise HTTPException(403, "Private space - members only")

    response = SpaceResponse.model_validate(space)

    if current_user:
        membership = await db.execute(
            select(space_members.c.role)
            .where(and_(
                space_members.c.space_id == space.id,
                space_members.c.user_id == current_user.id
            ))
        )
        role = membership.scalar_one_or_none()
        response.is_member = role is not None
        response.member_role = role

    return response

@router.post("/{space_id}/join")
async def join_space(
    space_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Join a space"""
    space = await db.get(Space, space_id)
    if not space:
        raise HTTPException(404, "Space not found")

    success = await SpaceService.join_space(db, space_id, current_user.id)
    if not success:
        raise HTTPException(400, "Already a member")

    return {"message": "Joined space successfully"}

@router.post("/{space_id}/leave")
async def leave_space(
    space_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Leave a space"""
    try:
        success = await SpaceService.leave_space(db, space_id, current_user.id)
        if not success:
            raise HTTPException(400, "Not a member")
    except ValueError as e:
        raise HTTPException(400, str(e))

    return {"message": "Left space successfully"}

@router.get("/{space_id}/members", response_model=List[SpaceMember])
async def get_space_members(
    space_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get space members"""
    # Get members with user info
    stmt = (
        select(
            User.id,
            User.username,
            User.name,
            User.avatar_url,
            space_members.c.role,
            space_members.c.joined_at
        )
        .join(space_members, User.id == space_members.c.user_id)
        .where(space_members.c.space_id == space_id)
        .order_by(space_members.c.joined_at)
    )

    result = await db.execute(stmt)
    members = result.all()

    return [
        SpaceMember(
            user_id=m[0],
            username=m[1],
            name=m[2],
            avatar_url=m[3],
            role=m[4],
            joined_at=m[5]
        )
        for m in members
    ]

@router.post("/{space_id}/articles")
async def add_article_to_space(
    space_id: UUID,
    article_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Share an article to a space"""
    try:
        space_article = await SpaceService.add_article_to_space(
            db, space_id, article_id, current_user.id
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    return {"message": "Article added to space"}

@router.get("/{space_id}/articles", response_model=List[SpaceArticle])
async def get_space_articles(
    space_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get articles in a space"""
    # Get articles with info
    stmt = (
        select(SpaceArticle, Article, User)
        .join(Article, SpaceArticle.article_id == Article.id)
        .join(User, Article.author_id == User.id)
        .where(SpaceArticle.space_id == space_id)
        .order_by(SpaceArticle.pinned.desc(), SpaceArticle.added_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    items = result.all()

    responses = []
    for space_article, article, author in items:
        responses.append(SpaceArticle(
            article_id=article.id,
            title=article.title,
            slug=article.slug,
            summary=article.summary,
            author=UserSummary(
                id=author.id,
                username=author.username,
                name=author.name,
                avatar_url=author.avatar_url
            ),
            pinned=space_article.pinned,
            added_at=space_article.added_at
        ))

    return responses
```

### 4. Add Optional User Dependency
Create `apps/api/src/aic_hub/dependencies/auth.py` addition:

```python
async def get_optional_user(
    session_token: str = Cookie(None, alias=settings.session_cookie.name),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not session_token:
        return None

    try:
        payload = jwt.decode(
            session_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id = UUID(payload.get("sub"))
        user = await db.get(User, user_id)
        return user
    except:
        return None
```

### 5. Add Routes to Main App
Update `apps/api/src/aic_hub/main.py`:
```python
from .routes.spaces import router as spaces_router

app.include_router(spaces_router)
```

## Testing Steps

1. **Create Space**
   ```bash
   curl -X POST http://localhost:3000/api/spaces \
     -H "Cookie: session=..." \
     -d '{
       "name": "RAG Enthusiasts",
       "description": "Discussing RAG implementations",
       "tags": ["RAG", "Vector DBs"]
     }'
   ```

2. **Join Space**
   ```bash
   curl -X POST http://localhost:3000/api/spaces/{space_id}/join \
     -H "Cookie: session=..."
   ```

3. **Share Article**
   ```bash
   curl -X POST http://localhost:3000/api/spaces/{space_id}/articles \
     -H "Cookie: session=..." \
     -d '{"article_id": "..."}'
   ```

4. **List Space Articles**
   ```bash
   curl http://localhost:3000/api/spaces/{space_id}/articles
   ```

## Success Metrics
- Space creation < 200ms
- Member operations < 100ms
- Article sharing immediate
- Proper permission checks

## Dependencies
- Tasks 01-04 completed
- User and Article models exist

## Common Issues

### Issue: Slug conflicts
- Solution: Add counter suffix for uniqueness

### Issue: Owner leaves space
- Solution: Prevent owner from leaving

### Issue: Private space access
- Solution: Check membership before showing

## Notes for AI Agents
- Keep permissions simple: owner, member
- Don't implement invites for MVP
- Use slug for URLs, not UUID
- Denormalize counts for performance