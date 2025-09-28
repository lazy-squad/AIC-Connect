# Task 03: Collaboration Spaces - Complete Implementation

## Objective
Create collaborative spaces where users can share articles, discussions, and work together on AI topics.

## Scope
- Backend: Space CRUD, membership management, article sharing
- Frontend: Space pages, member lists, article feeds
- Permissions: Owner/member roles, public/private visibility

## Dependencies
- **Required**: Task 01 (Users for membership)
- **Soft Dependency**: Task 02 (Articles to share, but can create spaces without)
- **Enables**: Task 05 (Spaces appear in feeds)

## Backend Implementation

### 1. Database Schema

#### Space Model (`apps/api/src/aic_hub/models/space.py`)
```python
class Space(Base):
    __tablename__ = "spaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(120), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=[], nullable=False)
    visibility = Column(String(20), default="public", nullable=False)  # public, private

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    member_count = Column(Integer, default=1, nullable=False)
    article_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("User", secondary="space_members", back_populates="spaces")
    articles = relationship("SpaceArticle", back_populates="space")

    # Indexes
    __table_args__ = (
        Index('idx_spaces_visibility_created', 'visibility', 'created_at'),
        Index('idx_spaces_tags', 'tags', postgresql_using='gin'),
        CheckConstraint("visibility IN ('public', 'private')", name="check_visibility"),
    )
```

#### SpaceMembers Association Table
```python
space_members = Table(
    'space_members',
    Base.metadata,
    Column('space_id', UUID(as_uuid=True), ForeignKey('spaces.id'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role', String(20), default='member', nullable=False),  # owner, moderator, member
    Column('joined_at', DateTime(timezone=True), server_default=func.now()),
    Index('idx_space_members_user', 'user_id'),
    CheckConstraint("role IN ('owner', 'moderator', 'member')", name="check_role"),
)
```

#### SpaceArticle Association Model
```python
class SpaceArticle(Base):
    __tablename__ = "space_articles"

    space_id = Column(UUID(as_uuid=True), ForeignKey('spaces.id'), primary_key=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey('articles.id'), primary_key=True)
    added_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    pinned = Column(Boolean, default=False, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    space = relationship("Space", back_populates="articles")
    article = relationship("Article")
    user = relationship("User", foreign_keys=[added_by])

    # Indexes
    __table_args__ = (
        Index('idx_space_articles_added', 'space_id', 'added_at'),
    )
```

### 2. API Endpoints

#### POST /api/spaces
**Purpose**: Create new space
**Auth**: Required
**Request**:
```json
{
  "name": "RAG Enthusiasts",
  "description": "A space for discussing RAG implementations and best practices",
  "tags": ["RAG", "Vector DBs", "Embeddings"],
  "visibility": "public"
}
```
**Validation**:
- name: Required, 1-100 chars
- description: Optional, max 500 chars
- tags: Max 5, from AI_TAGS
- visibility: "public" or "private"
**Response**: Created space with owner as first member

#### GET /api/spaces
**Purpose**: List spaces
**Auth**: Optional
**Query Parameters**:
- `tags[]`: Filter by tags
- `q`: Search name/description
- `my_spaces`: Boolean, user's spaces only (auth required)
- `skip`: Offset
- `limit`: Page size
**Response**:
```json
{
  "spaces": [
    {
      "id": "uuid",
      "name": "RAG Enthusiasts",
      "slug": "rag-enthusiasts",
      "description": "A space for...",
      "tags": ["RAG", "Vector DBs"],
      "visibility": "public",
      "memberCount": 42,
      "articleCount": 15,
      "createdAt": "2024-01-01T00:00:00Z",
      "owner": {
        "id": "uuid",
        "username": "johndoe",
        "displayName": "John Doe",
        "avatarUrl": "https://..."
      },
      "isMember": true,
      "memberRole": "member"
    }
  ],
  "total": 10,
  "skip": 0,
  "limit": 20
}
```

#### GET /api/spaces/{slug}
**Purpose**: Get space details
**Auth**: Optional (required for private spaces)
**Response**: Full space object with membership status

