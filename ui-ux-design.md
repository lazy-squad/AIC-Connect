# UI/UX Design Document: AI Collective Hub

**Version:** 1.0
**Date:** September 28, 2024
**Author:** Design Team
**Status:** Design Specification for MVP

---

## 1. Design Philosophy & Principles

### 1.1 Core Design Values

- **Trust Through Transparency:** Every interaction should reinforce credibility and expertise
- **Efficiency First:** Minimize clicks, maximize value for time-constrained professionals
- **Progressive Complexity:** Simple surface, powerful depth when needed
- **Content is King:** UI should fade away, letting knowledge shine
- **Respect for Privacy:** Clear, granular control over personal information

### 1.2 Design Principles

1. **Scannable Information Architecture:** F-pattern layouts, clear visual hierarchy
2. **Predictable Interactions:** Consistent patterns across all touchpoints
3. **Immediate Feedback:** Every action acknowledged within 100ms (optimistic UI updates)
4. **Graceful Degradation:** Beautiful on cutting-edge devices, functional everywhere
5. **Accessibility by Default:** WCAG 2.2 AA compliance, keyboard-first navigation

---

## 2. User Flows

### 2.1 Onboarding Flow

```
Landing → GitHub OAuth → Profile Seeding → Profile Enhancement → Home Feed
```

**Flow Details:**

1. **Landing Page (Unauthenticated)**
   - Hero with value proposition
   - Single CTA: "Sign in with GitHub"
   - Trust signals: member count, featured content preview
   - No registration form (GitHub-only)

2. **GitHub OAuth**
   - Redirect to GitHub authorization
   - Loading state with progress indicator
   - Error handling with retry option

3. **Profile Seeding (Automatic)**
   - Welcome modal with fetched GitHub data
   - Preview of auto-populated profile
   - Continue button to enhancement

4. **Profile Enhancement (First-time only)**
   - Multi-step wizard (3 steps max)
   - Step 1: Bio & expertise (rich text editor)
   - Step 2: Select AI expertise areas (tag selector)
   - Step 3: Current focus & looking for
   - Skip option available (complete later)
   - Progress indicator

5. **First Feed View**
   - Personalized welcome message
   - Quick tour tooltip overlay (dismissible)
   - Suggested first actions

### 2.2 Content Creation Flow

```
Feed → New Article → Editor → Preview → Publish → Share
```

**Flow Details:**

1. **Initiation**
   - Floating Action Button (FAB) on mobile
   - Header "New Article" button on desktop
   - Keyboard shortcut: Cmd/Ctrl + N

2. **Article Editor**
   - Full-screen focus mode
   - Auto-save every 30 seconds
   - Draft indicator in header
   - Exit confirmation if unsaved changes

3. **Publishing**
   - Preview modal before publish
   - Tag selection (required)
   - Visibility settings
   - Schedule option (future)

4. **Post-Publish**
   - Success toast with share options
   - View article / Back to feed options
   - Analytics preview (views, likes)

### 2.3 Content Discovery Flow

```
Home → Browse/Filter → Read → Engage → Profile → Follow
```

**Flow Details:**

1. **Feed Navigation**
   - Tab switcher: Global | Personalized
   - Filter bar with tag chips
   - Sort options: Recent | Popular | Discussed

2. **Article Interaction**
   - Card-based preview (title, excerpt, author, tags)
   - Hover: subtle elevation change
   - Click: smooth transition to article view
   - Like/Save buttons always visible

3. **Reading Experience**
   - Clean reader view
   - Floating action bar (like, save, share)
   - Author card sidebar (desktop) / bottom sheet (mobile)
   - Related articles at end

### 2.4 Collaboration Space Flow

```
Spaces → Create/Browse → Configure → Add Resources → Invite → Manage
```

**Flow Details:**

1. **Space Creation**
   - Modal wizard (2 steps)
   - Step 1: Title, description, tags
   - Step 2: Initial resources (optional)
   - Create & configure / Create & invite options

2. **Resource Management**
   - Drag-and-drop link addition
   - Auto-detect link type (Slack/GitHub/Notion)
   - Manual metadata editing
   - Reorder via drag handles

3. **Member Management**
   - Search and invite by username
   - Permission levels (viewer/contributor/admin)
   - Bulk actions for multiple members

### 2.5 User Discovery Flow

```
Directory → Search/Filter → Profile View → Connect/Follow
```

**Flow Details:**

1. **Member Directory**
   - Grid view (default) / List view toggle
   - Search by name, expertise, location
   - Filter by expertise areas, location
   - Infinite scroll pagination

2. **Profile Interaction**
   - Quick preview on hover (desktop)
   - Full profile in modal or new page
   - Action buttons: Follow, Message (future), Block

### 2.6 Admin Dashboard Flow

