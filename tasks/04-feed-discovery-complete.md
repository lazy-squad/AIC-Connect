# Task 04: Feed & Discovery - Complete Implementation

## Objective
Create a personalized feed system with discovery features, including trending content, tag-based filtering, and activity streams.

## Scope
- Backend: Feed aggregation APIs, trending algorithms
- Frontend: Feed page, filters, discovery tabs
- Personalization: Tag preferences, following (future)

## Dependencies
- **Required**: Task 01 (Users), Task 02 (Articles)
- **Optional**: Task 03 (Spaces for space activity)
- **Enhances with**: Task 05 (Tag system)

## Backend Implementation

### 1. Database Schema Changes

#### UserPreferences Model (`apps/api/src/aic_hub/models/user_preferences.py`)
```python
class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    preferred_tags = Column(ARRAY(String), default=[], nullable=False)
    feed_view = Column(String(20), default="latest", nullable=False)  # latest, trending, following
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="preferences")
```

#### Activity Model (`apps/api/src/aic_hub/models/activity.py`)
```python
class Activity(Base):
    __tablename__ = "activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # article_published, space_created, user_joined_space
    target_type = Column(String(50), nullable=False)  # article, space, user
    target_id = Column(UUID(as_uuid=True), nullable=False)
    metadata = Column(JSON, default={}, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    actor = relationship("User")

    # Indexes
    __table_args__ = (
        Index('idx_activities_actor_created', 'actor_id', 'created_at'),
        Index('idx_activities_target', 'target_type', 'target_id'),
    )
```

### 2. API Endpoints

#### GET /api/feed
**Purpose**: Get personalized feed
**Auth**: Optional (authenticated gets personalized)
**Query Parameters**:
- `view`: `latest`, `trending`, `following`, `recommended`
- `tags[]`: Filter by tags
- `time_range`: For trending (`24h`, `7d`, `30d`, `all`)
- `skip`: Offset
- `limit`: Page size
**Response**:
```json
{
  "items": [
    {
      "type": "article",
      "article": {
        "id": "uuid",
        "title": "Understanding RAG",
        "slug": "understanding-rag",
        "summary": "...",
        "tags": ["RAG"],
        "viewCount": 150,
        "publishedAt": "2024-01-01T00:00:00Z",
        "author": { /* UserSummary */ }
      },
      "reason": "trending_in_your_tags"  // trending, new_from_followed, recommended
    },
    {
      "type": "space_activity",
      "space": { /* SpaceSummary */ },
      "activity": "new_articles",
      "count": 3,
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 20,
  "nextCursor": "eyJvZmZzZXQiOjIwfQ=="
}
```

#### GET /api/feed/trending
**Purpose**: Get trending content
**Auth**: Optional
**Query Parameters**:
- `type`: `articles`, `spaces`, `tags`, `all`
- `time_range`: `24h`, `7d`, `30d`
- `limit`: Result count
**Response**:
```json
{
  "articles": [
    {
      "article": { /* ArticleSummary */ },
      "score": 450,  // Trending score
      "viewsInPeriod": 300,
      "trend": "rising"  // rising, steady, falling
    }
  ],
  "spaces": [
    {
      "space": { /* SpaceSummary */ },
      "newMembers": 15,
      "newArticles": 8,
      "activityScore": 230
    }
  ],
  "tags": [
    {
      "tag": "RAG",
      "count": 42,
      "change": "+15%",
      "articles": 25
    }
  ]
}
```

#### GET /api/feed/discover
**Purpose**: Content discovery
**Auth**: Optional
**Query Parameters**:
- `category`: `new_users`, `rising_articles`, `active_spaces`
- `exclude_seen`: Boolean
- `limit`: Result count
**Response**:
```json
{
  "category": "rising_articles",
  "items": [
    {
      "article": { /* ArticleSummary */ },
      "metrics": {
        "viewVelocity": 45,  // Views per hour
        "shareCount": 12,
        "firstSeen": "2024-01-01T00:00:00Z"
      }
    }
  ],
  "refreshAt": "2024-01-01T01:00:00Z"
}
```

