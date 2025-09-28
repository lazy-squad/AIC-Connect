# UI/UX Design Document: AI Collective Hub (48-Hour MVP)

**Version:** MVP-Focused with Detailed Flows
**Date:** September 28, 2024
**Purpose:** Complete design specification for AI agent implementation in 48 hours

---

## 1. MVP Philosophy

### Core Principle: Maximum Value, Minimum Complexity
- **Build what demonstrates value**, not what's technically interesting
- **Every feature must be essential** for the core user journey
- **Polish the basics** rather than adding features
- **AI agents work best with clear, simple patterns**

### What We're Building
A trusted platform where AI professionals can:
1. **Join** with GitHub (instant credibility)
2. **Share** knowledge through articles
3. **Discover** content and experts via tags
4. **Connect** through collaboration spaces

---

## 2. Information Architecture

### 2.1 Complete Site Map
```
/ (Public Landing Page)
├── /auth
│   └── /callback (GitHub OAuth return)
├── /feed (Protected - Home after login)
│   └── ?tag={tagname} (Filtered view)
├── /articles
│   ├── /new (Protected - Create article)
│   └── /[id] (Public - View article)
├── /spaces
│   ├── / (Protected - List all spaces)
│   ├── /new (Protected - Create space)
│   └── /[id] (Public - View space)
├── /members (Protected - User directory)
│   └── /[username] (Public - View profile)
└── /profile
    └── /edit (Protected - Edit own profile)
```

### 2.2 Navigation Structure

**Desktop Header (Always Visible)**
```
[Logo/Home]                    [Feed] [Spaces] [Members]        [New Article] [Avatar ▼]
                                                                             └── Profile
                                                                             └── Sign Out
```

**Mobile Header (Simplified)**
```
[Logo]                                                          [Menu ☰]
                                                               └── Feed
                                                               └── Spaces
                                                               └── Members
                                                               └── New Article
                                                               └── Profile
                                                               └── Sign Out
```

### 2.3 Route Protection Logic
- **Public Routes:** /, /articles/[id], /members/[username], /spaces/[id]
- **Protected Routes:** Everything else requires authentication
- **Redirect Logic:** Unauthenticated users → Landing page

---

## 3. Detailed User Flows

### 3.1 First-Time User Journey
```
1. LANDING PAGE
   User sees:
   - Hero: "Where AI Professionals Share Knowledge"
   - Subtext: "Join 70,000+ AI researchers, founders, and builders"
   - [Sign in with GitHub] button (primary, centered)
   - Preview of 3 recent articles (cards, non-clickable)

2. CLICK "Sign in with GitHub"
   → Redirect to github.com/login/oauth/authorize
   → User authorizes app
   → GitHub redirects to /auth/callback?code=xxx

3. CALLBACK PROCESSING
   Frontend:
   - Shows "Authenticating..." spinner
   - Exchanges code for JWT via backend
   - Stores JWT in localStorage
   - Fetches user data

4. FIRST LOGIN DETECTION
   If user.articles_count === 0:
   → Show welcome toast: "Welcome to AI Collective! Create your first article to introduce yourself."

5. LAND ON FEED
   - Feed shows all articles
   - "New Article" button has subtle pulse animation (first time only)
```

### 3.2 Article Creation Flow (Detailed)
```
1. USER CLICKS "New Article" (from anywhere)
   Location: Top-right header button (desktop) or menu (mobile)

2. ARTICLE CREATION PAGE (/articles/new)
   Layout:
   ┌─────────────────────────────────────┐
   │ Create Article                   [X]│
   ├─────────────────────────────────────┤
   │ Title*                              │
   │ [________________________________]  │
   │ (0/200 characters)                  │
   │                                     │
   │ Content*                            │
   │ [B][I][H2][H3][•][1.]["][🔗]       │
   │ ┌─────────────────────────────────┐ │
   │ │                                 │ │
   │ │  Start writing...               │ │
   │ │                                 │ │
   │ │                                 │ │
   │ └─────────────────────────────────┘ │
   │ (Min 50 characters)                 │
   │                                     │
   │ Tags* (Select 1-3)                  │
   │ [Dropdown: Select tags      ▼]      │
   │ Selected: [LLMs ×] [RAG ×]         │
   │                                     │
   │ [Cancel]           [Publish Article]│
   └─────────────────────────────────────┘

3. VALIDATION RULES
   - Title: Required, 10-200 characters
   - Content: Required, 50+ characters
   - Tags: Required, 1-3 selections
   - Real-time character count
   - Disable publish until valid

4. ON PUBLISH CLICK
   - Button changes to "Publishing..." with spinner
   - API call to POST /api/articles
   - Success: Redirect to /articles/[newId]
   - Error: Toast with message, button returns to "Publish Article"

5. ARTICLE VIEW PAGE
   User lands on their published article
   - Shows success toast: "Article published!"
   - Full article display
   - Share button (copies URL)
```