```
Admin Entry → Metrics Overview → Drill-down → Export
```

**Flow Details:**

1. **Dashboard Access**
   - Separate /admin route
   - Role-based access control
   - Return to main app button

2. **Metrics Navigation**
   - Tab-based sections
   - Date range selector
   - Refresh button with last-updated timestamp

3. **Data Export**
   - Select metrics to export
   - CSV download with progress
   - Email option for large exports

---

## 3. Information Architecture

### 3.1 Site Map

```
/
├── / (landing page)
├── /auth
│   └── /github/callback (OAuth callback)
├── /feed (authenticated home)
│   ├── ?view=global
│   └── ?view=personalized
├── /articles
│   ├── /new
│   └── /[id]
├── /spaces
│   ├── /new
│   └── /[id]
├── /members
│   └── /[username]
├── /profile
│   ├── /edit
│   └── /settings
├── /admin (role-based)
│   ├── /metrics
│   └── /export
└── /api
    ├── /auth/[...]
    ├── /users/[...]
    └── /articles/[...]
```

### 3.2 Navigation Structure

**Primary Navigation (Header)**
- Logo/Home
- Feed
- Spaces
- Members
- New Article (CTA)
- Profile Menu

**Secondary Navigation (Context-based)**
- Feed filters
- Tag selector
- Sort options
- View toggles

**Mobile Navigation**
- Bottom tab bar (4 items max)
- Hamburger menu for overflow
- FAB for primary action

---

## 4. Component Design System

### 4.1 Layout Components

#### AppShell
```typescript
interface AppShellProps {
  header: React.ReactNode;
  sidebar?: React.ReactNode; // Desktop only
  main: React.ReactNode;
  footer?: React.ReactNode;
  mobileNav?: React.ReactNode;
}
```

**Specifications:**
- Max width: 1440px (content), full width (header/footer)
- Breakpoints: 640px (mobile), 768px (tablet), 1024px (desktop)
- Spacing: 8px base unit system

#### Header
```typescript
interface HeaderProps {
  user?: User;
  notifications?: number;
  onNewArticle: () => void;
}
```

**Design:**
- Height: 64px (desktop), 56px (mobile)
- Sticky positioning with backdrop blur
- Logo left, actions right
- Search bar center (desktop only)

#### FeedCard
```typescript
interface FeedCardProps {
  article: Article;
  variant: 'compact' | 'expanded';
  onLike: () => void;
  onSave: () => void;
}
```

**Design:**
- Border radius: 8px
- Padding: 16px
- Hover state: elevation 2 → 4
- Image aspect ratio: 16:9 (optional)

### 4.2 Form Components

#### RichTextEditor (Tiptap)
```typescript
import { JSONContent } from '@tiptap/react';

interface RichTextEditorProps {
  content?: JSONContent;
  onChange: (content: JSONContent) => void;
  placeholder?: string;
  maxLength?: number;
}
```

**Toolbar Items:**
- Format: H1-H3, Bold, Italic, Underline
- Lists: Bullet, Numbered
- Insert: Link, Image, Code block
- Actions: Undo, Redo

**Design:**
- Floating toolbar on text selection
- Slash commands for power users
- Markdown shortcuts enabled
- Word count in footer

#### TagSelector
```typescript
interface TagSelectorProps {
  selected: string[];
  available: Tag[];
  max?: number;
  onChange: (tags: string[]) => void;
}
```

**Design:**
- Chip-based selection
- Typeahead search
- Max 5 tags per item
- Popular tags highlighted

#### ProfileForm
```typescript
interface ProfileFormProps {
  user: User;
  onSave: (updates: Partial<User>) => void;
}
```

**Fields:**
- Bio: Rich text, 500 char limit
- Expertise: Multi-select tags
- Current Focus: Text input
- Looking For: Checkbox group
- Visibility: Radio group

### 4.3 Feedback Components

#### Toast
```typescript
interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'info';
  duration?: number;
  action?: { label: string; onClick: () => void };
}
```

**Design:**
- Position: top-right (desktop), top-center (mobile)
- Auto-dismiss: 4s default
- Stacking for multiple toasts
- Swipe to dismiss (mobile)

#### LoadingState
```typescript
interface LoadingStateProps {
  variant: 'spinner' | 'skeleton' | 'progress';
  label?: string;
}
```

**Usage:**
- Spinner: Actions < 1s
- Skeleton: Content loading
- Progress: File uploads, exports

#### EmptyState
```typescript
interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
}
```

**Design:**
- Centered in container
- Subtle illustration
- Clear CTA if applicable

### 4.4 Navigation Components

#### TabNavigation
```typescript
interface TabNavigationProps {
  tabs: { id: string; label: string; count?: number }[];
  activeTab: string;
  onChange: (tabId: string) => void;
}
```

