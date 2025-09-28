# AI Collective Hub - Implementation Overview

## Project Architecture

### Backend (FastAPI)
- **Base URL**: `http://localhost:4000` (development)
- **Database**: PostgreSQL 16
- **Auth**: JWT in HttpOnly cookies
- **ORM**: SQLAlchemy 2.0 with async support
- **Migration**: Alembic

### Frontend (Next.js 14)
- **Base URL**: `http://localhost:3000`
- **Routing**: App Router
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: React Context + SWR for data fetching
- **Editor**: Tiptap for rich text

## Task Dependency Matrix

```
Task 01: Extend User Model & Profile API
├── No dependencies (can start immediately)
└── Enables: Tasks 02, 03, 04, 05

Task 02: Articles Feature (Backend + Frontend)
├── Depends on: Task 01 (user model)
└── Enables: Task 04 (spaces can share articles)

Task 03: User Profile Pages (Frontend)
├── Depends on: Task 01 (profile API)
└── Can run parallel with: Task 02, 04

Task 04: Collaboration Spaces (Backend + Frontend)
├── Depends on: Task 01 (users)
├── Soft depends on: Task 02 (articles to share)
└── Can run parallel with: Task 03

Task 05: Feed & Discovery (Frontend)
├── Depends on: Task 01, 02 (users, articles)
└── Can run parallel with: Task 04

Task 06: Tag System & Search
├── Depends on: Task 02 (articles have tags)
└── Enhances: Task 05 (feed filtering)

Task 07: Testing & Integration
├── Depends on: All tasks
└── Final validation
```

## Parallel Execution Strategy

### Wave 1 (Can start immediately)
- **Task 01**: Extend User Model & Profile API

### Wave 2 (After Task 01)
- **Task 02**: Articles Feature
- **Task 03**: User Profile Pages
- **Task 04**: Collaboration Spaces

### Wave 3 (After Wave 2)
- **Task 05**: Feed & Discovery
- **Task 06**: Tag System & Search

### Wave 4 (Final)
- **Task 07**: Testing & Integration

## API Contracts Overview

### Authentication (Existing)
- `POST /auth/signup` - Email signup
- `POST /auth/login` - Email login
- `GET /auth/login/github` - GitHub OAuth
- `GET /auth/callback/github` - GitHub callback
- `POST /auth/logout` - Logout

### User Profiles (Task 01)
- `GET /api/users/me` - Current user profile
- `PATCH /api/users/me` - Update profile
- `GET /api/users/{username}` - Public profile
- `GET /api/users` - List users with filters

### Articles (Task 02)
- `POST /api/articles` - Create article
- `GET /api/articles` - List articles
- `GET /api/articles/{slug}` - Get article
- `PATCH /api/articles/{id}` - Update article
- `DELETE /api/articles/{id}` - Delete article
- `GET /api/articles/drafts` - User's drafts

### Spaces (Task 04)
- `POST /api/spaces` - Create space
- `GET /api/spaces` - List spaces
- `GET /api/spaces/{slug}` - Get space
- `POST /api/spaces/{id}/join` - Join space
- `POST /api/spaces/{id}/leave` - Leave space
- `POST /api/spaces/{id}/articles` - Add article
- `GET /api/spaces/{id}/articles` - Space articles
- `GET /api/spaces/{id}/members` - Space members

### Tags & Search (Task 06)
- `GET /api/tags` - List all tags with stats
- `GET /api/search` - Search articles/spaces/users

## Data Models

### User (Extended)
```typescript
interface User {
  id: string
  email: string
  display_name?: string
  username: string  // unique, from GitHub
  github_username?: string
  avatar_url?: string
  bio?: string
  company?: string
  location?: string
  expertise_tags: string[]
  created_at: Date
  updated_at?: Date
}
```

### Article
```typescript
interface Article {
  id: string
  author_id: string
  title: string
  slug: string  // unique, generated
  content: TiptapJSON
  summary?: string
  tags: string[]
  published: boolean
  view_count: number
  created_at: Date
  updated_at?: Date
  published_at?: Date
}
```

### Space
```typescript
interface Space {
  id: string
  name: string
  slug: string  // unique
  description?: string
  tags: string[]
  visibility: 'public' | 'private'
  owner_id: string
  member_count: number
  article_count: number
  created_at: Date
  updated_at?: Date
}
```

