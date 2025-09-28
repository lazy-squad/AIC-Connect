# Task 03: Articles API Implementation

## Objective
Create FastAPI endpoints for article CRUD operations with Tiptap JSON content support, tag filtering, and proper authorization.

## Current State
- Database models will be created (Task 02)
- Authentication will be working (Task 01)
- FastAPI structure exists with auth routes

## Acceptance Criteria
- [ ] Create, read, update, delete articles
- [ ] Rich text content stored as Tiptap JSON
- [ ] Tag filtering and search functionality
- [ ] Author-only edit/delete permissions
- [ ] Published/draft status handling
- [ ] View count tracking

## Implementation Details

### 0. Check Existing Codebase
Before implementing, verify current state:

```bash
# Check for existing article routes
find apps/api/src -name "*.py" | xargs grep -l "article\|Article"

# Check existing route structure
ls -la apps/api/src/aic_hub/routes/
cat apps/api/src/aic_hub/main.py | grep "router"

# Check for existing schemas
ls -la apps/api/src/aic_hub/schemas/

# Check for existing services layer
ls -la apps/api/src/aic_hub/services/

# Check authentication dependencies
cat apps/api/src/aic_hub/dependencies/auth.py 2>/dev/null

# Check if pydantic is installed
grep pydantic apps/api/pyproject.toml

# Check for slug generation libraries
grep -E "slugify|slug" apps/api/pyproject.toml
```

### 1. Article Schemas
Create `apps/api/src/aic_hub/schemas/article.py`:

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: Dict[str, Any]  # Tiptap JSON
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list, max_items=5)
    published: bool = False

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = Field(None, max_items=5)
    published: Optional[bool] = None

class ArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    author_id: UUID
    title: str
    slug: str
    content: Dict[str, Any]
    summary: Optional[str]
    tags: List[str]
    published: bool
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]

    # Nested author info
    author: "UserSummary"

class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    name: str
    avatar_url: Optional[str]
```

### 2. Article Service Layer
Create `apps/api/src/aic_hub/services/article.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import slugify

from ..models import Article, User
from ..schemas.article import ArticleCreate, ArticleUpdate

class ArticleService:
    @staticmethod
    async def create_article(
        db: AsyncSession,
        article_data: ArticleCreate,
        author_id: UUID
    ) -> Article:
        # Generate unique slug
        base_slug = slugify.slugify(article_data.title)
        slug = await ArticleService._generate_unique_slug(db, base_slug)

        # Validate tags against AI_TAGS
        validated_tags = [tag for tag in article_data.tags if tag in AI_TAGS]

        article = Article(
            author_id=author_id,
            title=article_data.title,
            slug=slug,
            content=article_data.content,
            summary=article_data.summary,
            tags=validated_tags,
            published=article_data.published,
            published_at=datetime.utcnow() if article_data.published else None
        )

        db.add(article)
        await db.commit()
        await db.refresh(article)
        return article

    @staticmethod
    async def get_articles(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        tags: Optional[List[str]] = None,
        author_id: Optional[UUID] = None,
        published_only: bool = True
    ) -> List[Article]:
        query = select(Article).options(selectinload(Article.author))

        # Apply filters
        filters = []
        if published_only:
            filters.append(Article.published == True)
        if author_id:
            filters.append(Article.author_id == author_id)
        if tags:
            # Articles must have at least one of the requested tags
            filters.append(Article.tags.overlap(tags))

        if filters:
            query = query.where(and_(*filters))

        # Order by published date or created date
        query = query.order_by(
            Article.published_at.desc().nullsfirst(),
            Article.created_at.desc()
        )

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def increment_view_count(db: AsyncSession, article_id: UUID):
        # Atomic increment
        stmt = (
            update(Article)
            .where(Article.id == article_id)
            .values(view_count=Article.view_count + 1)
        )
        await db.execute(stmt)
        await db.commit()
```

### 3. Article Routes
Create `apps/api/src/aic_hub/routes/articles.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from uuid import UUID

from ..dependencies.auth import get_current_user
from ..dependencies.database import get_db
from ..services.article import ArticleService
from ..schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from ..models import User

router = APIRouter(prefix="/articles", tags=["articles"])