**Design:**
- Underline indicator for active
- Smooth slide animation
- Badge for counts
- Scrollable on mobile

#### Pagination
```typescript
interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  variant?: 'numbered' | 'infinite';
}
```

**Design:**
- Numbered: Classic pagination
- Infinite: Scroll-triggered loading
- "Load more" button fallback

### 4.5 Data Display Components

#### UserAvatar
```typescript
interface User {
  name: string;
  avatar?: string;
  username: string;
}

interface UserAvatarProps {
  user: User;
  size?: 'sm' | 'md' | 'lg';
  showPresence?: boolean;
}
```

**Sizes:**
- sm: 32px
- md: 48px
- lg: 64px

#### MetricCard
```typescript
interface MetricCardProps {
  label: string;
  value: number | string;
  change?: { value: number; period: string };
  icon?: ReactNode;
}
```

**Design:**
- Trend indicator (up/down/neutral)
- Sparkline for time series
- Hover for details

---

## 5. Interaction Patterns

### 5.1 Micro-interactions

#### Button States
- **Default:** Base color, subtle shadow
- **Hover:** Darken 10%, elevation increase
- **Active:** Darken 20%, elevation decrease
- **Disabled:** 50% opacity, no cursor
- **Loading:** Spinner replaces text

#### Form Validation
- **Inline:** Validate on blur
- **Success:** Green check icon
- **Error:** Red text below field
- **Warning:** Yellow for suggestions

#### Content Loading
- **Skeleton screens** for initial load
- **Progressive image loading** with blur-up
- **Optimistic updates** for user actions
- **Stale-while-revalidate** for feeds

### 5.2 Animations

#### Page Transitions
- **Duration:** 200-300ms
- **Easing:** ease-in-out
- **Types:** Fade, slide, scale

#### Component Animations
- **Cards:** Scale on hover (1.02)
- **Modals:** Fade + scale in
- **Toasts:** Slide in from edge
- **Dropdowns:** Fade + slight slide

### 5.3 Gestures (Mobile)

- **Swipe right:** Back navigation
- **Swipe left:** Delete/archive
- **Pull to refresh:** Update feed
- **Long press:** Context menu
- **Pinch:** Zoom images

---

## 6. Visual Design System

### 6.1 Color Palette

#### Primary Colors
```css
--primary-500: #2563EB; /* Main brand color */
--primary-600: #1D4ED8; /* Hover states */
--primary-400: #3B82F6; /* Light variant */
```

#### Semantic Colors
```css
--success: #10B981;
--warning: #F59E0B;
--error: #EF4444;
--info: #3B82F6;
```

#### Neutral Colors
```css
--gray-50: #F9FAFB;
--gray-100: #F3F4F6;
--gray-200: #E5E7EB;
--gray-300: #D1D5DB;
--gray-400: #9CA3AF;
--gray-500: #6B7280;
--gray-600: #4B5563;
--gray-700: #374151;
--gray-800: #1F2937;
--gray-900: #111827;
```

### 6.2 Typography

#### Font Stack
```css
--font-sans: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'SF Mono', monospace;
```

#### Type Scale
```css
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
```

#### Font Weights
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 6.3 Spacing System

Base unit: 8px

```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-10: 2.5rem;  /* 40px */
--space-12: 3rem;    /* 48px */
--space-16: 4rem;    /* 64px */
```

