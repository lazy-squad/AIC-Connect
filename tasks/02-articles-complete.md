# Task 02: Articles Feature - Complete Implementation

## Objective
Implement a full-featured article system with rich text editing (Tiptap), tagging, drafts, and publishing capabilities.

## Scope
- Backend: Article CRUD API, slug generation, view tracking
- Frontend: Tiptap editor, article pages, cards, forms
- Storage: Tiptap JSON format in PostgreSQL

## Dependencies
- **Required**: Task 01 (User profiles for author info)
- **Enables**: Task 04 (Spaces need articles), Task 05 (Feed)

## Backend Implementation

### 1. Database Schema

#### Article Model (`apps/api/src/aic_hub/models/article.py`)
```python
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, nullable=False, index=True)
    content = Column(JSON, nullable=False)  # Tiptap JSON format
    summary = Column(Text, nullable=True)  # Max 500 chars
    tags = Column(ARRAY(String), default=[], nullable=False)
    published = Column(Boolean, default=False, nullable=False, index=True)
    view_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    author = relationship("User", back_populates="articles")

    # Indexes for performance
    __table_args__ = (
        Index('idx_articles_published_created', 'published', 'created_at'),
        Index('idx_articles_author_published', 'author_id', 'published'),
        Index('idx_articles_tags', 'tags', postgresql_using='gin'),
    )
```

#### Migration
```bash
alembic revision --autogenerate -m "Add articles table"
```

### 2. API Endpoints

#### POST /api/articles
**Purpose**: Create new article
**Auth**: Required
**Request**:
```json
{
  "title": "Understanding RAG Systems",
  "content": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [
          {"type": "text", "text": "RAG systems combine..."}
        ]
      }
    ]
  },
  "summary": "An introduction to Retrieval-Augmented Generation",
  "tags": ["RAG", "LLMs", "Vector DBs"],
  "published": false
}
```
**Validation**:
- title: Required, 1-200 chars
- content: Valid Tiptap JSON structure
- summary: Optional, max 500 chars
- tags: Max 5, must be from AI_TAGS
- published: Boolean, sets published_at if true
**Response**: Created article with generated slug

#### GET /api/articles
**Purpose**: List published articles
**Auth**: Optional
**Query Parameters**:
- `tags[]`: Filter by tags (OR condition)
- `author`: Filter by username
- `q`: Search in title/summary
- `skip`: Offset (default: 0)
- `limit`: Page size (default: 20, max: 100)
- `sort`: `latest` (default), `popular`, `trending`
**Response**:
```json
{
  "articles": [
    {
      "id": "uuid",
      "title": "Understanding RAG Systems",
      "slug": "understanding-rag-systems",
      "summary": "An introduction to...",
      "tags": ["RAG", "LLMs"],
      "published": true,
      "viewCount": 150,
      "createdAt": "2024-01-01T00:00:00Z",
      "publishedAt": "2024-01-01T00:00:00Z",
      "author": {
        "id": "uuid",
        "username": "johndoe",
        "displayName": "John Doe",
        "avatarUrl": "https://..."
      }
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

#### GET /api/articles/drafts
**Purpose**: Get current user's draft articles
**Auth**: Required
**Response**: List of unpublished articles by current user

#### GET /api/articles/{slug}
**Purpose**: Get full article by slug
**Auth**: Optional (required for unpublished)
**Response**:
```json
{
  "id": "uuid",
  "title": "Understanding RAG Systems",
  "slug": "understanding-rag-systems",
  "content": { /* Tiptap JSON */ },
  "summary": "An introduction to...",
  "tags": ["RAG", "LLMs"],
  "published": true,
  "viewCount": 151,  // Incremented
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-02T00:00:00Z",
  "publishedAt": "2024-01-01T00:00:00Z",
  "author": {
    "id": "uuid",
    "username": "johndoe",
    "displayName": "John Doe",
    "avatarUrl": "https://...",
    "bio": "AI researcher",
    "expertiseTags": ["RAG", "LLMs"]
  },
  "isAuthor": false  // true if current user is author
}
```
**Side Effects**: Increment view_count for published articles

#### PATCH /api/articles/{id}
**Purpose**: Update article
**Auth**: Required (must be author)
**Request**: Partial update of article fields
**Validation**:
- Can only update own articles
- If changing title, regenerate slug
- If publishing, set published_at
**Response**: Updated article

#### DELETE /api/articles/{id}
**Purpose**: Delete article
**Auth**: Required (must be author)
**Response**: 204 No Content

#### POST /api/articles/{id}/publish
**Purpose**: Publish a draft
**Auth**: Required (must be author)
**Response**: Published article with published_at set

#### POST /api/articles/{id}/unpublish
**Purpose**: Revert to draft
**Auth**: Required (must be author)
**Response**: Article with published=false

### 3. Service Layer (`apps/api/src/aic_hub/services/article_service.py`)

```python
import re
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_, and_