## Frontend Routes

### Public Routes
- `/` - Landing page (existing)
- `/auth/login` - Login page (existing)
- `/auth/signup` - Signup page (existing)
- `/welcome` - Welcome page (existing)

### Protected Routes
- `/feed` - Main feed (Task 05)
- `/articles/new` - Create article (Task 02)
- `/articles/[slug]` - View article (Task 02)
- `/articles/[slug]/edit` - Edit article (Task 02)
- `/users/[username]` - User profile (Task 03)
- `/settings/profile` - Edit profile (Task 03)
- `/spaces` - Browse spaces (Task 04)
- `/spaces/new` - Create space (Task 04)
- `/spaces/[slug]` - View space (Task 04)
- `/search` - Search page (Task 06)

## Component Architecture

### Layout Components
- `Navigation` - Top nav with user menu
- `Footer` - Site footer
- `ProtectedRoute` - Auth wrapper

### Article Components
- `TiptapEditor` - Rich text editor
- `ArticleCard` - Article preview
- `ArticleView` - Full article display
- `ArticleForm` - Create/edit form

### User Components
- `UserCard` - User preview
- `UserProfile` - Full profile
- `ProfileEditForm` - Edit profile

### Space Components
- `SpaceCard` - Space preview
- `SpaceHeader` - Space details
- `SpaceMemberList` - Member list
- `SpaceArticleList` - Articles in space

### Shared Components
- `TagSelector` - Multi-select tags
- `TagFilter` - Filter by tags
- `SearchBar` - Global search
- `LoadingSpinner` - Loading state
- `ErrorBoundary` - Error handling
- `EmptyState` - No data state

## State Management

### Auth Context
```typescript
interface AuthContext {
  user: User | null
  loading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}
```

### Data Fetching (SWR)
- Article queries with pagination
- Space queries with filters
- User search with debounce
- Optimistic updates for likes/joins

## Fixed AI Tags
```typescript
const AI_TAGS = [
  "LLMs", "RAG", "Agents", "Fine-tuning", "Prompting",
  "Vector DBs", "Embeddings", "Training", "Inference",
  "Ethics", "Safety", "Benchmarks", "Datasets", "Tools",
  "Computer Vision", "NLP", "Speech", "Robotics", "RL"
]
```

## Performance Requirements
- Page load < 1s
- API responses < 200ms
- Search results < 500ms
- Editor initialization < 300ms
- Image optimization via Next.js

## Security Requirements
- XSS protection via React
- CSRF protection via SameSite cookies
- SQL injection prevention via SQLAlchemy
- Rate limiting on all mutations
- Input validation on all forms
- Secure password requirements (existing)

## Testing Requirements

### Backend Tests
- Unit tests for services
- Integration tests for API endpoints
- Database migration tests
- Auth flow tests (existing)

### Frontend Tests
- Component unit tests
- Page integration tests
- E2E user flows
- Accessibility tests

## Error Handling

### Backend Errors
- 400: Bad Request (validation)
- 401: Unauthorized (auth required)
- 403: Forbidden (no permission)
- 404: Not Found
- 429: Rate Limited
- 500: Server Error

### Frontend Error States
- Network errors → Retry UI
- Validation errors → Inline messages
- Auth errors → Redirect to login
- Not found → 404 page
- Server errors → Error boundary

## MVP Simplifications
- No real-time updates (no WebSockets)
- No image uploads (use GitHub avatars)
- No email notifications
- No draft autosave (manual save only)
- No comments on articles (v2)
- No following/followers (v2)
- No private messages (v2)
- No moderation tools (v2)
- No analytics dashboard (v2)

## Implementation Notes

### For AI Agents
1. Check existing code before implementing
2. Follow established patterns in codebase
3. Use existing components when possible
4. Test each endpoint with curl examples
5. Ensure proper error handling
6. Add logging for debugging
7. Update types/interfaces as needed
8. Keep MVP scope - don't over-engineer

### Code Organization
- Backend: Feature-based modules
- Frontend: Component-based structure
- Shared: Types in separate files
- Tests: Mirror source structure

### Git Workflow
- Create feature branch per task
- Commit frequently with clear messages
- Test before marking complete
- Document any deviations from spec