### 6.4 Elevation System

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.1);
```

---

## 7. Responsive Design

### 7.1 Breakpoint Strategy

```scss
$mobile: 640px;
$tablet: 768px;
$desktop: 1024px;
$wide: 1440px;
```

### 7.2 Mobile-First Approach

#### Layout Adaptations
- **Mobile (< 640px)**
  - Single column layout
  - Bottom navigation bar
  - Full-width cards
  - Sheet-based modals

- **Tablet (640px - 1024px)**
  - 2-column grid for cards
  - Side-sliding navigation
  - Modal dialogs

- **Desktop (> 1024px)**
  - 3-column layout (sidebar, main, aside)
  - Persistent sidebar
  - Hover states enabled
  - Keyboard shortcuts

### 7.3 Touch Targets

- Minimum size: 44x44px (iOS) / 48x48px (Android)
- Spacing between targets: 8px minimum
- Increased padding on mobile inputs

---

## 8. Accessibility

### 8.1 WCAG 2.2 AA Compliance

#### Color Contrast
- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum
- UI components: 3:1 minimum

#### Keyboard Navigation
- All interactive elements focusable
- Visible focus indicators
- Logical tab order
- Skip links for navigation

#### Screen Reader Support
- Semantic HTML structure
- ARIA labels for icons
- Live regions for dynamic content
- Alternative text for images

### 8.2 Accessibility Features

```typescript
interface AccessibilitySettings {
  reducedMotion: boolean;
  highContrast: boolean;
  fontSize: 'normal' | 'large' | 'extra-large';
  keyboardShortcuts: boolean;
}
```

---

## 9. Performance Considerations

### 9.1 Loading Performance

- **Initial Load:** < 3s on 3G
- **Time to Interactive:** < 5s
- **First Contentful Paint:** < 1.5s
- **Largest Contentful Paint:** < 2.5s

### 9.2 Optimization Techniques

- Lazy loading for images and components
- Virtual scrolling for long lists
- Code splitting by route
- Service Worker for offline caching
- WebP images with fallbacks
- Critical CSS inlining

---

## 10. Error States & Edge Cases

### 10.1 Error Handling

#### Network Errors
```typescript
interface ErrorStateProps {
  type: 'network' | 'server' | 'permission' | 'not-found';
  retry?: () => void;
}
```

**Design:**
- Clear error message
- Actionable recovery steps
- Retry button when applicable
- Contact support link

### 10.2 Edge Cases

- **Empty States:** First-time user experience
- **Offline Mode:** Cached content indicator
- **Long Content:** Truncation with "Read more"
- **Rate Limiting:** Countdown timer display
- **Session Timeout:** Modal with re-auth option

---

## 11. Platform-Specific Considerations

### 11.1 PWA Features

#### App Manifest
```json
{
  "name": "AI Collective Hub",
  "short_name": "AI Hub",
  "theme_color": "#2563EB",
  "background_color": "#ffffff",
  "display": "standalone",
  "orientation": "portrait"
}
```

#### Install Prompt
- Custom install banner
- "Add to Home Screen" instructions
- Post-install onboarding

### 11.2 Browser Compatibility

- Chrome 90+
- Safari 14+
- Firefox 88+
- Edge 90+
- Progressive enhancement for older browsers

---

## 12. Design Handoff Specifications

### 12.1 Design Tokens

```json
{
  "colors": { /* Color values */ },
  "typography": { /* Font values */ },
  "spacing": { /* Spacing values */ },
  "shadows": { /* Shadow values */ },
  "animations": { /* Animation values */ }
}
```

### 12.2 Component Documentation

Each component includes:
- Props interface
- Usage examples
- Do's and don'ts
- Accessibility notes
- Performance considerations

### 12.3 Asset Requirements

- Icons: SVG format, 24x24px base
- Images: WebP with JPEG fallback
- Logos: SVG for scalability
- Fonts: WOFF2 format

---

## 13. Metrics & Success Indicators

### 13.1 UX Metrics

- **Task Success Rate:** > 90%
- **Time on Task:** < 2 minutes for core flows
- **Error Rate:** < 5%
- **System Usability Scale (SUS):** > 80

### 13.2 Engagement Metrics

- **Bounce Rate:** < 30%
- **Session Duration:** > 5 minutes
- **Return Rate:** > 40% weekly
- **Feature Adoption:** > 60% in first week

---

## 14. Future Enhancements

### 14.1 Post-MVP Features

- Dark mode with system preference detection
- Customizable dashboard layouts
- Advanced keyboard shortcuts
- Voice input for content creation
- AR/VR content viewing
- Real-time collaboration cursors

### 14.2 Personalization

- AI-powered content recommendations
- Customizable feed algorithms
- Personal theme preferences
- Saved search filters
- Custom notification preferences

---

## Appendix A: Component Inventory

### Core Components Checklist

- [ ] AppShell
- [ ] Header
- [ ] Footer
- [ ] Sidebar
- [ ] MobileNav
- [ ] FeedCard
- [ ] ArticleViewer
- [ ] RichTextEditor
- [ ] TagSelector
- [ ] UserAvatar
- [ ] ProfileCard
- [ ] SpaceCard
- [ ] LinkCard
- [ ] MetricCard
- [ ] SearchBar
- [ ] FilterBar
- [ ] TabNavigation
- [ ] Pagination
- [ ] Modal
- [ ] Drawer
- [ ] Toast
- [ ] LoadingState
- [ ] EmptyState
- [ ] ErrorBoundary
- [ ] Button (variants)
- [ ] Input (types)
- [ ] Select
- [ ] Checkbox
- [ ] Radio
- [ ] Switch
- [ ] Tooltip
- [ ] Popover
- [ ] Dropdown

---

## Appendix B: Interaction Flow Diagrams

[Note: In implementation, these would be actual flow diagrams created in Figma/Miro]

1. **Onboarding Flow Diagram**
2. **Content Creation Flow Diagram**
3. **Discovery Flow Diagram**
4. **Collaboration Space Flow Diagram**
5. **Admin Dashboard Flow Diagram**

---

## Appendix C: Responsive Grid System

### Grid Configuration
```css
.container {
  --columns: 12;
  --gutter: 24px;
  --margin: 16px (mobile), 24px (tablet), 32px (desktop);
}
```

### Layout Templates
1. **Single Column:** Mobile default
2. **Sidebar Layout:** 3-9 split (desktop)
3. **Three Column:** 3-6-3 split (wide screens)
4. **Card Grid:** Auto-fit with minmax(300px, 1fr)

---

## 15. AI Agent Implementation Guide

### 15.1 Implementation Strategy for AI Agents

This section provides specific instructions for AI agents (like Claude) to build this application with a polished, modern UI.

#### Core Principles for AI Implementation

1. **Always use shadcn/ui components as the foundation**
2. **Never create custom components when shadcn provides one**
3. **Follow the shadcn design system strictly**
4. **Use Tailwind classes for all styling (no custom CSS)**
5. **Implement components in order of dependency**

#### Implementation Order

```
1. Setup & Configuration
   - Initialize Next.js with TypeScript
   - Install shadcn/ui with default theme
   - Configure Tailwind with custom colors