### 3.3 Content Discovery Flow (Detailed)
```
1. FEED PAGE (Default View)
   ┌─────────────────────────────────────┐
   │ All Articles          [New Article] │
   ├─────────────────────────────────────┤
   │ Filter by topic:                    │
   │ [All] [LLMs] [Agents] [Computer    │
   │ Vision] [RAG] [Safety] [More...]    │
   ├─────────────────────────────────────┤
   │ ┌─────────────────────────────────┐ │
   │ │ Building Production RAG Systems  │ │
   │ │ by Sarah Chen · 2 hours ago     │ │
   │ │                                  │ │
   │ │ Key lessons from deploying RAG   │ │
   │ │ at scale for enterprise...       │ │
   │ │                                  │ │
   │ │ [RAG] [LLMs]                    │ │
   │ └─────────────────────────────────┘ │
   │                                      │
   │ ┌─────────────────────────────────┐ │
   │ │ Computer Vision in 2024          │ │
   │ │ by Alex Kumar · 5 hours ago     │ │
   │ │ ...                              │ │
   │ └─────────────────────────────────┘ │
   │                                      │
   │ [Load More Articles]                 │
   └─────────────────────────────────────┘

2. TAG FILTERING
   User clicks "RAG" tag:
   - URL changes to /feed?tag=RAG
   - Tag button shows active state (primary color)
   - Feed updates to show only RAG articles
   - Shows count: "12 articles about RAG"
   - [Clear Filter] button appears

3. ARTICLE INTERACTION
   User clicks article card:
   → Navigate to /articles/[id]
   → Show full article with:
     - Author info box (avatar, name, bio)
     - Full formatted content
     - Tags (clickable → filter feed)
     - "More by this author" section

4. AUTHOR DISCOVERY
   User clicks author name:
   → Navigate to /members/[username]
   → Show profile with:
     - GitHub info (avatar, company, location)
     - Bio (if set)
     - Expertise tags
     - All articles by author
```

### 3.4 Collaboration Space Flow (Detailed)
```
1. SPACES LIST PAGE (/spaces)
   ┌─────────────────────────────────────┐
   │ Collaboration Spaces  [Create Space] │
   ├─────────────────────────────────────┤
   │ Active spaces where teams           │
   │ coordinate their work                │
   ├─────────────────────────────────────┤
   │ ┌─────────────────────────────────┐ │
   │ │ RAG Working Group                │ │
   │ │                                  │ │
   │ │ Building better retrieval        │ │
   │ │ systems together                 │ │
   │ │                                  │ │
   │ │ 5 resources · by Sarah Chen     │ │
   │ └─────────────────────────────────┘ │
   │                                      │
   │ ┌─────────────────────────────────┐ │
   │ │ AI Safety Research               │ │
   │ │ ...                              │ │
   │ └─────────────────────────────────┘ │
   └─────────────────────────────────────┘

2. CREATE SPACE (/spaces/new)
   ┌─────────────────────────────────────┐
   │ Create Collaboration Space           │
   ├─────────────────────────────────────┤
   │ Title*                              │
   │ [RAG Working Group_____________]    │
   │                                     │
   │ Description*                        │
   │ [Building better retrieval systems  │
   │  together. Weekly sync on Tuesdays.]│
   │                                     │
   │ Resources                           │
   │ Add links to your team's resources: │
   │                                     │
   │ URL: [github.com/team/rag-toolkit] │
   │ Description: [Our main repository]  │
   │ [Add Resource]                      │
   │                                     │
   │ Added:                              │
   │ • github.com/team/rag-toolkit      │
   │   Our main repository          [×]  │
   │                                     │
   │ Tags (Select 1-3)                   │
   │ [RAG] [LLMs]                       │
   │                                     │
   │ [Cancel]           [Create Space]   │
   └─────────────────────────────────────┘

3. SPACE VIEW PAGE (/spaces/[id])
   ┌─────────────────────────────────────┐
   │ RAG Working Group                    │
   │ by Sarah Chen                        │
   ├─────────────────────────────────────┤
   │ Building better retrieval systems    │
   │ together. Weekly sync on Tuesdays.   │
   ├─────────────────────────────────────┤
   │ Resources                            │
   │                                      │
   │ 📦 github.com/team/rag-toolkit      │
   │    Our main repository               │
   │                                      │
   │ 📝 notion.so/team/rag-docs          │
   │    Documentation and guides          │
   │                                      │
   │ 💬 slack://channel?team=T123&id=C456│
   │    Team discussion channel           │
   ├─────────────────────────────────────┤
   │ [Copy Space Link]                    │
   └─────────────────────────────────────┘
```

