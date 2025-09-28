# Task 02: Create Database Models

## Objective
Set up SQLAlchemy models and Alembic migrations for all MVP entities: users, articles, spaces, and tags.

## Current State
- Database connection is configured and working
- Alembic is set up but no models exist yet
- User table partially defined in task 01

## Acceptance Criteria
- [ ] All core models are created with proper relationships
- [ ] Alembic migration runs successfully
- [ ] Database schema supports all MVP features
- [ ] Indexes are added for query performance
- [ ] Foreign keys and constraints are properly defined

## Implementation Details

### 0. Check Existing Codebase
Before implementing, verify current state:

```bash
# Check for existing models
find apps/api/src -name "*.py" -type f | xargs grep -l "class.*Base"

# Check database configuration
cat apps/api/src/aic_hub/db.py

# Check if Alembic is configured
cat apps/api/alembic.ini
ls -la apps/api/alembic/versions/

# Check for any existing model files
ls -la apps/api/src/aic_hub/models/

# Check SQLAlchemy version and imports
grep -r "from sqlalchemy" apps/api/src/

# Check dependencies
cat apps/api/pyproject.toml | grep -A 10 dependencies
```

### 1. Create Base Models
Location: `apps/api/src/aic_hub/models/`

Create these model files:
- `user.py` - User profile with GitHub data
- `article.py` - Article with rich text content
- `space.py` - Collaboration spaces
- `tag.py` - Fixed taxonomy tags

### 2. User Model (`user.py`)
```python
class User(Base):
    __tablename__ = "users"

    # Fields from GitHub OAuth
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    github_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)

    # Platform-specific profile
    bio = Column(Text, nullable=True)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    expertise_tags = Column(ARRAY(String), default=[])

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    articles = relationship("Article", back_populates="author")
    spaces = relationship("Space", secondary="space_members", back_populates="members")
```

### 3. Article Model (`article.py`)
```python
class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, nullable=False, index=True)
    content = Column(JSON, nullable=False)  # Tiptap JSON format
    summary = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=[], index=True)
    published = Column(Boolean, default=False, index=True)
    view_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    author = relationship("User", back_populates="articles")

    # Indexes for performance
    __table_args__ = (
        Index('idx_articles_published_created', 'published', 'created_at'),
        Index('idx_articles_author_published', 'author_id', 'published'),
    )
```

### 4. Space Model (`space.py`)
```python
class Space(Base):
    __tablename__ = "spaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(120), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=[], index=True)
    visibility = Column(String(20), default="public")  # public, private
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Metadata
    member_count = Column(Integer, default=1)
    article_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User")
    members = relationship("User", secondary="space_members", back_populates="spaces")
    articles = relationship("SpaceArticle", back_populates="space")

# Association table for space membership
space_members = Table(
    'space_members',
    Base.metadata,
    Column('space_id', UUID(as_uuid=True), ForeignKey('spaces.id'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role', String(20), default='member'),  # owner, moderator, member
    Column('joined_at', DateTime(timezone=True), server_default=func.now())
)

# Association for articles in spaces
class SpaceArticle(Base):
    __tablename__ = "space_articles"

    space_id = Column(UUID(as_uuid=True), ForeignKey('spaces.id'), primary_key=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey('articles.id'), primary_key=True)
    pinned = Column(Boolean, default=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    space = relationship("Space", back_populates="articles")
    article = relationship("Article")
```

### 5. Tag Model (`tag.py`)
```python
# Fixed taxonomy - not a database table, but enum
AI_TAGS = [
    "LLMs", "RAG", "Agents", "Fine-tuning", "Prompting",
    "Vector DBs", "Embeddings", "Training", "Inference",
    "Ethics", "Safety", "Benchmarks", "Datasets", "Tools",
    "Computer Vision", "NLP", "Speech", "Robotics", "RL"
]

# Tag usage tracking (optional for analytics)
class TagUsage(Base):
    __tablename__ = "tag_usage"

    tag = Column(String, primary_key=True)
    article_count = Column(Integer, default=0)
    space_count = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True), server_default=func.now())
```

### 6. Create Alembic Migration
```bash
cd apps/api
uv run alembic revision --autogenerate -m "Add core models for MVP"
```

Review generated migration and ensure:
- All foreign keys are correct
- Indexes are created
- UUID generation works
- Array fields are handled properly

### 7. Run Migration
```bash
uv run alembic upgrade head
```

### 8. Add Model Exports
Update `apps/api/src/aic_hub/models/__init__.py`:
```python
from .user import User
from .article import Article
from .space import Space, SpaceArticle, space_members
from .tag import AI_TAGS, TagUsage

__all__ = [
    "User", "Article", "Space", "SpaceArticle",
    "space_members", "AI_TAGS", "TagUsage"
]
```

## Testing Steps

1. **Migration Test**
   ```bash
   # Down and up to test reversibility
   uv run alembic downgrade -1
   uv run alembic upgrade head
   ```

2. **Model Validation**
   ```python
   # Create test script to verify models
   from aic_hub.models import User, Article, Space
   from aic_hub.db import get_session

   # Test user creation
   # Test article with tags
   # Test space membership
   ```

3. **Query Performance**
   - Check EXPLAIN ANALYZE for common queries
   - Verify indexes are being used
   - Test array field queries for tags

## Success Metrics
- Migration completes in < 5 seconds
- All relationships resolve correctly
- Tag queries use indexes efficiently
- No N+1 query problems in relationships

## Dependencies
- Task 01 must be partially complete (User model basics)
- PostgreSQL with UUID and ARRAY support
- SQLAlchemy 2.0+ for modern syntax

## Common Issues

### Issue: UUID type not found
- Solution: Ensure `uuid-ossp` extension is enabled in PostgreSQL

### Issue: Array fields not working
- Solution: Use PostgreSQL-specific ARRAY type, not generic list

### Issue: Migration fails on foreign keys
- Solution: Create tables in correct order, users first

## Notes for AI Agents
- Keep models simple - no complex inheritance
- Use JSON field for Tiptap content, not separate table
- Don't over-normalize - some denormalization is OK for MVP
- Remember this is PostgreSQL specific, not generic SQL