2. Layout Components (Week 1, Day 1)
   - AppShell using shadcn Layout
   - Navigation using shadcn NavigationMenu

3. Authentication Flow (Week 1, Day 2)
   - Login page with shadcn Card
   - OAuth integration

4. Core Features (Week 1, Days 3-5)
   - Feed using shadcn Card + Skeleton
   - Editor using Tiptap + shadcn styles
   - Profiles using shadcn Form components
```

### 15.2 shadcn Component Mapping

#### CRITICAL: Component Usage Map

| Custom Component | shadcn Components to Use | Additional Libraries |
|-----------------|-------------------------|---------------------|
| **AppShell** | Custom wrapper using divs with Tailwind | - |
| **Header** | `<NavigationMenu>`, `<Button>`, `<Avatar>` | - |
| **FeedCard** | `<Card>`, `<CardHeader>`, `<CardContent>`, `<Badge>` | - |
| **RichTextEditor** | `<Card>` wrapper, `<Toolbar>` custom | Tiptap |
| **TagSelector** | `<Command>`, `<Badge>`, `<Popover>` | - |
| **UserAvatar** | `<Avatar>`, `<AvatarFallback>`, `<AvatarImage>` | - |
| **ProfileForm** | `<Form>`, `<Input>`, `<Textarea>`, `<Select>` | react-hook-form, zod |
| **Toast** | `<Toast>`, `<Toaster>` from shadcn | - |
| **Modal** | `<Dialog>`, `<DialogContent>`, `<DialogHeader>` | - |
| **LoadingState** | `<Skeleton>`, `<Spinner>` (custom), `<Progress>` | - |
| **EmptyState** | `<Card>` with custom content | - |
| **TabNavigation** | `<Tabs>`, `<TabsList>`, `<TabsTrigger>` | - |
| **Pagination** | `<Pagination>` components | - |
| **MetricCard** | `<Card>`, `<CardContent>`, custom chart | recharts |
| **SearchBar** | `<Command>` with `<Input>` | - |
| **FilterBar** | `<Select>`, `<Toggle>`, `<ToggleGroup>` | - |
| **Dropdown** | `<DropdownMenu>`, `<DropdownMenuTrigger>` | - |
| **Sidebar** | `<Sheet>` (mobile), `<ScrollArea>` (desktop) | - |

#### Component Implementation Examples

```typescript
// CORRECT: Using shadcn components
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface Article {
  id: string;
  title: string;
  excerpt: string;
  author: {
    name: string;
    avatar?: string;
  };
  tags: string[];
}

