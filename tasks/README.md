# AI Collective Hub - Implementation Tasks

## Quick Start for AI Agents

This folder contains comprehensive implementation specifications for building the AI Collective Hub MVP. Each task is self-contained with complete frontend and backend requirements.

## Task Files

1. **[00-implementation-overview.md](./00-implementation-overview.md)** - Architecture, dependencies, and implementation strategy
2. **[01-user-profiles-complete.md](./01-user-profiles-complete.md)** - Extended user profiles with GitHub integration
3. **[02-articles-complete.md](./02-articles-complete.md)** - Article system with Tiptap editor
4. **[03-spaces-complete.md](./03-spaces-complete.md)** - Collaboration spaces
5. **[04-feed-discovery-complete.md](./04-feed-discovery-complete.md)** - Personalized feeds and discovery
6. **[05-tags-search-complete.md](./05-tags-search-complete.md)** - Tag system and search functionality

## Current Codebase Status

### ✅ Already Implemented
- Basic authentication (email + password)
- GitHub OAuth flow
- Session management with JWT cookies
- Basic User, OAuthAccount models
- Health check endpoints
- Frontend auth pages (login/signup)
- Database migrations setup

### 🔨 To Be Implemented
- Extended user profiles (Task 01)
- Article creation and management (Task 02)
- Collaboration spaces (Task 03)
- Feed and discovery (Task 04)
- Tag system and search (Task 05)

## Implementation Strategy

### Phase 1: Foundation (Task 01)
**Start immediately** - No dependencies
- Extend User model with GitHub fields
- Add expertise tags
- Create profile API endpoints
- Build profile pages

### Phase 2: Core Features (Tasks 02, 03)
**After Phase 1** - Can run in parallel
- **Task 02**: Article system with Tiptap
- **Task 03**: Collaboration spaces

### Phase 3: Discovery (Tasks 04, 05)
**After Phase 2**
- **Task 04**: Feed and trending
- **Task 05**: Tags and search

## For Each Task

### 1. Pre-Implementation Checklist
```bash
# Check existing code
cat apps/api/src/aic_hub/models/*.py
cat apps/api/src/aic_hub/routes/*.py
ls -la apps/web/src/components/
ls -la apps/web/src/app/

# Check dependencies
cat apps/api/pyproject.toml
cat apps/web/package.json

# Check migrations
ls -la apps/api/alembic/versions/
```

### 2. Backend Implementation Order
1. Create/extend models
2. Create migration: `uv run alembic revision --autogenerate -m "Description"`
3. Run migration: `uv run alembic upgrade head`
4. Create service layer
5. Create API endpoints
6. Add to main.py router
7. Test with curl

### 3. Frontend Implementation Order
1. Install dependencies if needed
2. Create type definitions
3. Build components (bottom-up)
4. Create pages
5. Add routing
6. Setup state management
7. Connect to API
8. Test UI flows

### 4. Testing Each Endpoint
```bash
# Create/Update
curl -X POST http://localhost:3000/api/[endpoint] \
  -H "Content-Type: application/json" \
  -H "Cookie: aic_hub_session=..." \
  -d '{"field": "value"}'

# Read
curl http://localhost:3000/api/[endpoint] \
  -H "Cookie: aic_hub_session=..."

# With query params
curl "http://localhost:3000/api/[endpoint]?param=value"
```

## Key Technical Decisions

### Backend
- **Framework**: FastAPI with async SQLAlchemy
- **Database**: PostgreSQL 16
- **Auth**: JWT in HttpOnly cookies
- **Search**: PostgreSQL full-text search (not Elasticsearch)
- **File Storage**: None for MVP (no image uploads)

### Frontend
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: React Context + SWR
- **Editor**: Tiptap for rich text
- **Forms**: Controlled components with validation

### Architecture
- **Monorepo**: pnpm workspaces
- **API**: Separate FastAPI backend (port 4000)
- **Web**: Next.js frontend (port 3000)
- **Proxy**: Next.js proxies /api to backend