#### GET /api/feed/activity
**Purpose**: Get activity stream
**Auth**: Required
**Query Parameters**:
- `scope`: `following`, `spaces`, `all`
- `types[]`: Activity types to include
- `since`: Timestamp for updates
- `limit`: Result count
**Response**:
```json
{
  "activities": [
    {
      "id": "uuid",
      "actor": { /* UserSummary */ },
      "action": "published_article",
      "target": {
        "type": "article",
        "id": "uuid",
        "title": "New Article",
        "slug": "new-article"
      },
      "timestamp": "2024-01-01T00:00:00Z"
    },
    {
      "id": "uuid",
      "actor": { /* UserSummary */ },
      "action": "joined_space",
      "target": {
        "type": "space",
        "id": "uuid",
        "name": "AI Research",
        "slug": "ai-research"
      },
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "hasMore": true,
  "oldestTimestamp": "2024-01-01T00:00:00Z"
}
```

#### PATCH /api/users/me/preferences
**Purpose**: Update feed preferences
**Auth**: Required
**Request**:
```json
{
  "preferredTags": ["RAG", "LLMs", "Agents"],
  "feedView": "trending"
}
```
**Response**: Updated preferences

#### POST /api/feed/interactions
**Purpose**: Track user interactions for recommendations
**Auth**: Required
**Request**:
```json
{
  "type": "view",  // view, click, share, save
  "targetType": "article",
  "targetId": "uuid",
  "duration": 45,  // Seconds for view
  "metadata": {
    "source": "feed",
    "position": 3
  }
}
```
**Response**: 204 No Content

### 3. Service Layer

#### FeedService (`apps/api/src/aic_hub/services/feed_service.py`)
```python
class FeedService:
    @staticmethod
    async def get_personalized_feed(
        db: AsyncSession,
        user_id: UUID | None,
        view: str,
        tags: List[str] | None,
        skip: int,
        limit: int
    ) -> FeedResponse:
        """Generate personalized feed based on preferences"""

    @staticmethod
    async def calculate_trending(
        db: AsyncSession,
        time_range: str,
        content_type: str
    ) -> List[TrendingItem]:
        """Calculate trending content using view velocity and engagement"""

    @staticmethod
    async def get_recommendations(
        db: AsyncSession,
        user_id: UUID,
        limit: int
    ) -> List[Article]:
        """Get recommended articles based on user activity"""

    @staticmethod
    def calculate_trending_score(
        views: int,
        age_hours: float,
        interactions: int
    ) -> float:
        """Calculate trending score using time decay"""
        # Score = (views + interactions * 2) / (age_hours + 2) ^ 1.5
```

#### ActivityService (`apps/api/src/aic_hub/services/activity_service.py`)
```python
class ActivityService:
    @staticmethod
    async def record_activity(
        db: AsyncSession,
        actor_id: UUID,
        action: str,
        target_type: str,
        target_id: UUID,
        metadata: dict = None
    ) -> Activity:
        """Record user activity for feeds"""

    @staticmethod
    async def get_activity_stream(
        db: AsyncSession,
        user_id: UUID,
        scope: str,
        types: List[str],
        since: datetime | None,
        limit: int
    ) -> List[Activity]:
        """Get activity stream for user"""
```

## Frontend Implementation

### 1. Feed Components

#### FeedItem (`apps/web/src/components/feed/FeedItem.tsx`)
```typescript
interface FeedItemProps {
  item: FeedItem
  onInteraction: (type: string, targetId: string) => void
}

// Polymorphic component rendering:
// - Article cards
// - Space activity
// - User joined
// - Trending indicator
```

#### FeedFilters (`apps/web/src/components/feed/FeedFilters.tsx`)
```typescript
interface FeedFiltersProps {
  selectedTags: string[]
  onTagsChange: (tags: string[]) => void
  timeRange: string
  onTimeRangeChange: (range: string) => void
  view: string
  onViewChange: (view: string) => void
}

// Filters:
// - Tag multi-select
// - Time range dropdown
// - View tabs (Latest, Trending, Following)
// - Clear filters button
```