@router.post("/", response_model=ArticleResponse)
async def create_article(
    article: ArticleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new article"""
    article = await ArticleService.create_article(db, article, current_user.id)
    return article

@router.get("/", response_model=List[ArticleResponse])
async def list_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tags: Optional[List[str]] = Query(None),
    author: Optional[str] = Query(None),  # username
    db: AsyncSession = Depends(get_db)
):
    """List published articles with optional filters"""
    author_id = None
    if author:
        user = await db.execute(select(User).where(User.username == author))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "Author not found")
        author_id = user.id

    articles = await ArticleService.get_articles(
        db, skip, limit, tags, author_id, published_only=True
    )
    return articles

@router.get("/drafts", response_model=List[ArticleResponse])
async def list_drafts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List current user's draft articles"""
    articles = await ArticleService.get_articles(
        db, author_id=current_user.id, published_only=False
    )
    return [a for a in articles if not a.published]

@router.get("/{slug}", response_model=ArticleResponse)
async def get_article(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get article by slug"""
    query = select(Article).options(selectinload(Article.author))
    query = query.where(Article.slug == slug)
    result = await db.execute(query)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(404, "Article not found")

    # Increment view count for published articles
    if article.published:
        await ArticleService.increment_view_count(db, article.id)

    return article

@router.patch("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: UUID,
    updates: ArticleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an article (author only)"""
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(404, "Article not found")

    if article.author_id != current_user.id:
        raise HTTPException(403, "Not authorized to edit this article")

    # Apply updates
    for field, value in updates.dict(exclude_unset=True).items():
        if field == "title" and value:
            # Regenerate slug if title changes
            article.slug = await ArticleService._generate_unique_slug(
                db, slugify.slugify(value)
            )
        if field == "published" and value and not article.published:
            article.published_at = datetime.utcnow()
        if field == "tags" and value:
            # Validate against AI_TAGS
            article.tags = [tag for tag in value if tag in AI_TAGS]
        else:
            setattr(article, field, value)

    article.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(article)
    return article

@router.delete("/{article_id}")
async def delete_article(
    article_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an article (author only)"""
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(404, "Article not found")

    if article.author_id != current_user.id:
        raise HTTPException(403, "Not authorized to delete this article")

    await db.delete(article)
    await db.commit()
    return {"message": "Article deleted"}

@router.get("/tags/popular")
async def get_popular_tags(
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get most used tags"""
    # For MVP, return fixed tags with usage counts
    query = select(
        func.unnest(Article.tags).label('tag'),
        func.count('*').label('count')
    ).where(Article.published == True)
    query = query.group_by('tag').order_by(func.count('*').desc()).limit(limit)

    result = await db.execute(query)
    tags = result.all()

    return [{"tag": tag, "count": count} for tag, count in tags]
```

### 4. Add Routes to Main App
Update `apps/api/src/aic_hub/main.py`:
```python
from .routes.articles import router as articles_router

app.include_router(articles_router)
```

### 5. Database Dependencies
Create `apps/api/src/aic_hub/dependencies/database.py`:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import async_session_maker

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
```

## Testing Steps

1. **Create Article**
   ```bash
   curl -X POST http://localhost:3000/api/articles \
     -H "Cookie: session=..." \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Getting Started with RAG",
       "content": {"type": "doc", "content": [...]},
       "tags": ["RAG", "LLMs"],
       "published": false
     }'
   ```

2. **List Articles**
   ```bash
   # All published
   curl http://localhost:3000/api/articles

   # Filter by tags
   curl "http://localhost:3000/api/articles?tags=RAG&tags=LLMs"

   # By author
   curl "http://localhost:3000/api/articles?author=johndoe"
   ```

3. **Update Article**
   ```bash
   curl -X PATCH http://localhost:3000/api/articles/{id} \
     -H "Cookie: session=..." \
     -d '{"published": true}'
   ```

## Success Metrics
- Article creation < 200ms
- List queries < 100ms with indexes
- Slug generation is unique
- View counts increment correctly
- Tag filtering works efficiently

## Dependencies
- Task 01 (Auth) completed
- Task 02 (Models) completed
- Tiptap JSON schema understood

## Common Issues

### Issue: Slug conflicts
- Solution: Add retry logic with counter suffix

### Issue: Large content payloads
- Solution: Set max content size, consider compression

### Issue: Tag validation fails
- Solution: Frontend should use same AI_TAGS list

## Notes for AI Agents
- Don't parse Tiptap JSON, store as-is
- Use PostgreSQL array operations for tag queries
- Keep author info minimal in list responses
- Remember to handle both published and draft states