### 3.5 User Profile Flow (Detailed)
```
1. VIEWING PROFILE (/members/[username])
   ┌─────────────────────────────────────┐
   │ [Avatar]  Sarah Chen                 │
   │           @sarahchen                 │
   │           San Francisco, CA          │
   │           OpenAI                     │
   ├─────────────────────────────────────┤
   │ Bio                                  │
   │ Building RAG systems at scale.       │
   │ Previously at Anthropic.             │
   ├─────────────────────────────────────┤
   │ Expertise                            │
   │ [RAG] [LLMs] [ML Ops]               │
   ├─────────────────────────────────────┤
   │ Articles (5)                         │
   │                                      │
   │ • Building Production RAG Systems    │
   │   2 hours ago                       │
   │                                      │
   │ • Optimizing Vector Databases        │
   │   3 days ago                        │
   │                                      │
   │ [View All Articles]                  │
   └─────────────────────────────────────┘

2. EDITING OWN PROFILE (/profile/edit)
   (Only visible on own profile)

   ┌─────────────────────────────────────┐
   │ Edit Profile                         │
   ├─────────────────────────────────────┤
   │ GitHub Info (Cannot edit)            │
   │ Name: Sarah Chen                     │
   │ Username: sarahchen                  │
   │ Company: OpenAI                      │
   │ Location: San Francisco, CA          │
   ├─────────────────────────────────────┤
   │ Bio                                  │
   │ [Building RAG systems at scale.     │
   │  Previously at Anthropic._____]     │
   │                                     │
   │ Expertise Tags (Select up to 5)     │
   │ [RAG ×] [LLMs ×] [ML Ops ×]        │
   │ [Add more ▼]                        │
   │                                     │
   │ [Cancel]           [Save Changes]   │
   └─────────────────────────────────────┘
```

---

## 4. Component Specifications (Detailed)

### 4.1 Feed Card (Most Important Component)
```
Desktop (Width: 100%, Max: 680px)
┌────────────────────────────────────────┐
│ Title of the Article Here              │ ← font-semibold text-lg
│ by Author Name · 2 hours ago           │ ← text-sm text-muted-foreground
│                                         │
│ This is the excerpt of the article     │ ← text-base, line-clamp-2
│ content that gives readers a preview...│
│                                         │
│ [LLMs] [RAG] [Production]             │ ← gap-2, badge variant="secondary"
└────────────────────────────────────────┘
  ↑ border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer

Mobile (Width: 100%)
┌────────────────────────────────────────┐
│ Title of the Article Here              │
│ by Author Name · 2h                    │ ← Shortened time on mobile
│                                         │
│ This is the excerpt of the article...  │ ← line-clamp-3 on mobile
│                                         │
│ [LLMs] [RAG]                          │ ← Max 2 tags shown on mobile
└────────────────────────────────────────┘
```

**Interaction States:**
- Default: White background, gray border
- Hover: Shadow-md, slight scale (1.01)
- Active: Scale(0.99) for click feedback
- Loading: Skeleton with pulse animation