#### TrendingSection (`apps/web/src/components/feed/TrendingSection.tsx`)
```typescript
interface TrendingSectionProps {
  type: 'articles' | 'spaces' | 'tags'
  timeRange: string
  limit?: number
}

// Display:
// - Trending items with scores
// - Trend indicators (↑↓)
// - Time range selector
// - See more link
```

#### ActivityStream (`apps/web/src/components/feed/ActivityStream.tsx`)
```typescript
interface ActivityStreamProps {
  scope: 'following' | 'spaces' | 'all'
  compact?: boolean
}

// Display:
// - Recent activities
// - Actor avatars
// - Action descriptions
// - Relative timestamps
// - Load more button
```

#### DiscoveryCard (`apps/web/src/components/feed/DiscoveryCard.tsx`)
```typescript
interface DiscoveryCardProps {
  category: string
  items: DiscoveryItem[]
  onDismiss: () => void
}

// Display:
// - Category header
// - Recommended items
// - Dismiss option
// - Refresh button
```

### 2. Feed Pages

#### Main Feed (`apps/web/src/app/feed/page.tsx`)
**Route**: `/feed`
**Features**:
- Tab views: For You, Latest, Trending, Following
- Tag filters (sticky)
- Infinite scroll
- Pull to refresh
- Empty states
- Loading states
- Error recovery

```typescript
// Main feed page structure
export default function FeedPage() {
  const { user } = useAuth()
  const [view, setView] = useState('latest')
  const [filters, setFilters] = useState<FeedFilters>({})

  const { data, error, isLoading, size, setSize } = useSWRInfinite(
    (index) => getFeedKey(index, view, filters),
    fetcher
  )

  // Tabs component
  // Filters sidebar
  // Feed items list
  // Infinite scroll trigger
}
```

#### Trending Page (`apps/web/src/app/trending/page.tsx`)
**Route**: `/trending`
**Features**:
- Trending articles, spaces, tags
- Time range selector
- Category tabs
- Charts/visualizations
- Share trending items

#### Discover Page (`apps/web/src/app/discover/page.tsx`)
**Route**: `/discover`
**Features**:
- New users to follow
- Rising content
- Recommended based on interests
- Topic exploration
- Onboarding for new users

### 3. State Management

#### Feed Context (`apps/web/src/contexts/feed-context.tsx`)
```typescript
interface FeedContext {
  preferences: UserPreferences
  updatePreferences: (prefs: Partial<UserPreferences>) => void
  trackInteraction: (interaction: Interaction) => void
  refreshFeed: () => void
}
```

#### Feed Hooks (`apps/web/src/hooks/useFeed.ts`)
```typescript
// Main feed with infinite scroll
export function useFeed(params: FeedParams) {
  return useSWRInfinite(
    (index) => `/api/feed?${buildQuery(params, index)}`,
    fetcher,
    {
      revalidateFirstPage: false,
      revalidateAll: false
    }
  )
}

// Trending content
export function useTrending(type: string, timeRange: string) {
  return useSWR<TrendingResponse>(
    `/api/feed/trending?type=${type}&time_range=${timeRange}`,
    fetcher,
    { refreshInterval: 60000 }  // Refresh every minute
  )
}

// Activity stream with polling
export function useActivityStream(scope: string) {
  return useSWR<ActivityResponse>(
    `/api/feed/activity?scope=${scope}`,
    fetcher,
    { refreshInterval: 30000 }  // Poll every 30 seconds
  )
}

// Discovery recommendations
export function useDiscovery(category: string) {
  return useSWR<DiscoveryResponse>(
    `/api/feed/discover?category=${category}`,
    fetcher
  )
}
```

