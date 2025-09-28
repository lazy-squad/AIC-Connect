# Task 01: User Profiles - Complete Implementation

## Objective
Extend the existing user system to support rich profiles with GitHub data, expertise tags, and profile management capabilities for the AI Collective Hub.

## Scope
- Backend: Extend User model, create profile API endpoints
- Frontend: Profile pages, edit forms, user cards
- Integration: GitHub OAuth data population

## Dependencies
- **Required**: Existing auth system (complete)
- **Enables**: All other tasks need user profiles

## Backend Implementation

### 1. Database Schema Changes

#### Update User Model (`apps/api/src/aic_hub/models/user.py`)
```python
# Add these columns to existing User model
username = Column(String(50), unique=True, nullable=True, index=True)
github_username = Column(String(50), unique=True, nullable=True)
avatar_url = Column(String(500), nullable=True)
bio = Column(Text, nullable=True)
company = Column(String(100), nullable=True)
location = Column(String(100), nullable=True)
expertise_tags = Column(ARRAY(String), default=[], nullable=False)
updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Add indexes
__table_args__ = (
    Index('idx_user_expertise_tags', 'expertise_tags', postgresql_using='gin'),
)
```

#### Migration (`alembic revision --autogenerate -m "Add profile fields"`)
- Add new columns with proper defaults
- Create GIN index for array search
- Ensure backward compatibility

### 2. API Endpoints