### 4.2 Article Editor Component
```
┌────────────────────────────────────────┐
│ Create Article                    [×]  │ ← Header with close button
├────────────────────────────────────────┤
│                                        │
│ Title *                                │
│ ┌────────────────────────────────────┐ │
│ │Building a Multi-Agent System       │ │ ← Input with counter
│ └────────────────────────────────────┘ │
│ 35/200 characters                      │
│                                        │
│ ┌────────────────────────────────────┐ │
│ │[B][I][H2][H3][•][1.]["][Link]     │ │ ← Toolbar sticky on scroll
│ ├────────────────────────────────────┤ │
│ │                                    │ │
│ │ Start writing your article...      │ │ ← Min height: 300px
│ │                                    │ │
│ │                                    │ │
│ └────────────────────────────────────┘ │
│ 156 characters (minimum: 50)           │
│                                        │
│ Tags * (Select 1-3)                    │
│ ┌────────────────────────────────────┐ │
│ │ Select tags...                  ▼ │ │ ← Command/Select component
│ └────────────────────────────────────┘ │
│ Selected: [LLMs ×] [Agents ×]         │
│                                        │
│ ┌─────────────┬──────────────────────┐ │
│ │   Cancel    │  Publish Article     │ │
│ └─────────────┴──────────────────────┘ │
└────────────────────────────────────────┘
```

**Toolbar Buttons:**
- Bold (Cmd+B)
- Italic (Cmd+I)
- Heading 2
- Heading 3
- Bullet List
- Numbered List
- Blockquote
- Link (Cmd+K)

### 4.3 User Avatar Component
```
Small (32x32) - Used in cards
[●]

Medium (40x40) - Used in header
[●] ▼

Large (64x64) - Used in profile
┌────┐
│ ● │
└────┘

With Fallback (When no avatar)
[SC] ← Initials with background color based on username hash
```

### 4.4 Empty States (Critical for Polish)
```
Feed Empty State
┌────────────────────────────────────────┐
│                                        │
│            📝                          │
│                                        │
│     No articles yet                   │
│                                        │
│  Be the first to share knowledge      │
│  with the community                    │
│                                        │
│      [Create Article]                  │
│                                        │
└────────────────────────────────────────┘

Space Empty State
┌────────────────────────────────────────┐
│                                        │
│            🚀                          │
│                                        │
│   No collaboration spaces yet          │
│                                        │
│  Create a space to coordinate         │
│  with your team                       │
│                                        │
│      [Create Space]                    │
│                                        │
└────────────────────────────────────────┘
```

### 4.5 Loading States (Use Skeletons)
```
Feed Loading
┌────────────────────────────────────────┐
│ ████████████████████                   │ ← Pulse animation
│ ███████ · ████                        │
│                                        │
│ ████████████████████████████████       │
│ ████████████████████████               │
│                                        │
│ ███  ███  ███                         │
└────────────────────────────────────────┘

Profile Loading
┌────────────────────────────────────────┐
│ [███]  ████████████                    │
│        ████████                        │
│        ████████████                    │
├────────────────────────────────────────┤
│ ████████████████████████████████       │
│ ████████████████████                   │
└────────────────────────────────────────┘
```

---

## 5. Interaction Patterns

### 5.1 Form Interactions
```
Input Field States:
- Default: Gray border
- Focus: Blue border + ring
- Error: Red border + message below
- Success: Green check icon (optional)
- Disabled: Gray background

Button States:
- Default: Solid background
- Hover: Darken 10%
- Active: Scale(0.95)
- Loading: Spinner + "Loading..."
- Disabled: Opacity 50%
```

### 5.2 Navigation Patterns
```
Page Transitions:
- Instant navigation (no fancy transitions)
- Show loading state immediately
- Keep header stable (no layout shift)

Link Behavior:
- All cards are clickable
- Tags always filter feed
- Author names go to profile
- External links open new tab
```

### 5.3 Feedback Patterns
```
Success Toast (Top-right, auto-dismiss 3s):
┌─────────────────────────┐
│ ✓ Article published!    │
└─────────────────────────┘

Error Toast (Top-right, manual dismiss):
┌─────────────────────────┐
│ ⚠ Something went wrong  │
│   Please try again   [×] │
└─────────────────────────┘

Loading Inline:
[Publishing...    ◉]
```

---

## 6. Mobile Responsive Design

### 6.1 Breakpoint Behavior
```
Mobile (<640px):
- Single column
- Full-width cards
- Stacked navigation
- Hamburger menu
- Larger touch targets (44px min)

Tablet (640-1024px):
- 2-column grid for some content
- Side-by-side layouts where sensible

Desktop (>1024px):
- Centered content (max-width: 1280px)
- Multi-column layouts
- Hover states enabled
```

