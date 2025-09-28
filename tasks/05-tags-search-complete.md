# Task 05: Tag System & Search - Complete Implementation

## Objective
Implement a comprehensive tag system with fixed AI taxonomy and powerful search capabilities across articles, spaces, and users.

## Scope
- Backend: Tag management, search APIs, indexing
- Frontend: Tag components, search interface, filters
- Search: Full-text search with PostgreSQL

## Dependencies
- **Required**: Task 02 (Articles have tags), Task 03 (Spaces have tags)
- **Enhances**: Task 04 (Feed filtering), All content discovery

## Fixed AI Taxonomy
```typescript
const AI_TAGS = [
  // Core AI/ML
  "LLMs",           // Large Language Models
  "RAG",            // Retrieval-Augmented Generation
  "Agents",         // AI Agents & Multi-agent systems
  "Fine-tuning",    // Model fine-tuning
  "Prompting",      // Prompt engineering

  // Infrastructure
  "Vector DBs",     // Vector databases
  "Embeddings",     // Embedding models & techniques
  "Training",       // Model training
  "Inference",      // Model inference & deployment

  // Governance
  "Ethics",         // AI ethics
  "Safety",         // AI safety & alignment
  "Benchmarks",     // Evaluation & benchmarks
  "Datasets",       // Datasets & data preparation
  "Tools",          // AI tools & frameworks

  // Applications
  "Computer Vision", // CV applications
  "NLP",            // Natural Language Processing
  "Speech",         // Speech recognition & synthesis
  "Robotics",       // Robotics & embodied AI
  "RL"              // Reinforcement Learning
]
```

## Backend Implementation

### 1. Database Schema

#### TagUsage Model (`apps/api/src/aic_hub/models/tag_usage.py`)
```python
class TagUsage(Base):
    __tablename__ = "tag_usage"

    tag = Column(String(50), primary_key=True)
    article_count = Column(Integer, default=0, nullable=False)
    space_count = Column(Integer, default=0, nullable=False)
    user_count = Column(Integer, default=0, nullable=False)  # Users with this expertise
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    trending_score = Column(Float, default=0.0, nullable=False)
    week_count = Column(Integer, default=0, nullable=False)  # Usage this week
    month_count = Column(Integer, default=0, nullable=False)  # Usage this month

    # Indexes
    __table_args__ = (
        Index('idx_tag_usage_trending', 'trending_score'),
        Index('idx_tag_usage_counts', 'article_count', 'space_count', 'user_count'),
    )
```

#### SearchIndex Table (`apps/api/src/aic_hub/models/search_index.py`)
```python
class SearchIndex(Base):
    __tablename__ = "search_index"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type = Column(String(20), nullable=False)  # article, space, user
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=[], nullable=False)
    search_vector = Column(TSVectorType, nullable=False)  # PostgreSQL full-text search
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_search_vector', 'search_vector', postgresql_using='gin'),
        Index('idx_search_entity', 'entity_type', 'entity_id'),
        Index('idx_search_tags', 'tags', postgresql_using='gin'),
    )
```

### 2. API Endpoints

#### GET /api/tags
**Purpose**: Get all tags with usage stats
**Auth**: Optional
**Query Parameters**:
- `sort`: `alphabetical`, `popular`, `trending`
- `category`: `all`, `with_content`, `with_experts`
- `limit`: Max results
**Response**:
```json
{
  "tags": [
    {
      "name": "RAG",
      "description": "Retrieval-Augmented Generation",
      "stats": {
        "articles": 45,
        "spaces": 8,
        "experts": 23,
        "totalUsage": 76,
        "weeklyGrowth": "+15%",
        "trendingScore": 85.5
      },
      "related": ["Vector DBs", "LLMs", "Embeddings"]
    }
  ]
}
```

#### GET /api/tags/{tag}
**Purpose**: Get detailed tag information
**Auth**: Optional
**Response**:
```json
{
  "name": "RAG",
  "description": "Retrieval-Augmented Generation combines...",
  "stats": { /* usage stats */ },
  "topArticles": [ /* top 5 articles */ ],
  "topSpaces": [ /* top 3 spaces */ ],
  "topExperts": [ /* top 5 users */ ],
  "relatedTags": ["Vector DBs", "LLMs"],
  "trendHistory": [
    {"date": "2024-01-01", "count": 12},
    {"date": "2024-01-02", "count": 15}
  ]
}
```

#### GET /api/tags/suggest
**Purpose**: Get tag suggestions based on content
**Auth**: Required
**Request**:
```json
{
  "title": "Building RAG Systems with LangChain",
  "content": "This article discusses..."
}
```
**Response**:
```json
{
  "suggestedTags": ["RAG", "LLMs", "Tools"],
  "confidence": {
    "RAG": 0.95,
    "LLMs": 0.87,
    "Tools": 0.72
  }
}
```