export function FeedCard({ article }: { article: Article }) {
  return (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <CardHeader>
        <div className="flex items-center gap-3">
          <Avatar className="h-10 w-10">
            <AvatarImage src={article.author.avatar} />
            <AvatarFallback>{article.author.name[0]}</AvatarFallback>
          </Avatar>
          <div>
            <CardTitle className="text-lg">{article.title}</CardTitle>
            <CardDescription>{article.author.name}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground line-clamp-3">{article.excerpt}</p>
        <div className="flex gap-2 mt-4">
          {article.tags.map(tag => (
            <Badge key={tag} variant="secondary">{tag}</Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

// INCORRECT: Creating custom components
// DO NOT create custom card components from scratch
```

### 15.3 Polished & Modern UI Instructions

#### Visual Polish Requirements

1. **Shadows and Elevation**
   ```typescript
   // Use these exact shadow classes for consistency
   const shadowClasses = {
     card: "shadow-sm hover:shadow-md transition-shadow duration-200",
     modal: "shadow-2xl",
     dropdown: "shadow-lg",
     button: "shadow-sm hover:shadow active:shadow-none"
   }
   ```

2. **Animations and Transitions**
   ```typescript
   // ALWAYS add these transitions to interactive elements
   const transitions = {
     hover: "transition-all duration-200 ease-in-out",
     page: "animate-in fade-in-0 duration-300",
     modal: "animate-in fade-in-0 zoom-in-95 duration-200",
     slideIn: "animate-in slide-in-from-bottom duration-300"
   }
   ```

3. **Spacing and Layout**
   ```typescript
   // Consistent spacing patterns
   const spacing = {
     page: "container mx-auto px-4 sm:px-6 lg:px-8 py-8",
     section: "space-y-6",
     card: "p-6",
     compact: "p-4",
     stack: "space-y-4",
     inline: "space-x-3"
   }
   ```

4. **Typography Hierarchy**
   ```typescript
   // Use these exact combinations for text
   const typography = {
     h1: "text-4xl font-bold tracking-tight",
     h2: "text-2xl font-semibold tracking-tight",
     h3: "text-xl font-semibold",
     body: "text-base text-muted-foreground",
     small: "text-sm text-muted-foreground",
     label: "text-sm font-medium"
   }
   ```

5. **Color Usage**
   ```typescript
   // Modern color patterns
   const colorPatterns = {
     primary: "bg-primary text-primary-foreground",
     secondary: "bg-secondary text-secondary-foreground",
     muted: "bg-muted text-muted-foreground",
     card: "bg-card text-card-foreground",
     destructive: "bg-destructive text-destructive-foreground"
   }
   ```

#### Critical Polish Details

1. **ALWAYS use these modern UI patterns:**
   - Rounded corners: `rounded-lg` for cards, `rounded-md` for buttons
   - Subtle borders: `border` not `border-2`
   - Muted colors for secondary text: `text-muted-foreground`
   - Hover states on ALL interactive elements
   - Focus rings: `focus-visible:ring-2 focus-visible:ring-primary`

2. **NEVER do these (they look outdated):**
   - Sharp corners (no border-radius)
   - Heavy shadows or borders
   - Pure black text (#000000)
   - Instant state changes (no transitions)
   - Default browser styles

3. **Modern Layout Patterns:**
   ```typescript
   // Bento grid for dashboards
   <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

   // Sticky header with blur
   <header className="sticky top-0 z-50 backdrop-blur-lg bg-background/80 border-b">

   // Floating action button
   <Button className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg">
   ```

4. **Loading States (CRITICAL for polish):**
   ```typescript
   // ALWAYS implement skeleton loading
   import { Skeleton } from "@/components/ui/skeleton"

   function FeedCardSkeleton() {
     return (
       <Card>
         <CardHeader>
           <Skeleton className="h-12 w-12 rounded-full" />
           <Skeleton className="h-4 w-3/4" />
         </CardHeader>
         <CardContent>
           <Skeleton className="h-20 w-full" />
         </CardContent>
       </Card>
     )
   }
   ```

5. **Empty States (Required for professional look):**
   ```typescript
   function EmptyFeed() {
     return (
       <Card className="flex flex-col items-center justify-center p-12 text-center">
         <Icons.inbox className="h-12 w-12 text-muted-foreground mb-4" />
         <h3 className="text-lg font-semibold">No articles yet</h3>
         <p className="text-sm text-muted-foreground mt-2">
           Be the first to share knowledge with the community
         </p>
         <Button className="mt-6">Create Article</Button>
       </Card>
     )
   }
   ```

### 15.4 File Structure for AI Implementation

```
src/
├── app/
│   ├── layout.tsx                 // Root layout with providers
│   ├── page.tsx                   // Landing page
│   ├── (auth)/
│   │   └── login/page.tsx        // GitHub OAuth login
│   ├── (authenticated)/
│   │   ├── layout.tsx            // Auth guard wrapper
│   │   ├── feed/
│   │   │   ├── page.tsx          // Feed page
│   │   │   └── loading.tsx       // Loading skeleton
│   │   ├── articles/
│   │   │   ├── [id]/page.tsx    // Article view
│   │   │   └── new/page.tsx      // Article creation
│   │   ├── spaces/
│   │   │   ├── page.tsx          // Spaces list
│   │   │   └── [id]/page.tsx     // Space detail
│   │   └── profile/
│   │       └── [username]/page.tsx // User profile
├── components/
│   ├── ui/                       // shadcn components (DO NOT MODIFY)
│   ├── layout/
│   │   ├── app-shell.tsx
│   │   ├── header.tsx
│   │   └── mobile-nav.tsx
│   ├── feed/
│   │   ├── feed-card.tsx
│   │   └── feed-filters.tsx
│   ├── editor/
│   │   └── rich-text-editor.tsx
│   └── shared/
│       ├── user-avatar.tsx
│       └── empty-state.tsx
└── lib/
    ├── utils.ts                  // cn() utility from shadcn
    └── constants.ts              // Design tokens
```

### 15.5 Implementation Checklist for AI Agents

When implementing each component, verify:

- [ ] Uses shadcn component as base
- [ ] Has proper TypeScript types
- [ ] Includes loading state
- [ ] Includes error state
- [ ] Includes empty state
- [ ] Has hover effects on interactive elements
- [ ] Uses proper spacing (8px grid)
- [ ] Follows color scheme (no custom colors)
- [ ] Has smooth transitions (200ms)
- [ ] Is keyboard accessible
- [ ] Has proper ARIA labels
- [ ] Uses semantic HTML
- [ ] Is responsive (mobile-first)
- [ ] Has proper focus states

### 15.6 Common Implementation Patterns

```typescript
// Pattern 1: Page with loading state
export default async function FeedPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Feed</h1>
        <Button>
          <Icons.plus className="mr-2 h-4 w-4" />
          New Article
        </Button>
      </div>
      <Suspense fallback={<FeedSkeleton />}>
        <FeedContent />
      </Suspense>
    </div>
  )
}

// Pattern 2: Form with validation
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const formSchema = z.object({
  title: z.string().min(1, "Title is required").max(200, "Title too long"),
  content: z.string().min(10, "Content must be at least 10 characters"),
  tags: z.array(z.string()).min(1, "Select at least one tag").max(5, "Maximum 5 tags")
})

export function ArticleForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema)
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Title</FormLabel>
              <FormControl>
                <Input placeholder="Enter article title" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  )
}