### 6.2 Mobile-Specific Adjustments
```
Header Mobile:
[Logo]                    [☰]

Feed Card Mobile:
- Smaller font for metadata
- Show only 2 tags max
- 3-line excerpt

Editor Mobile:
- Full-screen mode
- Toolbar scrolls horizontally
- Larger buttons (44px targets)

Profile Mobile:
- Stack all sections vertically
- Collapse long lists with "Show more"
```

---

## 7. Technical Implementation Guide

### 7.1 Route Structure
```javascript
// Public routes (no auth required)
const publicRoutes = [
  '/',
  '/articles/[id]',
  '/members/[username]',
  '/spaces/[id]'
]

// Protected routes (require auth)
const protectedRoutes = [
  '/feed',
  '/articles/new',
  '/spaces',
  '/spaces/new',
  '/members',
  '/profile/edit'
]

// Auth check pattern
if (protectedRoute && !localStorage.getItem('token')) {
  redirect('/')
}
```

### 7.2 API Endpoints Needed
```
Authentication:
POST   /api/auth/github/callback  { code }
GET    /api/auth/me

Articles:
GET    /api/articles              ?tag=x&limit=20&offset=0
POST   /api/articles              { title, content, tags }
GET    /api/articles/{id}

Users:
GET    /api/users                 ?limit=20&offset=0
GET    /api/users/{username}
PATCH  /api/users/me              { bio, expertise_tags }

Spaces:
GET    /api/spaces                ?limit=20&offset=0
POST   /api/spaces                { title, description, tags, links }
GET    /api/spaces/{id}

Tags:
GET    /api/tags                  Returns fixed list
```

### 7.3 Data Models
```typescript
// User (from GitHub + custom fields)
{
  id: string
  username: string
  name: string
  avatar_url: string
  company?: string
  location?: string
  bio?: string          // Custom
  expertise_tags: string[]  // Custom
  created_at: Date
}

// Article
{
  id: string
  title: string
  content: object      // Tiptap JSON
  excerpt: string      // First 200 chars
  tags: string[]
  author_id: string
  author: User         // Populated
  created_at: Date
  updated_at: Date
}

// Space
{
  id: string
  title: string
  description: string
  tags: string[]
  links: Link[]
  owner_id: string
  owner: User          // Populated
  created_at: Date
}

// Link
{
  url: string
  description?: string
}
```

### 7.4 State Management Pattern
```typescript
// Simple useState for everything
// No Redux, no Context (except maybe auth)

// Page component pattern:
function FeedPage() {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [tag, setTag] = useState(null)

  useEffect(() => {
    fetchArticles(tag)
      .then(setArticles)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [tag])

  if (loading) return <FeedSkeleton />
  if (error) return <ErrorState />
  if (!articles.length) return <EmptyState />

  return <FeedGrid articles={articles} onTagClick={setTag} />
}
```

---

## 8. Fixed Tag List

```javascript
const AI_TAGS = [
  'LLMs',           // Large Language Models
  'Agents',         // AI Agents
  'RAG',            // Retrieval Augmented Generation
  'Fine-tuning',    // Model fine-tuning
  'Prompting',      // Prompt engineering
  'Computer Vision',// CV/Image AI
  'ML Ops',         // Machine Learning Operations
  'AI Safety',      // Safety & Alignment
  'Data',           // Data Engineering
  'Research',       // AI Research
  'Production',     // Production systems
  'Open Source'     // OSS projects
]
```

---

## 9. Polish Details That Matter

### 9.1 Micro-Interactions
- **Card hover:** Subtle shadow (transition 200ms)
- **Button click:** Scale to 0.95 (50ms)
- **Tag click:** Background color change
- **Link hover:** Underline appear
- **Focus states:** Blue ring (2px)

### 9.2 Performance Optimizations
- **Pagination:** Load 20 items at a time
- **Images:** Lazy load all avatars
- **Debouncing:** Search input (300ms)
- **Caching:** Keep previous page data
- **Optimistic UI:** Update immediately, rollback on error

### 9.3 Edge Cases to Handle
- **No network:** "Check your connection"
- **Empty search:** "No results found"
- **Long content:** Truncate with ellipsis
- **Missing avatar:** Show initials
- **Failed image:** Show placeholder
- **Session expired:** Redirect to login

---

## 10. Implementation Timeline (48 Hours)