#### GET /api/search
**Purpose**: Universal search across platform
**Auth**: Optional
**Query Parameters**:
- `q`: Search query (required)
- `type`: `all`, `articles`, `spaces`, `users`
- `tags[]`: Filter by tags
- `sort`: `relevance`, `latest`, `popular`
- `skip`: Offset
- `limit`: Page size
**Response**:
```json
{
  "results": [
    {
      "type": "article",
      "score": 0.95,
      "item": {
        "id": "uuid",
        "title": "Understanding RAG Systems",
        "slug": "understanding-rag-systems",
        "summary": "...",
        "tags": ["RAG"],
        "highlights": {
          "title": "Understanding <mark>RAG</mark> Systems",
          "content": "...<mark>RAG</mark> combines retrieval..."
        }
      }
    },
    {
      "type": "space",
      "score": 0.82,
      "item": { /* SpaceSummary */ }
    },
    {
      "type": "user",
      "score": 0.75,
      "item": { /* UserSummary */ }
    }
  ],
  "total": 42,
  "facets": {
    "types": {
      "articles": 25,
      "spaces": 10,
      "users": 7
    },
    "tags": {
      "RAG": 15,
      "LLMs": 12,
      "Vector DBs": 8
    }
  },
  "skip": 0,
  "limit": 20,
  "processingTime": 45  // milliseconds
}
```

#### GET /api/search/autocomplete
**Purpose**: Search suggestions as user types
**Auth**: Optional
**Query Parameters**:
- `q`: Partial query (min 2 chars)
- `limit`: Max suggestions (default: 5)
**Response**:
```json
{
  "suggestions": [
    {
      "type": "query",
      "text": "RAG implementation",
      "count": 15
    },
    {
      "type": "tag",
      "text": "RAG",
      "count": 45
    },
    {
      "type": "user",
      "text": "rag-expert",
      "user": { /* UserSummary */ }
    }
  ]
}
```

#### POST /api/search/index
**Purpose**: Manually trigger search index update
**Auth**: Admin only
**Response**: 202 Accepted

### 3. Service Layer

#### TagService (`apps/api/src/aic_hub/services/tag_service.py`)
```python
class TagService:
    # Tag descriptions mapping
    TAG_DESCRIPTIONS = {
        "LLMs": "Large Language Models - Foundation models like GPT, Claude, LLaMA",
        "RAG": "Retrieval-Augmented Generation - Combining retrieval with generation",
        # ... all tags
    }

    # Related tags mapping
    TAG_RELATIONSHIPS = {
        "RAG": ["Vector DBs", "Embeddings", "LLMs"],
        "Agents": ["LLMs", "Tools", "Prompting"],
        # ... relationships
    }

    @staticmethod
    async def update_tag_usage(
        db: AsyncSession,
        tag: str,
        entity_type: str,
        delta: int = 1
    ) -> None:
        """Update tag usage counts"""

    @staticmethod
    async def calculate_trending_scores(
        db: AsyncSession
    ) -> None:
        """Calculate trending scores for all tags"""

    @staticmethod
    async def get_related_tags(
        tag: str,
        limit: int = 5
    ) -> List[str]:
        """Get related tags based on co-occurrence"""

    @staticmethod
    async def suggest_tags(
        title: str,
        content: str,
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """Suggest tags using NLP analysis"""
        # Simple keyword matching for MVP
        # Future: Use embeddings for semantic matching
```

#### SearchService (`apps/api/src/aic_hub/services/search_service.py`)
```python
from sqlalchemy import func, select, or_, and_

class SearchService:
    @staticmethod
    async def search(
        db: AsyncSession,
        query: str,
        search_type: str = "all",
        tags: List[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> SearchResponse:
        """
        Full-text search using PostgreSQL
        """
        # Build search query
        search_vector = func.to_tsquery('english', query)

        # Search articles
        if search_type in ["all", "articles"]:
            articles = await SearchService._search_articles(
                db, search_vector, tags
            )

        # Search spaces
        if search_type in ["all", "spaces"]:
            spaces = await SearchService._search_spaces(
                db, search_vector, tags
            )

        # Search users
        if search_type in ["all", "users"]:
            users = await SearchService._search_users(
                db, query, tags
            )

        # Combine and rank results
        return SearchService._rank_results(
            articles, spaces, users, skip, limit
        )

    @staticmethod
    async def update_search_index(
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID,
        title: str,
        content: str,
        tags: List[str]
    ) -> None:
        """Update search index for entity"""
        # Generate search vector
        search_text = f"{title} {content} {' '.join(tags)}"
        search_vector = func.to_tsvector('english', search_text)

        # Upsert index entry
        # ...

    @staticmethod
    async def autocomplete(
        db: AsyncSession,
        query: str,
        limit: int = 5
    ) -> List[Suggestion]:
        """Generate autocomplete suggestions"""
        suggestions = []

        # Tag suggestions
        matching_tags = [
            tag for tag in AI_TAGS
            if query.lower() in tag.lower()
        ][:3]

        # Recent searches (future)
        # Popular searches (future)

        return suggestions
```