class ArticleService:
    @staticmethod
    async def create_article(
        db: AsyncSession,
        author_id: UUID,
        data: ArticleCreate
    ) -> Article:
        """Create article with unique slug generation"""
        slug = await ArticleService._generate_unique_slug(db, data.title)
        # Validate tags against AI_TAGS
        # Create article
        # Set published_at if published

    @staticmethod
    async def _generate_unique_slug(
        db: AsyncSession,
        title: str,
        existing_id: UUID = None
    ) -> str:
        """Generate unique slug from title"""
        # Slugify title
        # Check uniqueness
        # Append number if needed

    @staticmethod
    async def get_articles(
        db: AsyncSession,
        tags: List[str] = None,
        author_username: str = None,
        search_query: str = None,
        published_only: bool = True,
        skip: int = 0,
        limit: int = 20,
        sort: str = "latest"
    ) -> Tuple[List[Article], int]:
        """Get articles with filters and pagination"""
        # Build query with filters
        # Apply sorting
        # Return articles and total count

    @staticmethod
    async def increment_view_count(
        db: AsyncSession,
        article_id: UUID
    ) -> None:
        """Atomically increment view count"""
        stmt = (
            update(Article)
            .where(Article.id == article_id)
            .values(view_count=Article.view_count + 1)
        )
        await db.execute(stmt)

    @staticmethod
    def validate_tiptap_content(content: dict) -> bool:
        """Validate Tiptap JSON structure"""
        # Check required fields
        # Validate node types
        # Ensure no malicious content
```

### 4. Slug Generation Utility (`apps/api/src/aic_hub/utils/slug.py`)

```python
import re
from unidecode import unidecode