### Phase 1: Core Setup (0-8 hours)
```
Backend:
- [ ] FastAPI setup with CORS
- [ ] PostgreSQL + models
- [ ] GitHub OAuth endpoint
- [ ] JWT generation

Frontend:
- [ ] Next.js + TypeScript
- [ ] shadcn/ui installation
- [ ] Basic routing
- [ ] Auth flow
```

### Phase 2: Essential Features (8-24 hours)
```
Backend:
- [ ] Articles CRUD
- [ ] Users endpoints
- [ ] Tags endpoint
- [ ] Basic validation

Frontend:
- [ ] Feed page with cards
- [ ] Article creation with Tiptap
- [ ] Tag filtering
- [ ] User profiles
```

### Phase 3: Collaboration (24-32 hours)
```
Backend:
- [ ] Spaces CRUD
- [ ] Links handling

Frontend:
- [ ] Spaces list/create
- [ ] Space detail view
- [ ] Member directory
```

### Phase 4: Polish (32-40 hours)
```
All Components:
- [ ] Loading states
- [ ] Empty states
- [ ] Error handling
- [ ] Mobile responsive
- [ ] Form validation
- [ ] Toast notifications
```

### Phase 5: Demo Prep (40-48 hours)
```
Final Steps:
- [ ] Seed realistic data
- [ ] Fix critical bugs only
- [ ] Test full user journey
- [ ] Deploy to VM
- [ ] Practice demo
```

---

## 11. Demo Script (Detailed - 3 minutes)

### Setup (Before Demo)
- Seed 10 articles with variety of tags
- Create 3 users with different expertise
- Create 2 collaboration spaces
- Clear browser cache

### Script
```
1. LANDING (10 seconds)
   "This is AI Collective Hub - where AI professionals share knowledge"
   - Point out GitHub sign-in (trust)
   - Show preview of content

2. AUTHENTICATION (15 seconds)
   - Click "Sign in with GitHub"
   - Show GitHub OAuth page briefly
   - Return authenticated
   "Notice how quick that was - no forms to fill"

3. FEED EXPLORATION (30 seconds)
   - "Here's our community's latest insights"
   - Scroll to show variety
   - Click "RAG" tag
   - "Instantly filter to your interests"
   - Show filtered results

4. CREATE ARTICLE (45 seconds)
   - Click "New Article"
   - Type: "Lessons from Building RAG at Scale"
   - Add formatted content:
     - Bold important point
     - Bullet list of tips
   - Select tags: RAG, Production
   - Click Publish
   - "Published instantly, no drafts needed"

5. USER DISCOVERY (30 seconds)
   - Go to Members directory
   - "Find experts in specific areas"
   - Click on a profile
   - Show their articles and expertise
   - "Connect with the right people"

6. COLLABORATION SPACE (45 seconds)
   - Go to Spaces
   - Create "RAG Working Group"
   - Add description
   - Add GitHub repo link
   - Add Notion doc link
   - "Aggregate all your team's resources"
   - Show created space

7. WRAP UP (15 seconds)
   - Return to feed
   - "Built in 48 hours"
   - "Fully open source"
   - "Deploy to your own infrastructure"
```

---

## 12. Success Criteria

The MVP is successful if:
1. ✅ User can sign in with GitHub in < 30 seconds
2. ✅ User can create an article in < 2 minutes
3. ✅ User can filter content by tags instantly
4. ✅ User can find other members by expertise
5. ✅ User can create a collaboration space
6. ✅ All core features work on mobile
7. ✅ No critical errors during demo

---

## 13. Component Priority List

Build these in order:
1. **AuthFlow** - Nothing works without it
2. **FeedCard** - Most visible component
3. **ArticleEditor** - Core value prop
4. **TagFilter** - Enables discovery
5. **ProfileView** - Community aspect
6. **SpaceCard** - Collaboration feature
7. **EmptyStates** - Polish
8. **LoadingStates** - Polish

---

## Key Reminders for AI Agents

1. **Use shadcn/ui components** - Don't build from scratch
2. **Client-side only** - No SSR for MVP
3. **Simple patterns** - useState, useEffect, fetch
4. **Mobile-first** - Test on phone-sized viewport
5. **Error handling** - Every API call needs try/catch
6. **Loading states** - Never show blank screen
7. **Keep it simple** - 48 hours only!

This document provides complete specifications for building a polished MVP in 48 hours.