#### GET /api/users/me
**Purpose**: Get current user's complete profile
**Auth**: Required
**Response**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "displayName": "John Doe",
  "username": "johndoe",
  "avatarUrl": "https://github.com/...",
  "bio": "AI researcher focused on RAG",
  "company": "AI Collective",
  "location": "San Francisco, CA",
  "expertiseTags": ["RAG", "LLMs", "Vector DBs"],
  "githubUsername": "johndoe",
  "createdAt": "2024-01-01T00:00:00Z",
  "articleCount": 5,
  "spaceCount": 3
}
```

#### PATCH /api/users/me
**Purpose**: Update current user's profile
**Auth**: Required
**Request**:
```json
{
  "displayName": "John Doe",
  "bio": "Updated bio",
  "company": "New Company",
  "location": "New York, NY",
  "expertiseTags": ["RAG", "Agents"]
}
```
**Validation**:
- displayName: 1-100 chars
- bio: 0-500 chars
- expertiseTags: max 10, must be from AI_TAGS list
- username: Cannot be changed after set
**Response**: Updated user object

#### GET /api/users/{username}
**Purpose**: Get public user profile
**Auth**: Optional (affects email visibility)
**Response**:
```json
{
  "id": "uuid",
  "username": "johndoe",
  "displayName": "John Doe",
  "avatarUrl": "https://...",
  "bio": "AI researcher",
  "company": "AI Collective",
  "location": "San Francisco",
  "expertiseTags": ["RAG", "LLMs"],
  "createdAt": "2024-01-01T00:00:00Z",
  "articleCount": 5,
  "spaceCount": 3
}
```
Note: Email excluded from public profile

#### GET /api/users
**Purpose**: Search and list users
**Auth**: Optional
**Query Parameters**:
- `q`: Search query (searches username, displayName, bio)
- `expertise`: Filter by expertise tags (array)
- `skip`: Pagination offset (default: 0)
- `limit`: Page size (default: 20, max: 100)
**Response**:
```json
{
  "users": [...],
  "total": 150,
  "skip": 0,
  "limit": 20
}
```

#### POST /api/users/check-username
**Purpose**: Check username availability
**Auth**: Required
**Request**:
```json
{
  "username": "desired-username"
}
```
**Response**:
```json
{
  "available": true,
  "suggestion": null
}
```

### 3. Service Layer (`apps/api/src/aic_hub/services/user_service.py`)

```python
class UserService:
    @staticmethod
    async def get_user_stats(db: AsyncSession, user_id: UUID) -> dict:
        """Get article and space counts for user"""

    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user: User,
        updates: UserProfileUpdate
    ) -> User:
        """Update user profile with validation"""

    @staticmethod
    async def populate_github_data(
        user: User,
        github_profile: GitHubProfile
    ) -> None:
        """Populate user fields from GitHub OAuth"""

    @staticmethod
    async def search_users(
        db: AsyncSession,
        query: str = None,
        expertise: List[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[User], int]:
        """Search users with filters"""
```

### 4. Update GitHub OAuth Integration

Modify `github_callback` in `apps/api/src/aic_hub/routes/auth.py`:
- Populate username from GitHub login
- Set avatar_url, bio, company, location
- Handle username conflicts (append number)

## Frontend Implementation

### 1. Components

#### UserAvatar (`apps/web/src/components/user/UserAvatar.tsx`)
```typescript
interface UserAvatarProps {
  user: {
    avatarUrl?: string
    displayName?: string
    username: string
  }
  size?: 'sm' | 'md' | 'lg'
  showName?: boolean
  linkToProfile?: boolean
}
```
- Renders avatar with fallback to initials
- Optional name display
- Click to profile navigation

#### UserCard (`apps/web/src/components/user/UserCard.tsx`)
```typescript
interface UserCardProps {
  user: UserPublicProfile
  showStats?: boolean
  showBio?: boolean
  variant?: 'compact' | 'full'
}
```
- Display user info in card format
- Show expertise tags
- Article/space counts
- Link to full profile

#### ProfileEditForm (`apps/web/src/components/user/ProfileEditForm.tsx`)
```typescript
interface ProfileEditFormProps {
  user: UserProfile
  onSave: (updates: UserProfileUpdate) => Promise<void>
  onCancel: () => void
}
```
- Form fields for all editable properties
- Username validation (if not set)
- Expertise tag selector (max 10)
- Character count for bio
- Optimistic UI updates

#### ExpertiseTagSelector (`apps/web/src/components/tags/ExpertiseTagSelector.tsx`)
```typescript
interface ExpertiseTagSelectorProps {
  selected: string[]
  onChange: (tags: string[]) => void
  max?: number
  variant?: 'chips' | 'checkboxes'
}
```
- Multi-select from AI_TAGS
- Visual feedback for selection limit
- Search/filter tags

### 2. Pages

#### User Profile Page (`apps/web/src/app/users/[username]/page.tsx`)
**Route**: `/users/{username}`
**Features**:
- Fetch and display user profile
- Show articles by user
- Show spaces user belongs to
- Edit button (if own profile)
- 404 handling for unknown users
- SEO meta tags

#### Profile Settings Page (`apps/web/src/app/settings/profile/page.tsx`)
**Route**: `/settings/profile`
**Features**:
- Protected route (auth required)
- Edit form for current user
- Username setting (one-time if not set)
- Save/cancel actions
- Success/error feedback
- Link to change password (if email user)

#### Users Directory Page (`apps/web/src/app/users/page.tsx`)
**Route**: `/users`
**Features**:
- Browse all users
- Search by name/bio
- Filter by expertise tags
- Pagination
- Grid/list view toggle

### 3. State Management

#### Update Auth Context
```typescript
interface AuthContext {
  user: UserProfile | null
  loading: boolean
  error: string | null
  updateProfile: (updates: UserProfileUpdate) => Promise<void>
  refreshProfile: () => Promise<void>
}
```

#### User Hooks (`apps/web/src/hooks/useUser.ts`)
```typescript
// Fetch any user's profile
export function useUser(username: string) {
  return useSWR<UserPublicProfile>(
    username ? `/api/users/${username}` : null,
    fetcher
  )
}

// Search users
export function useUsers(params: UserSearchParams) {
  const query = new URLSearchParams(params)
  return useSWR<UserSearchResponse>(
    `/api/users?${query}`,
    fetcher
  )
}

// Check username availability
export function useUsernameCheck(username: string) {
  return useSWR<UsernameCheckResponse>(
    username ? `/api/users/check-username` : null,
    (url) => fetcher(url, { method: 'POST', body: { username } }),
    { debounce: 500 }
  )
}
```

### 4. Types (`apps/web/src/types/user.ts`)
```typescript
interface UserProfile {
  id: string
  email: string
  displayName?: string
  username?: string
  avatarUrl?: string
  bio?: string
  company?: string
  location?: string
  expertiseTags: string[]
  githubUsername?: string
  createdAt: Date
  articleCount: number
  spaceCount: number
}

interface UserPublicProfile {
  // Same as UserProfile but without email
}

interface UserProfileUpdate {
  displayName?: string
  bio?: string
  company?: string
  location?: string
  expertiseTags?: string[]
}
```

## Integration Points

### GitHub OAuth Flow
1. User signs in with GitHub
2. Backend fetches GitHub profile
3. Populate user fields:
   - username from login
   - avatar_url from avatar
   - bio, company, location if available
4. Handle username conflicts
5. User can edit later in settings

### Navigation Updates
- Add user avatar to top nav
- Dropdown with profile link
- Settings link
- Sign out option

### Article/Space Integration
- Author displays with avatar
- Link to author profile
- Show author expertise tags

## Testing Requirements

### Backend Tests
```python
# test_user_profile.py
async def test_get_current_user_profile()
async def test_update_profile()
async def test_get_public_profile()
async def test_search_users()
async def test_username_availability()
async def test_github_data_population()
async def test_expertise_tags_validation()
```

### Frontend Tests
```typescript
// UserCard.test.tsx
test('renders user information')
test('shows expertise tags')
test('links to profile')

// ProfileEditForm.test.tsx
test('validates input fields')
test('limits expertise tags')
test('handles save errors')

// Profile page tests
test('displays user profile')
test('shows edit button for own profile')
test('handles unknown user')
```

### E2E Tests
```typescript
test('Complete profile flow', async () => {
  // 1. Sign up/login
  // 2. Navigate to settings
  // 3. Update profile
  // 4. View public profile
  // 5. Search for user
})
```

## Error Handling

### Backend Errors
- 400: Invalid expertise tags
- 400: Username already taken
- 400: Bio too long
- 404: User not found
- 401: Unauthorized to edit

### Frontend Error States
- Form validation errors
- Network error retry
- Username taken message
- Not found page
- Loading states

## Performance Considerations
- Cache user profiles (5 min)
- Index username for fast lookup
- GIN index for tag searches
- Lazy load user articles
- Avatar image optimization

## Security Considerations
- Email only visible to self
- Sanitize bio content
- Validate expertise tags
- Rate limit profile updates
- Prevent username hijacking

## Acceptance Criteria
- [ ] User model extended with new fields
- [ ] Migration runs successfully
- [ ] GitHub data populates on OAuth
- [ ] Profile API endpoints work
- [ ] Profile page displays correctly
- [ ] Edit form validates and saves
- [ ] Search/filter users works
- [ ] Navigation shows user avatar
- [ ] Tests pass
- [ ] No regressions in auth flow

## Implementation Order
1. Backend: Extend model and migration
2. Backend: Create API endpoints
3. Backend: Update GitHub OAuth
4. Frontend: Create components
5. Frontend: Create pages
6. Frontend: Update navigation
7. Testing: Write and run tests
8. Integration: Full flow testing

## Notes for AI Agents
- Check existing User model first
- Use existing auth dependencies
- Follow REST conventions
- Reuse existing UI components
- Test each endpoint with curl
- Handle edge cases (no avatar, no bio)
- Keep username immutable once set
- Don't expose sensitive data