## Common Patterns

### Backend Patterns
```python
# Service layer pattern
class ArticleService:
    @staticmethod
    async def create_article(db: AsyncSession, ...) -> Article:
        # Business logic here
        pass

# Dependency injection
async def get_current_user(
    session_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Auth logic
    pass

# Route with auth
@router.post("/articles")
async def create_article(
    data: ArticleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Route logic
    pass
```

### Frontend Patterns
```typescript
// SWR for data fetching
export function useArticles(params) {
  return useSWR<ArticleList>(
    `/api/articles?${buildQuery(params)}`,
    fetcher
  )
}

// Protected route
export default function ProtectedPage() {
  return (
    <ProtectedRoute>
      {/* Page content */}
    </ProtectedRoute>
  )
}

// Form handling
const handleSubmit = async (data: FormData) => {
  try {
    const response = await fetch('/api/endpoint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    })
    // Handle response
  } catch (error) {
    // Handle error
  }
}
```

## Environment Setup

### Required Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/aic_hub

# GitHub OAuth (existing)
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx

# Security (existing)
SECRET_KEY=xxx
JWT_SECRET_KEY=xxx

# API
NEXT_PUBLIC_API_BASE_URL=/api
```

### Development Commands
```bash
# Start all services
docker compose -f docker/compose.yaml up

# API development
cd apps/api
uv run uvicorn aic_hub.main:app --reload --port 4000

# Frontend development
cd apps/web
pnpm dev

# Run migrations
cd apps/api
uv run alembic upgrade head

# Create migration
uv run alembic revision --autogenerate -m "Description"
```

## Quality Checklist

For each implementation:
- [ ] Existing code checked first
- [ ] Models match specification
- [ ] Migrations run successfully
- [ ] API endpoints tested with curl
- [ ] Frontend components render
- [ ] Forms validate properly
- [ ] Error states handled
- [ ] Loading states shown
- [ ] Mobile responsive
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] Tests written (if time permits)

## MVP Scope Reminders

### What to Build
- ✅ GitHub OAuth (existing)
- ✅ User profiles with expertise
- ✅ Articles with Tiptap editor
- ✅ Collaboration spaces
- ✅ Feed with filters
- ✅ Tag system (fixed list)
- ✅ Search functionality

### What NOT to Build (v2)
- ❌ Real-time updates (WebSockets)
- ❌ Image uploads
- ❌ Email notifications
- ❌ Comments on articles
- ❌ Following system
- ❌ Private messages
- ❌ Admin dashboard
- ❌ Analytics
- ❌ Draft autosave

## Troubleshooting

### Common Issues

**Migration fails**
```bash
# Check current version
uv run alembic current

# See history
uv run alembic history

# Downgrade if needed
uv run alembic downgrade -1
```

**CORS errors**
- Check `apps/api/src/aic_hub/main.py` CORS configuration
- Ensure credentials: 'include' in fetch

**Cookie not setting**
- Check SameSite and Secure settings
- Use HTTP in development

**TypeScript errors**
```bash
cd apps/web
pnpm typecheck
```

**Database connection issues**
```bash
# Check PostgreSQL is running
docker compose -f docker/compose.yaml ps

# Check connection
docker compose -f docker/compose.yaml logs postgres
```

## Success Criteria

The MVP is complete when:
1. Users can sign up/login with GitHub ✅ (existing)
2. Users can create and edit profiles
3. Users can write articles with rich text
4. Users can create and join spaces
5. Users can discover content via feeds
6. Users can filter by AI tags
7. Users can search across platform
8. All features work on mobile
9. No critical bugs
10. Performance is acceptable (<1s page loads)

## Questions?

If you encounter issues:
1. Check the existing codebase first
2. Refer to the specific task documentation
3. Look for similar patterns in existing code
4. Test incrementally
5. Use the simplest solution that works

Remember: This is an MVP for a 48-hour hackathon. Focus on functionality over perfection.