### 4. Types (`apps/web/src/types/feed.ts`)
```typescript
interface FeedItem {
  type: 'article' | 'space_activity' | 'user_activity'
  data: Article | SpaceActivity | UserActivity
  reason?: string
  score?: number
}

interface TrendingItem {
  type: 'article' | 'space' | 'tag'
  data: any
  score: number
  trend: 'rising' | 'steady' | 'falling'
  metrics: {
    views?: number
    members?: number
    articles?: number
  }
}

interface Activity {
  id: string
  actor: UserSummary
  action: string
  target: {
    type: string
    id: string
    name?: string
    title?: string
  }
  timestamp: string
}

interface UserPreferences {
  preferredTags: string[]
  feedView: 'latest' | 'trending' | 'following'
}
```

## Integration Points

### Navigation
- Feed link in main nav
- Trending badge for hot content
- Discovery hint for new users

### Article Integration
- Articles appear in feed
- View tracking for trending
- Share to feed functionality

### Space Integration
- Space activity in feed
- New space announcements
- Popular spaces highlighted

### User Integration
- Following system (future)
- User preferences sync
- Personalized recommendations

## Algorithms

### Trending Score Calculation
```python
def calculate_trending_score(views, age_hours, interactions):
    """
    Time-decay algorithm for trending content
    Higher score = more trending
    """
    base_score = views + (interactions * 2)
    time_penalty = (age_hours + 2) ** 1.5
    return base_score / time_penalty
```

### Feed Ranking
```python
def rank_feed_items(items, user_preferences):
    """
    Rank feed items based on:
    1. Relevance to user tags
    2. Recency
    3. Engagement metrics
    4. Author reputation
    """
    for item in items:
        relevance_score = calculate_relevance(item, user_preferences)
        recency_score = calculate_recency(item)
        engagement_score = calculate_engagement(item)

        item.score = (
            relevance_score * 0.4 +
            recency_score * 0.3 +
            engagement_score * 0.3
        )

    return sorted(items, key=lambda x: x.score, reverse=True)
```

## Testing Requirements

### Backend Tests
```python
# test_feed.py
async def test_personalized_feed()
async def test_trending_calculation()
async def test_activity_stream()
async def test_discovery_recommendations()
async def test_feed_pagination()
async def test_interaction_tracking()
async def test_preference_updates()
```

### Frontend Tests
```typescript
// FeedItem.test.tsx
test('renders different item types')
test('tracks interactions')

// Feed page tests
test('loads feed with infinite scroll')
test('applies filters')
test('switches between views')
test('handles empty states')
```

### E2E Tests
```typescript
test('Feed interaction flow', async () => {
  // 1. Load feed
  // 2. Apply filters
  // 3. Switch to trending
  // 4. Click article
  // 5. Check view tracked
  // 6. Load more items
})
```

## Performance Considerations

### Backend
- Cache trending calculations (5 min)
- Denormalize view counts
- Batch activity inserts
- Use cursor pagination for feeds
- Background job for trending calc

### Frontend
- Virtual scrolling for long feeds
- Debounce filter changes
- Prefetch next page
- Optimistic UI updates
- Image lazy loading

## Acceptance Criteria
- [ ] Feed API returns paginated results
- [ ] Trending algorithm works correctly
- [ ] Activity tracking implemented
- [ ] Feed preferences persist
- [ ] Multiple view modes work
- [ ] Tag filtering works
- [ ] Infinite scroll works
- [ ] Discovery suggests relevant content
- [ ] Performance targets met
- [ ] Tests pass

## Implementation Order
1. Backend: Create activity model
2. Backend: Implement feed API
3. Backend: Add trending calculation
4. Backend: Add discovery endpoint
5. Frontend: Create feed components
6. Frontend: Implement main feed page
7. Frontend: Add infinite scroll
8. Frontend: Add filtering
9. Testing: Write tests
10. Optimization: Add caching

## Notes for AI Agents
- Use cursor pagination, not offset
- Cache trending scores aggressively
- Track interactions asynchronously
- Implement virtual scrolling for performance
- Handle empty states gracefully
- Test with various data volumes
- Consider mobile experience
- Add analytics tracking