## Frontend Implementation

### 1. Tag Components

#### TagBadge (`apps/web/src/components/tags/TagBadge.tsx`)
```typescript
interface TagBadgeProps {
  tag: string
  size?: 'sm' | 'md' | 'lg'
  showCount?: boolean
  count?: number
  onClick?: () => void
  onRemove?: () => void
}

// Display:
// - Tag name
// - Optional count
// - Click to filter
// - Remove button
```

#### TagCloud (`apps/web/src/components/tags/TagCloud.tsx`)
```typescript
interface TagCloudProps {
  tags: TagWithStats[]
  maxTags?: number
  onTagClick: (tag: string) => void
  variant?: 'sized' | 'uniform'
}

// Display:
// - Tags with relative sizing
// - Hover for stats
// - Click to explore
```

#### TagExplorer (`apps/web/src/components/tags/TagExplorer.tsx`)
```typescript
interface TagExplorerProps {
  tag: string
}

// Display:
// - Tag description
// - Usage stats
// - Top content
// - Top experts
// - Related tags
// - Trend chart
```

#### TagFilter (`apps/web/src/components/tags/TagFilter.tsx`)
```typescript
interface TagFilterProps {
  selected: string[]
  onChange: (tags: string[]) => void
  showCounts?: boolean
  multiSelect?: boolean
}

// Display:
// - All AI_TAGS
// - Selection state
// - Usage counts
// - Clear button
// - Search within tags
```

### 2. Search Components

#### SearchBar (`apps/web/src/components/search/SearchBar.tsx`)
```typescript
interface SearchBarProps {
  placeholder?: string
  onSearch: (query: string) => void
  showSuggestions?: boolean
  className?: string
}

// Features:
// - Input with icon
// - Autocomplete dropdown
// - Recent searches
// - Keyboard navigation
// - Mobile optimized
```

#### SearchResults (`apps/web/src/components/search/SearchResults.tsx`)
```typescript
interface SearchResultsProps {
  results: SearchResult[]
  query: string
  loading: boolean
  onLoadMore: () => void
}

// Display:
// - Grouped by type
// - Highlighted matches
// - Result counts
// - Load more
// - Empty state
```

#### SearchFilters (`apps/web/src/components/search/SearchFilters.tsx`)
```typescript
interface SearchFiltersProps {
  filters: SearchFilters
  onChange: (filters: SearchFilters) => void
  facets: SearchFacets
}

// Filters:
// - Content type
// - Tags
// - Date range
// - Sort order
```

#### GlobalSearch (`apps/web/src/components/search/GlobalSearch.tsx`)
```typescript
interface GlobalSearchProps {
  isOpen: boolean
  onClose: () => void
}

// Modal search with:
// - Full-screen overlay
// - Instant results
// - Keyboard shortcuts (Cmd+K)
// - Recent searches
// - Popular searches
```

### 3. Search Pages

#### Search Page (`apps/web/src/app/search/page.tsx`)
**Route**: `/search`
**Features**:
- Search input with autocomplete
- Filters sidebar
- Results with pagination
- Search history
- Save searches
- Analytics tracking

#### Tag Page (`apps/web/src/app/tags/[tag]/page.tsx`)
**Route**: `/tags/{tag}`
**Features**:
- Tag overview
- Top articles
- Active spaces
- Expert users
- Related tags
- Follow tag (future)

#### Tags Directory (`apps/web/src/app/tags/page.tsx`)
**Route**: `/tags`
**Features**:
- All AI tags grid
- Usage statistics
- Trending tags
- Tag relationships
- Search within tags

### 4. State Management

#### Search Hooks (`apps/web/src/hooks/useSearch.ts`)
```typescript
// Universal search
export function useSearch(query: string, filters?: SearchFilters) {
  return useSWR<SearchResponse>(
    query ? `/api/search?q=${encodeURIComponent(query)}${buildFilterQuery(filters)}` : null,
    fetcher,
    { keepPreviousData: true }
  )
}

// Autocomplete
export function useAutocomplete(query: string) {
  return useSWR<AutocompleteResponse>(
    query?.length >= 2 ? `/api/search/autocomplete?q=${encodeURIComponent(query)}` : null,
    fetcher,
    {
      dedupingInterval: 300,
      keepPreviousData: true
    }
  )
}

// Tag data
export function useTag(tag: string) {
  return useSWR<TagDetails>(
    tag ? `/api/tags/${encodeURIComponent(tag)}` : null,
    fetcher
  )
}

// All tags
export function useTags(sort: string = 'popular') {
  return useSWR<TagsResponse>(
    `/api/tags?sort=${sort}`,
    fetcher
  )
}
```