// Pattern 3: Data fetching with error handling
export async function FeedContent() {
  try {
    const articles = await fetchArticles()

    if (!articles || articles.length === 0) {
      return <EmptyFeed />
    }

    return (
      <div className="grid gap-6">
        {articles.map((article: Article) => (
          <FeedCard key={article.id} article={article} />
        ))}
      </div>
    )
  } catch (error) {
    return <ErrorState retry={() => window.location.reload()} />
  }
}
```

### 15.7 Performance & Optimization Rules

1. **Use dynamic imports for heavy components:**
   ```typescript
   const RichTextEditor = dynamic(() => import('@/components/editor/rich-text-editor'), {
     loading: () => <Skeleton className="h-[400px]" />,
     ssr: false
   })
   ```

2. **Implement virtual scrolling for long lists:**
   ```typescript
   import { useVirtualizer } from '@tanstack/react-virtual'
   ```

3. **Use React.memo for expensive components:**
   ```typescript
   export const FeedCard = React.memo(({ article }) => {
     // Component implementation
   })
   ```

4. **Optimize images:**
   ```typescript
   import Image from 'next/image'

   <Image
     src={article.image}
     alt={article.title}
     width={800}
     height={400}
     className="rounded-lg"
     loading="lazy"
     placeholder="blur"
   />
   ```

### 15.8 Testing Implementation

Each component should have:

```typescript
// components/feed/__tests__/feed-card.test.tsx
import { render, screen } from '@testing-library/react'
import { FeedCard } from '../feed-card'

describe('FeedCard', () => {
  it('renders article title', () => {
    const article = { title: 'Test Article', ... }
    render(<FeedCard article={article} />)
    expect(screen.getByText('Test Article')).toBeInTheDocument()
  })

  it('shows loading skeleton', () => {
    render(<FeedCardSkeleton />)
    expect(screen.getByTestId('skeleton')).toBeInTheDocument()
  })
})
```

---

## 16. CRITICAL ARCHITECTURE CLARIFICATION

### 16.1 Separated Frontend/Backend Architecture

**⚠️ CRITICAL: This application uses a SEPARATED architecture, NOT a monolithic Next.js app:**

```
┌─────────────────┐         ┌─────────────────┐
│   Next.js App   │  HTTP   │  FastAPI Backend│
│   (Port 3000)   │◄──────►│   (Port 8000)   │
│                 │  JSON   │                 │
│  - UI Rendering │         │  - Business     │
│  - Client State │         │    Logic        │
│  - Auth UI      │         │  - Database     │
│                 │         │  - Auth Logic   │
└─────────────────┘         └─────────────────┘
```

### 16.2 API Client Setup

**lib/api-client.ts** - Central API client for all FastAPI calls:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  async request(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
        ...(this.token && { Authorization: `Bearer ${this.token}` })
      }
    };

    const response = await fetch(url, config);

    if (response.status === 401) {
      // Handle token expiration
      this.token = null;
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
      }
    }

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  get(endpoint: string) {
    return this.request(endpoint, { method: 'GET' });
  }

  post(endpoint: string, body: any) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body)
    });
  }

  patch(endpoint: string, body: any) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(body)
    });
  }

  delete(endpoint: string) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
```