#### PATCH /api/spaces/{id}
**Purpose**: Update space
**Auth**: Required (must be owner)
**Request**: Partial update of space fields
**Response**: Updated space

#### DELETE /api/spaces/{id}
**Purpose**: Delete space
**Auth**: Required (must be owner)
**Response**: 204 No Content

#### POST /api/spaces/{id}/join
**Purpose**: Join a space
**Auth**: Required
**Response**:
```json
{
  "success": true,
  "role": "member",
  "joinedAt": "2024-01-01T00:00:00Z"
}
```

#### POST /api/spaces/{id}/leave
**Purpose**: Leave a space
**Auth**: Required
**Validation**: Owner cannot leave
**Response**: 204 No Content

#### GET /api/spaces/{id}/members
**Purpose**: Get space members
**Auth**: Optional (required for private spaces)
**Query Parameters**:
- `role`: Filter by role
- `skip`: Offset
- `limit`: Page size
**Response**:
```json
{
  "members": [
    {
      "user": {
        "id": "uuid",
        "username": "johndoe",
        "displayName": "John Doe",
        "avatarUrl": "https://...",
        "expertiseTags": ["RAG", "LLMs"]
      },
      "role": "owner",
      "joinedAt": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

#### PATCH /api/spaces/{id}/members/{userId}
**Purpose**: Update member role
**Auth**: Required (must be owner/moderator)
**Request**:
```json
{
  "role": "moderator"
}
```
**Response**: Updated member object

#### POST /api/spaces/{id}/articles
**Purpose**: Share article to space
**Auth**: Required (must be member)
**Request**:
```json
{
  "articleId": "uuid"
}
```
**Validation**:
- Must be space member
- Article must be published
- Article not already in space
**Response**: SpaceArticle object

#### GET /api/spaces/{id}/articles
**Purpose**: Get articles in space
**Auth**: Optional (required for private spaces)
**Query Parameters**:
- `pinned_first`: Boolean
- `skip`: Offset
- `limit`: Page size
**Response**:
```json
{
  "articles": [
    {
      "article": {
        "id": "uuid",
        "title": "Understanding RAG",
        "slug": "understanding-rag",
        "summary": "...",
        "tags": ["RAG"],
        "author": { /* UserSummary */ }
      },
      "addedBy": { /* UserSummary */ },
      "pinned": false,
      "addedAt": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 20
}
```

#### PATCH /api/spaces/{id}/articles/{articleId}
**Purpose**: Pin/unpin article
**Auth**: Required (must be owner/moderator)
**Request**:
```json
{
  "pinned": true
}
```
**Response**: Updated SpaceArticle

#### DELETE /api/spaces/{id}/articles/{articleId}
**Purpose**: Remove article from space
**Auth**: Required (must be owner/moderator or article adder)
**Response**: 204 No Content

### 3. Service Layer (`apps/api/src/aic_hub/services/space_service.py`)

```python
class SpaceService:
    @staticmethod
    async def create_space(
        db: AsyncSession,
        owner_id: UUID,
        data: SpaceCreate
    ) -> Space:
        """Create space with owner as first member"""

    @staticmethod
    async def can_access_space(
        space: Space,
        user_id: UUID | None,
        db: AsyncSession
    ) -> bool:
        """Check if user can access space (public or member)"""

    @staticmethod
    async def get_member_role(
        db: AsyncSession,
        space_id: UUID,
        user_id: UUID
    ) -> str | None:
        """Get user's role in space"""

    @staticmethod
    async def join_space(
        db: AsyncSession,
        space_id: UUID,
        user_id: UUID
    ) -> SpaceMember:
        """Add user to space"""

    @staticmethod
    async def leave_space(
        db: AsyncSession,
        space_id: UUID,
        user_id: UUID
    ) -> bool:
        """Remove user from space (not owner)"""

    @staticmethod
    async def share_article(
        db: AsyncSession,
        space_id: UUID,
        article_id: UUID,
        user_id: UUID
    ) -> SpaceArticle:
        """Share article to space"""
```

## Frontend Implementation

### 1. Space Components

#### SpaceCard (`apps/web/src/components/spaces/SpaceCard.tsx`)
```typescript
interface SpaceCardProps {
  space: SpaceSummary
  showJoinButton?: boolean
  onJoin?: (spaceId: string) => void
}

// Display:
// - Name with link
// - Description (truncated)
// - Owner info
// - Member/article counts
// - Tags
// - Join/leave button
// - Private indicator
```

#### SpaceHeader (`apps/web/src/components/spaces/SpaceHeader.tsx`)
```typescript
interface SpaceHeaderProps {
  space: Space
  isMember: boolean
  memberRole?: string
  onJoin: () => void
  onLeave: () => void
  onEdit: () => void
}

// Display:
// - Space name and description
// - Owner info
// - Stats (members, articles)
// - Action buttons based on role
// - Tags
// - Visibility badge
```

#### SpaceMemberList (`apps/web/src/components/spaces/SpaceMemberList.tsx`)
```typescript
interface SpaceMemberListProps {
  spaceId: string
  canManage: boolean
  onRoleChange?: (userId: string, role: string) => void
}

// Display:
// - Member cards with roles
// - Role badges
// - Join date
// - Manage roles (if authorized)
// - Pagination
```

#### SpaceArticleList (`apps/web/src/components/spaces/SpaceArticleList.tsx`)
```typescript
interface SpaceArticleListProps {
  spaceId: string
  canManage: boolean
  onPin?: (articleId: string) => void
  onRemove?: (articleId: string) => void
}

// Display:
// - Articles with metadata
// - Pinned articles first
// - Added by info
// - Pin/remove actions
// - Share article button
```

#### ShareArticleModal (`apps/web/src/components/spaces/ShareArticleModal.tsx`)
```typescript
interface ShareArticleModalProps {
  article: Article
  userSpaces: Space[]
  onShare: (spaceId: string) => void
  onClose: () => void
}

// Display:
// - List of user's spaces
// - Already shared indicators
// - Share buttons
// - Success feedback
```

### 2. Space Pages

#### Spaces Directory (`apps/web/src/app/spaces/page.tsx`)
**Route**: `/spaces`
**Features**:
- Browse all public spaces
- Filter by tags
- Search by name/description
- "My Spaces" tab (if authenticated)
- Create space button
- Grid/list view toggle

#### Create Space (`apps/web/src/app/spaces/new/page.tsx`)
**Route**: `/spaces/new`
**Features**:
- Protected route
- Space creation form
- Name, description, tags
- Visibility selector
- Validation
- Success redirect to space

#### Space Detail (`apps/web/src/app/spaces/[slug]/page.tsx`)
**Route**: `/spaces/{slug}`
**Features**:
- Space header with info
- Tabs: Articles, Members, About
- Join/leave functionality
- Edit button (if owner)
- Share article button (if member)
- Private space access control

#### Edit Space (`apps/web/src/app/spaces/[slug]/edit/page.tsx`)
**Route**: `/spaces/{slug}/edit`
**Features**:
- Protected route
- Must be owner
- Edit form
- Delete confirmation
- Member management
- Success/error handling

### 3. State Management

#### Space Hooks (`apps/web/src/hooks/useSpace.ts`)
```typescript
// Fetch single space
export function useSpace(slug: string) {
  return useSWR<Space>(
    slug ? `/api/spaces/${slug}` : null,
    fetcher
  )
}

// Fetch spaces list
export function useSpaces(params: SpaceQueryParams) {
  const query = new URLSearchParams(params)
  return useSWR<SpaceListResponse>(
    `/api/spaces?${query}`,
    fetcher
  )
}

// Space members
export function useSpaceMembers(spaceId: string, params?: MemberQueryParams) {
  const query = new URLSearchParams(params)
  return useSWR<MemberListResponse>(
    spaceId ? `/api/spaces/${spaceId}/members?${query}` : null,
    fetcher
  )
}

// Space articles
export function useSpaceArticles(spaceId: string, params?: ArticleQueryParams) {
  const query = new URLSearchParams(params)
  return useSWR<SpaceArticleListResponse>(
    spaceId ? `/api/spaces/${spaceId}/articles?${query}` : null,
    fetcher
  )
}

// Mutations
export function useJoinSpace() {
  return useSWRMutation(
    (spaceId: string) => `/api/spaces/${spaceId}/join`,
    joinSpace,
    {
      onSuccess: () => {
        // Invalidate space data
        mutate(key => typeof key === 'string' && key.startsWith('/api/spaces'))
      }
    }
  )
}
```

### 4. Types (`apps/web/src/types/space.ts`)
```typescript
interface Space {
  id: string
  name: string
  slug: string
  description?: string
  tags: string[]
  visibility: 'public' | 'private'
  ownerId: string
  memberCount: number
  articleCount: number
  createdAt: string
  updatedAt?: string
  owner: UserSummary
  isMember?: boolean
  memberRole?: 'owner' | 'moderator' | 'member'
}

interface SpaceMember {
  user: UserSummary
  role: 'owner' | 'moderator' | 'member'
  joinedAt: string
}

interface SpaceArticle {
  article: ArticleSummary
  addedBy: UserSummary
  pinned: boolean
  addedAt: string
}

interface SpaceFormData {
  name: string
  description?: string
  tags: string[]
  visibility: 'public' | 'private'
}
```

## Integration Points

### Navigation Updates
- "Spaces" in main nav
- "My Spaces" in user menu
- Space count in user profile

### Article Integration
- "Share to Space" button on articles
- Article appears in space feeds
- Space name on shared articles

### User Profile Integration
- User's spaces on profile
- Space membership count

### Feed Integration (Task 05)
- Space activity in feeds
- New spaces highlighted

## Testing Requirements

### Backend Tests
```python
# test_spaces.py
async def test_create_space()
async def test_join_leave_space()
async def test_private_space_access()
async def test_share_article_to_space()
async def test_member_roles()
async def test_owner_cannot_leave()
async def test_space_article_pinning()
async def test_space_deletion()
async def test_search_spaces()
```

### Frontend Tests
```typescript
// SpaceCard.test.tsx
test('displays space information')
test('shows join button when not member')
test('indicates private spaces')

// Space pages
test('creates new space')
test('joins public space')
test('cannot access private space when not member')
test('owner can edit space')
test('members can share articles')
```

### E2E Tests
```typescript
test('Complete space flow', async () => {
  // 1. Create space
  // 2. Join space
  // 3. Share article
  // 4. Pin article (as owner)
  // 5. Manage members
  // 6. Leave space
})
```

## Error Handling

### Backend Errors
- 400: Invalid space data
- 401: Authentication required
- 403: Not authorized (private space, not owner)
- 404: Space not found
- 409: Already member / article already shared

### Frontend Error States
- Private space: Access denied message
- Network errors: Retry UI
- Form validation: Inline errors
- Not found: 404 page

## Performance Considerations
- Index space slugs
- GIN index for tag searches
- Denormalize member/article counts
- Paginate member/article lists
- Cache space data (5 min)

## Security Considerations
- Private space access control
- Owner/moderator permissions
- Rate limit space creation
- Validate membership before actions
- Sanitize description content

## Acceptance Criteria
- [ ] Space model and associations created
- [ ] CRUD API endpoints working
- [ ] Membership management works
- [ ] Article sharing works
- [ ] Private spaces restricted
- [ ] Role-based permissions work
- [ ] Frontend pages render correctly
- [ ] Join/leave functionality works
- [ ] Search and filters work
- [ ] Tests pass
- [ ] No permission bypasses

## Implementation Order
1. Backend: Create models and migration
2. Backend: Implement space CRUD
3. Backend: Add membership management
4. Backend: Add article sharing
5. Frontend: Create space components
6. Frontend: Implement pages
7. Frontend: Add state management
8. Testing: Write and run tests
9. Integration: Full flow testing

## Notes for AI Agents
- Ensure owner is first member
- Handle slug conflicts
- Validate tags against AI_TAGS
- Check membership before all actions
- Use transactions for consistency
- Test private space access
- Implement proper pagination
- Cache member counts