### 5. Types (`apps/web/src/types/search.ts`)
```typescript
interface SearchResult {
  type: 'article' | 'space' | 'user'
  score: number
  item: any
  highlights?: {
    title?: string
    content?: string
  }
}

interface SearchFilters {
  type?: string
  tags?: string[]
  dateRange?: string
  sort?: 'relevance' | 'latest' | 'popular'
}

interface SearchFacets {
  types: Record<string, number>
  tags: Record<string, number>
}

interface TagWithStats {
  name: string
  description?: string
  stats: {
    articles: number
    spaces: number
    experts: number
    trendingScore: number
  }
  related?: string[]
}
```

## Search Implementation Details

### PostgreSQL Full-Text Search Setup
```sql
-- Add text search configuration
CREATE TEXT SEARCH CONFIGURATION english_stem (COPY = english);

-- Add search indexes
CREATE INDEX idx_articles_search ON articles USING GIN(
  to_tsvector('english', title || ' ' || summary || ' ' || array_to_string(tags, ' '))
);

CREATE INDEX idx_spaces_search ON spaces USING GIN(
  to_tsvector('english', name || ' ' || COALESCE(description, '') || ' ' || array_to_string(tags, ' '))
);

CREATE INDEX idx_users_search ON users USING GIN(
  to_tsvector('english', username || ' ' || COALESCE(display_name, '') || ' ' || COALESCE(bio, ''))
);
```

### Search Ranking Algorithm
```python
def calculate_search_score(
    text_rank: float,      # PostgreSQL ts_rank
    entity_type: str,      # article, space, user
    popularity: float,     # views, members, etc.
    recency: float,       # age factor
    tag_match: bool       # exact tag match
) -> float:
    """
    Combined scoring for search results
    """
    # Base score from text relevance
    score = text_rank * 100

    # Type boost
    type_weights = {
        'article': 1.0,
        'space': 0.9,
        'user': 0.8
    }
    score *= type_weights.get(entity_type, 1.0)

    # Popularity boost (logarithmic)
    score += math.log(popularity + 1) * 10

    # Recency boost (decay over time)
    days_old = recency / 86400
    score *= (1 / (1 + days_old / 30))

    # Tag match bonus
    if tag_match:
        score *= 1.5

    return score
```

## Testing Requirements

### Backend Tests
```python
# test_tags.py
async def test_tag_usage_tracking()
async def test_trending_calculation()
async def test_tag_suggestions()
async def test_related_tags()

# test_search.py
async def test_full_text_search()
async def test_search_filtering()
async def test_search_ranking()
async def test_autocomplete()
async def test_search_pagination()
```

### Frontend Tests
```typescript
// SearchBar.test.tsx
test('shows autocomplete suggestions')
test('handles keyboard navigation')
test('debounces input')

// Search page tests
test('displays search results')
test('applies filters')
test('handles empty results')
test('loads more results')
```

### E2E Tests
```typescript
test('Complete search flow', async () => {
  // 1. Open global search (Cmd+K)
  // 2. Type query
  // 3. See autocomplete
  // 4. Submit search
  // 5. Filter by tag
  // 6. Click result
})
```

## Performance Considerations

### Backend
- Pre-calculate trending scores (hourly job)
- Cache tag stats (5 min)
- Index all searchable fields
- Use PostgreSQL native FTS
- Limit autocomplete queries

### Frontend
- Debounce search input (300ms)
- Virtual scroll for long results
- Lazy load result details
- Cache recent searches locally
- Prefetch popular tags

## Security Considerations
- Sanitize search queries
- Prevent SQL injection in FTS
- Rate limit search requests
- Validate tag names
- Limit result sizes

## Acceptance Criteria
- [ ] All AI_TAGS defined and documented
- [ ] Tag usage tracking works
- [ ] Search returns relevant results
- [ ] Autocomplete responds quickly
- [ ] Tag filtering works across platform
- [ ] Search highlights match terms
- [ ] Tag statistics accurate
- [ ] Mobile search works well
- [ ] Keyboard shortcuts work
- [ ] Tests pass

## Implementation Order
1. Backend: Define AI_TAGS constant
2. Backend: Create tag usage model
3. Backend: Implement tag service
4. Backend: Setup PostgreSQL FTS
5. Backend: Create search API
6. Frontend: Create tag components
7. Frontend: Implement search bar
8. Frontend: Create search page
9. Frontend: Add global search
10. Testing: Write tests
11. Optimization: Add caching

## Notes for AI Agents
- Use PostgreSQL native FTS, not external service
- Keep AI_TAGS immutable
- Pre-calculate trending for performance
- Test search with various queries
- Handle special characters in search
- Implement proper pagination
- Add search analytics
- Consider i18n for future