### 16.3 Authentication Flow (GitHub OAuth with FastAPI)

**⚠️ CRITICAL FIX: GitHub OAuth cannot redirect directly to backend!**

```typescript
// app/login/page.tsx
'use client';

export default function LoginPage() {
  const handleGitHubLogin = () => {
    // GitHub OAuth must redirect back to frontend, not backend!
    const clientId = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID;
    const redirectUri = encodeURIComponent('http://localhost:3000/auth/callback');
    const scope = encodeURIComponent('read:user user:email');

    window.location.href = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`;
  };

  return (
    <Button onClick={handleGitHubLogin}>
      Sign in with GitHub
    </Button>
  );
}

// app/auth/callback/page.tsx
'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { apiClient } from '@/lib/api-client';

export default function CallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const code = searchParams.get('code');

    if (code) {
      // Exchange code with FastAPI backend
      apiClient.post('/api/auth/github/callback', { code })
        .then((response) => {
          apiClient.setToken(response.access_token);
          router.push('/feed');
        })
        .catch(() => {
          router.push('/login?error=auth_failed');
        });
    }
  }, []);

  return <div>Authenticating...</div>;
}

// lib/auth-context.tsx - REQUIRED for auth state management
'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';

interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('auth_token');
    if (token) {
      apiClient.setToken(token);
      apiClient.get('/api/users/me')
        .then(setUser)
        .catch(() => localStorage.removeItem('auth_token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (token: string) => {
    apiClient.setToken(token);
    localStorage.setItem('auth_token', token);
    const user = await apiClient.get('/api/users/me');
    setUser(user);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    apiClient.setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

### 16.4 Data Fetching Pattern (MVP - Simple Client Components)

**For MVP: Use Client Components with simple fetch patterns:**

```typescript
// ✅ MVP APPROACH - Simple and works
'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';

export default function FeedPage() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get('/api/articles')
      .then(data => setArticles(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <FeedSkeleton />;
  return <Feed articles={articles} />;
}
```

**Note for MVP:**
- No SEO needed = Client Components are fine
- No real-time updates needed = Simple fetch is enough
- No complex caching = useState/useEffect works

### 16.5 Form Submission Pattern

```typescript
// ✅ CORRECT - Submit to FastAPI backend
async function handleSubmit(data: FormData) {
  try {
    const response = await apiClient.post('/api/articles', {
      title: data.title,
      content: data.content,
      tags: data.tags
    });

    // Handle success
    router.push(`/articles/${response.id}`);
  } catch (error) {
    // Handle error
    toast({ title: 'Error', variant: 'destructive' });
  }
}
```

### 16.6 FastAPI CORS Configuration

**backend/app/main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 16.7 Docker Compose Setup

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/aihub
      - GITHUB_CLIENT_ID=${GITHUB_CLIENT_ID}
      - GITHUB_CLIENT_SECRET=${GITHUB_CLIENT_SECRET}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=aihub
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 16.8 MVP Simplifications

**What we're NOT building for MVP:**
- ❌ Server-side rendering (SEO not needed)
- ❌ WebSockets (no real-time features)
- ❌ Direct messaging (future feature)
- ❌ Complex caching strategies
- ❌ Optimistic UI updates
- ❌ Offline support (Service Workers)
- ❌ Push notifications
- ❌ Advanced gestures (swipe, pull-to-refresh)

**What we ARE building:**
- ✅ Simple Client Components with useEffect
- ✅ Basic JWT authentication
- ✅ Standard REST API calls
- ✅ Local storage for token
- ✅ Basic loading/error states
- ✅ Simple form submissions

### 16.9 Common Mistakes to Avoid

1. ❌ **Putting API routes in Next.js** - All API logic must be in FastAPI
2. ❌ **Direct database access from Next.js** - Only FastAPI should access the database
3. ❌ **Forgetting CORS configuration** - FastAPI must allow requests from localhost:3000
4. ❌ **Over-engineering for MVP** - Keep it simple, no complex patterns

---

## CRITICAL REMINDERS FOR AI AGENTS (MVP)

1. **KEEP IT SIMPLE** - This is an MVP, not production
2. **ARCHITECTURE: Next.js (3000) + FastAPI (8000)** - Separated frontend/backend
3. **CLIENT COMPONENTS ONLY** - No SSR needed for MVP
4. **SIMPLE FETCH PATTERNS** - useState + useEffect is fine
5. **ALWAYS USE SHADCN** - Never build components from scratch
6. **BASIC JWT AUTH** - Token in localStorage
7. **CONFIGURE CORS** - FastAPI must accept Next.js requests
8. **NO WEBSOCKETS** - No real-time features in MVP

When in doubt: Choose the simplest solution that works. Ship fast.