def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to URL-safe slug"""
    # Convert to ASCII
    text = unidecode(text)
    # Lowercase and replace spaces
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    # Truncate
    return text[:max_length].rstrip('-')
```

## Frontend Implementation

### 1. Tiptap Editor Setup

#### Install Dependencies
```json
{
  "dependencies": {
    "@tiptap/react": "^2.1.0",
    "@tiptap/starter-kit": "^2.1.0",
    "@tiptap/extension-link": "^2.1.0",
    "@tiptap/extension-code-block-lowlight": "^2.1.0",
    "@tiptap/extension-placeholder": "^2.1.0",
    "lowlight": "^3.0.0"
  }
}
```

#### Editor Component (`apps/web/src/components/editor/TiptapEditor.tsx`)
```typescript
interface TiptapEditorProps {
  content?: any
  onChange: (content: any) => void
  placeholder?: string
  editable?: boolean
  className?: string
}

// Features:
// - Bold, italic, underline, strike
// - Headings (H2, H3)
// - Lists (bullet, ordered)
// - Blockquote
// - Code blocks with syntax highlighting
// - Links
// - Undo/redo
```

#### Editor Toolbar (`apps/web/src/components/editor/EditorToolbar.tsx`)
```typescript
interface EditorToolbarProps {
  editor: Editor
  variant?: 'full' | 'minimal'
}

// Toolbar buttons with active states
// Keyboard shortcuts display
// Mobile-responsive layout
```

### 2. Article Components

#### ArticleCard (`apps/web/src/components/articles/ArticleCard.tsx`)
```typescript
interface ArticleCardProps {
  article: ArticlePreview
  variant?: 'default' | 'compact' | 'featured'
  showAuthor?: boolean
  onTagClick?: (tag: string) => void
}

// Display:
// - Title with link
// - Summary
// - Author avatar and name
// - Tags
// - View count
// - Published date
```

#### ArticleView (`apps/web/src/components/articles/ArticleView.tsx`)
```typescript
interface ArticleViewProps {
  article: Article
  isAuthor: boolean
  onEdit?: () => void
  onDelete?: () => void
}

// Display:
// - Full article with Tiptap renderer
// - Author card
// - Tags
// - Meta info (views, dates)
// - Edit/delete buttons if author
```

#### ArticleForm (`apps/web/src/components/articles/ArticleForm.tsx`)
```typescript
interface ArticleFormProps {
  article?: Article  // For editing
  onSubmit: (data: ArticleFormData) => Promise<void>
  onCancel: () => void
}

// Fields:
// - Title input
// - Tiptap editor for content
// - Summary textarea
// - Tag selector (max 5)
// - Save as draft checkbox
// - Submit/cancel buttons
// - Validation messages
// - Autosave indicator (future)
```

### 3. Article Pages

#### Create Article (`apps/web/src/app/articles/new/page.tsx`)
**Route**: `/articles/new`
**Features**:
- Protected route
- Article form
- Save as draft
- Publish immediately
- Preview mode
- Success redirect to article

#### View Article (`apps/web/src/app/articles/[slug]/page.tsx`)
**Route**: `/articles/{slug}`
**Features**:
- Fetch article by slug
- Render with Tiptap viewer
- Show author info
- Related articles (by tags)
- Edit button if author
- 404 for unknown slugs
- SEO meta tags

#### Edit Article (`apps/web/src/app/articles/[slug]/edit/page.tsx`)
**Route**: `/articles/{slug}/edit`
**Features**:
- Protected route
- Must be author
- Load existing article
- Update form
- Publish/unpublish toggle
- Delete confirmation
- Success/error handling

#### User Drafts (`apps/web/src/app/drafts/page.tsx`)
**Route**: `/drafts`
**Features**:
- Protected route
- List user's unpublished articles
- Quick actions (edit, delete, publish)
- Empty state
- Sort by updated date

### 4. State Management

#### Article Hooks (`apps/web/src/hooks/useArticle.ts`)
```typescript
// Fetch single article
export function useArticle(slug: string) {
  return useSWR<Article>(
    slug ? `/api/articles/${slug}` : null,
    fetcher
  )
}

// Fetch article list
export function useArticles(params: ArticleQueryParams) {
  const query = new URLSearchParams(params)
  return useSWR<ArticleListResponse>(
    `/api/articles?${query}`,
    fetcher
  )
}

// User's drafts
export function useDrafts() {
  return useSWR<Article[]>(
    '/api/articles/drafts',
    fetcher
  )
}

// Article mutations
export function useCreateArticle() {
  const router = useRouter()
  return useSWRMutation(
    '/api/articles',
    createArticle,
    {
      onSuccess: (article) => {
        router.push(`/articles/${article.slug}`)
      }
    }
  )
}
```

### 5. Types (`apps/web/src/types/article.ts`)
```typescript
interface Article {
  id: string
  title: string
  slug: string
  content: any  // Tiptap JSON
  summary?: string
  tags: string[]
  published: boolean
  viewCount: number
  createdAt: string
  updatedAt?: string
  publishedAt?: string
  author: UserSummary
  isAuthor?: boolean
}

interface ArticleFormData {
  title: string
  content: any
  summary?: string
  tags: string[]
  published: boolean
}

interface ArticleQueryParams {
  tags?: string[]
  author?: string
  q?: string
  skip?: number
  limit?: number
  sort?: 'latest' | 'popular' | 'trending'
}
```

## Integration Points

### Navigation Updates
- "Write" button in nav (authenticated)
- "My Drafts" in user menu
- Article count in user profile

### User Profile Integration
- Show user's articles on profile
- Article count stat
- Link from article to author

### Feed Integration (Task 05)
- Articles appear in main feed
- Filter by tags
- Sort options

### Space Integration (Task 04)
- Share articles to spaces
- Space article lists

## Testing Requirements

### Backend Tests
```python
# test_articles.py
async def test_create_article()
async def test_slug_generation()
async def test_get_articles_with_filters()
async def test_get_article_by_slug()
async def test_update_own_article()
async def test_cannot_update_others_article()
async def test_delete_article()
async def test_publish_unpublish()
async def test_view_count_increment()
async def test_tag_validation()
async def test_search_articles()
```

### Frontend Tests
```typescript
// TiptapEditor.test.tsx
test('renders editor with toolbar')
test('handles content changes')
test('applies formatting')

// ArticleForm.test.tsx
test('validates required fields')
test('limits tags to 5')
test('handles submit')
test('shows validation errors')

// Article pages
test('creates new article')
test('displays article content')
test('only author can edit')
test('404 for unknown article')
```

### E2E Tests
```typescript
test('Complete article flow', async () => {
  // 1. Login
  // 2. Create article as draft
  // 3. Edit draft
  // 4. Publish article
  // 5. View published article
  // 6. Update article
  // 7. View count increases
})
```

## Error Handling

### Backend Errors
- 400: Invalid title/content
- 400: Too many tags
- 401: Authentication required
- 403: Not article author
- 404: Article not found
- 409: Slug conflict (handled internally)

### Frontend Error States
- Network errors: Show retry
- Validation errors: Inline messages
- Save failures: Toast notification
- Not found: 404 page
- Unauthorized: Redirect to login

## Performance Considerations

### Backend
- Slug indexed for fast lookup
- GIN index for tag searches
- Pagination on all lists
- View count atomic increment
- Lazy load article content

### Frontend
- Lazy load Tiptap editor
- Code splitting for editor bundle
- Image optimization in content
- SWR caching for articles
- Debounce search input

## Security Considerations
- Sanitize Tiptap content
- Validate JSON structure
- XSS prevention in rendering
- Rate limit article creation
- CSRF protection on mutations
- Only authors can edit/delete
- Drafts private to author

## Acceptance Criteria
- [ ] Article model and migration created
- [ ] CRUD API endpoints working
- [ ] Slug generation is unique
- [ ] View counting works
- [ ] Tiptap editor integrated
- [ ] Article creation flow works
- [ ] Article display renders correctly
- [ ] Edit only by author
- [ ] Draft/publish states work
- [ ] Tag filtering works
- [ ] Search functionality works
- [ ] Tests pass
- [ ] No XSS vulnerabilities

## Implementation Order
1. Backend: Create model and migration
2. Backend: Implement CRUD endpoints
3. Backend: Add search and filters
4. Frontend: Setup Tiptap editor
5. Frontend: Create article components
6. Frontend: Implement pages
7. Frontend: Add state management
8. Testing: Write and run tests
9. Integration: Full flow testing

## Notes for AI Agents
- Use python-slugify for slug generation
- Store Tiptap JSON as-is, don't parse
- Validate tags against AI_TAGS constant
- Use transactions for article creation
- Handle slug conflicts gracefully
- Test with various content types
- Ensure mobile responsiveness
- Keep editor bundle size optimized