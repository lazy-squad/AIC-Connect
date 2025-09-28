# Product Requirements Document: AI Collective Hub MVP

**Author:** AI Collective Team
**Version:** 1.1
**Date:** September 28, 2025
**Status:** Approved MVP scope • **Deploy target:** Single VM behind AWS ALB (HTTP first, HTTPS/ACM last) • **Audience:** Engineering, Product, Design, DevOps

---

## 1. Overview

### 1.1. Problem Statement

The AI Collective is a global, grassroots community of over 70,000 AI "pioneers"—founders, researchers, and investors—dedicated to steering AI's future towards trust and human flourishing. Currently, the invaluable insights generated in local chapter events and discussions are ephemeral. The community lacks a central, trusted digital hub to preserve knowledge, facilitate cross-chapter discovery of experts and content, and coordinate collaborative projects. This fragmentation hinders the Collective's mission to unite groups and bridge communication gaps on a global scale.

### 1.2. Product Vision & MVP Goal

**Vision:** To create the definitive digital hub for the AI Collective, a platform that transforms a decentralized network of chapters into a cohesive global force for innovation and collaboration.

**MVP Goal:** For this hackathon, our goal is to build a Minimum Viable Product (MVP) that demonstrates the core value proposition of a unified, high-trust platform. The MVP will focus on establishing a seamless user journey from onboarding to content creation, discovery, and the initiation of collaborative work, validating the concept of a central hub built on strategic integration rather than monolithic development.

### 1.3. Target Audience

The primary users are the members of the AI Collective: AI founders, researchers, operators, and investors. This is a technically proficient audience that values efficiency, high signal-to-noise ratio, and verifiable expertise. They are active on professional platforms like GitHub and are likely to engage in deep, nuanced discussions.

### 1.4. Guiding Principles

- **Integrate, Don't Replicate:** Leverage best-in-class external tools for their core competencies (e.g., real-time chat, project management) and focus the Hub's value on aggregation and context.
- **Velocity and Viability:** Prioritize features that can be implemented to a high standard within the hackathon's timeframe and which deliver immediate, tangible value to the user.
- **Foundation for the Future:** Make architectural choices (e.g., API-first identity, headless CMS) that enable future scalability and prevent technical debt.

---

## 2. MVP Feature Requirements

### 2.1. User Onboarding & Identity

**User Story:** As a new member of the AI Collective, I want to sign up instantly using my existing professional identity so I can join the community with minimal friction and have a profile that reflects my expertise.

| Requirement ID | Description                                                                                                                                                                                                                                                                                         | Priority    |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| ONB-01         | **GitHub Authentication:** The platform must use GitHub OAuth as the sole method for user registration and login. This establishes a high-trust, verified identity from the outset.                                                                                                                 | Must-Have   |
| ONB-02         | **Profile Seeding:** Upon first authentication, the system must automatically fetch and populate the user's profile with publicly available data from the GitHub API (GET /user endpoint): Name, GitHub Username, Avatar, Company, Location.                                                        | Must-Have   |
| ONB-03         | **Profile Enhancement:** After initial GitHub auth, users must be prompted to complete their platform-specific profile with: Professional Bio (rich text), AI Expertise Areas (from controlled taxonomy), Current Focus, Looking For (collaborators/advisors/funding), Publications/Projects links. | Must-Have   |
| ONB-04         | **Local User Record:** A corresponding user record must be created and persisted in the platform's local database, storing both GitHub data and platform-specific profile data.                                                                                                                     | Must-Have   |
| ONB-05         | **Profile Visibility Controls:** Users can set their profile visibility (public/community/hidden) and control who can contact them.                                                                                                                                                                 | Should-Have |

### 2.2. Content Creation

**User Story:** As an expert in my field, I want a clean, powerful, and intuitive editor to write and format long-form articles, share my research, and contribute high-quality knowledge to the community.

| Requirement ID | Description                                                                                                                                                                                                                                                     | Priority     |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| CON-01         | **Rich-Text Editor:** The platform must provide a modern, WYSIWYG rich-text editor for all content creation. The recommended implementation is Tiptap, a headless editor framework that offers maximum flexibility and a strong foundation for future features. | Must-Have    |
| CON-02         | **Core Formatting Tools:** The editor must support essential formatting options, including: Headings (H1-H3), Bold, Italic, Unordered (bullet) lists, Ordered (numbered) lists, Blockquotes, Code blocks, and Hyperlinks.                                       | Must-Have    |
| CON-03         | **Structured Content Storage:** The editor's output must be saved to the database in a structured JSON format, not raw HTML. This is critical for data integrity, future search indexing, and content portability.                                              | Must-Have    |
| CON-04         | **Media Support:** Support for image uploads with object storage (S3) and automatic generation of pre-signed URLs.                                                                                                                                              | Should-Have  |
| CON-05         | **Link Previews:** Automatic Open Graph metadata fetching for embedded links.                                                                                                                                                                                   | Nice-to-Have |

### 2.3. Content & User Discovery

**User Story:** As a member, I want to easily find content relevant to my specific interests (like Large Language Models) and discover other experts within the community to follow and learn from.

| Requirement ID | Description                                                                                                                                                                                                                                                   | Priority    |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| DIS-01         | **Tag-Based System:** All content must be classifiable with tags. A tag-based system is flexible and user-intuitive for filtering.                                                                                                                            | Must-Have   |
| DIS-02         | **Controlled Taxonomy:** For the MVP, the system will use a predefined, centrally managed list of AI-specific tags (e.g., "LLM Agents", "Computer Vision", "AI Safety", "Data Engineering"). This prevents tag duplication and ensures filtering reliability. | Must-Have   |
| DIS-03         | **Content Filtering:** The main content feed must be filterable by one or more tags, allowing users to narrow down the content to their specific interests.                                                                                                   | Must-Have   |
| DIS-04         | **Feed Types:** Two feed views: Global Feed (all public content, chronological) and Personalized Feed (filtered by user's selected expertise areas).                                                                                                          | Must-Have   |
| DIS-05         | **User Directory:** A searchable member directory allowing discovery by name, expertise areas, location, or current focus.                                                                                                                                    | Must-Have   |
| DIS-06         | **Public User Profiles:** Clicking on a user's name anywhere leads to their profile page, displaying both GitHub-sourced and platform-specific information.                                                                                                   | Must-Have   |
| DIS-07         | **Chapter Discovery:** Suggestions for local AI Collective chapters based on user location (city-level) and interest overlap.                                                                                                                                 | Should-Have |

### 2.4. Collaboration Spaces

**User Story:** As a project lead, I want to create a dedicated space for my initiative where I can aggregate all relevant resources—like our Slack channel, GitHub repo, and Notion docs—into a single, shareable dashboard for my team.

| Requirement ID | Description                                                                                                                                                                                                                                                                                                                                                                                                                                        | Priority    |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| COL-01         | **Space Creation:** Users must be able to create a "Collaboration Space" with a unique title, description, and tags.                                                                                                                                                                                                                                                                                                                               | Must-Have   |
| COL-02         | **Deep Link Aggregation:** Within a Space, users must be able to add, edit, and delete links to external resources. The system must support deep links that point to specific content within other applications.                                                                                                                                                                                                                                   | Must-Have   |
| COL-03         | **Supported Link Types:** The MVP will demonstrate support for deep links from key collaboration tools:<br>• **Slack:** Links to specific channels or DMs (e.g., `slack://channel?team={TEAM_ID}&id={CHANNEL_ID}`)<br>• **GitHub:** Permanent links to specific files, lines of code, or commits using the commit SHA<br>• **Notion:** Links to specific pages or content blocks<br>• **Generic:** Any HTTPS URL with automatic Open Graph preview | Must-Have   |
| COL-04         | **Link Metadata:** Each added link must store the URL, user-provided title, description, and auto-fetched preview data where available.                                                                                                                                                                                                                                                                                                            | Must-Have   |
| COL-05         | **Space Members:** Ability to add other users as members of a collaboration space.                                                                                                                                                                                                                                                                                                                                                                 | Should-Have |

### 2.5. Progressive Web App (PWA)

**User Story:** As a mobile user, I want to install the Hub on my device and access content even when connectivity is poor.

| Requirement ID | Description                                                                                               | Priority    |
| -------------- | --------------------------------------------------------------------------------------------------------- | ----------- |
| PWA-01         | **Installability:** The application must be installable as a PWA with proper manifest.json configuration. | Must-Have   |
| PWA-02         | **Offline Support:** Cache recent feed content for offline reading using Service Workers.                 | Should-Have |
| PWA-03         | **Responsive Design:** Fully responsive UI that works seamlessly on mobile, tablet, and desktop.          | Must-Have   |

### 2.6. Admin Dashboard (Lite)

**User Story:** As a community organizer, I want to see engagement metrics and export data for outreach.

| Requirement ID | Description                                                                                                                     | Priority     |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| ADM-01         | **Engagement Metrics:** View platform-wide metrics: active users (7/30d), new signups, posts/day, collaboration spaces created. | Should-Have  |
| ADM-02         | **Content Insights:** Top tags, trending articles, most active collaboration spaces.                                            | Should-Have  |
| ADM-03         | **Chapter Health:** For chapter organizers: member count, activity trends, top contributors.                                    | Nice-to-Have |
| ADM-04         | **CSV Export:** Export aggregate metrics and user lists (where consented) for outreach.                                         | Should-Have  |

---

## 3. Non-Goals for MVP

To ensure focus and deliver a polished core product within the hackathon timeline, the following features are explicitly out of scope for the MVP:

- **Algorithmic Feeds:** No complex ML-based "For You" recommendations. Feeds are chronological with tag filtering.
- **Reputation System:** No karma, points, or credibility scores.
- **Direct Messaging:** No private 1-to-1 or group messaging within the platform.
- **Real-time Collaboration:** The Tiptap editor will be single-user only. No collaborative editing.
- **Email Notifications:** No email notification system beyond authentication magic links.
- **Native Collaboration Tools:** No built-in Kanban boards, chat, or document storage.
- **Advanced Moderation:** No AI-powered content moderation or complex review workflows.
- **Payment Integration:** No paid tiers, sponsorships, or financial transactions.
- **Mobile Apps:** Web-first PWA only, no native iOS/Android apps.

---

## 4. Success Metrics

The success of the MVP will be measured by its ability to achieve the following within the hackathon context:

**Primary Metric:** A successful end-to-end demonstration of the core user flow:

1. User onboards via GitHub OAuth
2. User enhances profile with AI-specific information
3. User creates a formatted article using the rich-text editor and applies tags
4. User creates a Collaboration Space and adds deep links to external resources
5. Another user discovers the content and author's profile via tag filtering and search
6. Users can install the PWA and access content offline

**Secondary Metrics:**

- **Time to First Post:** < 5 minutes from signup
- **Profile Completion Rate:** > 60% add bio and expertise areas
- **Content Discovery:** Users find relevant content within 3 clicks
- **Architectural Soundness:** Clean separation of concerns, scalable data model
- **Accessibility Score:** WCAG 2.2 AA compliance on core flows

---

## 5. Information Architecture

### Core Entities

- **User:** GitHub ID, name, avatar, company, location, bio, expertise_areas, current_focus, looking_for, profile_visibility
- **InterestTag:** Controlled taxonomy of AI-related topics
- **Article:** author_id, title, content_json, tags, created_at, updated_at, view_count
- **CollaborationSpace:** owner_id, title, description, tags, member_ids, created_at
- **ExternalLink:** space_id, url, title, description, link_type, og_preview_data
- **Chapter:** name, slug, city, lat, lon, activity_score
- **Membership:** user_id, chapter_id, role, joined_at
- **AuditLog:** actor_id, action, target_type, target_id, timestamp, ip_address

### Key Relationships

- User ↔ Article (one-to-many, author)
- User ↔ InterestTag (many-to-many, expertise)
- Article ↔ InterestTag (many-to-many, categorization)
- User ↔ CollaborationSpace (one-to-many as owner, many-to-many as member)
- CollaborationSpace ↔ ExternalLink (one-to-many)
- User ↔ Chapter ↔ Membership (many-to-many with role)

---

## 6. System Architecture

### Technology Stack

- **Frontend:**

  - Next.js 14+ (App Router) with TypeScript
  - shadcn/ui components (Radix UI + Tailwind CSS)
  - Tiptap editor for rich text
  - SWR or React Query for data fetching
  - Service Workers for PWA/offline support

- **Backend:**

  - Python with FastAPI
  - Pydantic for automatic data validation and serialization
  - WebSocket support for real-time features (future)
  - Async/await for high performance

- **Database & Storage:**

  - PostgreSQL 16 (primary database)
  - Redis (session cache, rate limiting)
  - S3-compatible object storage (images, attachments)

- **Infrastructure:**
  - Docker Compose for local development and deployment
  - Single VM deployment initially
  - AWS ALB for load balancing and SSL termination
  - GitHub Actions for CI/CD

### API Design

RESTful API with JSON payloads:

- `GET/POST /api/auth/github/*` - GitHub OAuth flow
- `GET/PATCH /api/users/{id}` - User profiles
- `GET/POST /api/articles` - Article CRUD
- `GET /api/articles?tags=tag1,tag2` - Filtered content
- `GET/POST /api/spaces` - Collaboration spaces
- `POST /api/spaces/{id}/links` - Add external links
- `GET /api/feed/global` - Global content feed
- `GET /api/feed/personalized` - User's filtered feed

---

## 7. Security & Privacy

### Baseline (MVP)

- **Authentication:** GitHub OAuth 2.0 exclusive
- **Authorization:** Simple RBAC (member, chapter_admin, global_admin)
- **Data Protection:**
  - OWASP ASVS L1 controls
  - Input validation with Pydantic models
  - SQL injection prevention via SQLAlchemy ORM/parameterized queries
  - XSS protection via React's default escaping
- **Security Headers:**
  - CSP (Content Security Policy)
  - HSTS (after HTTPS enabled)
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff
- **Rate Limiting:** API rate limits per user (Redis-based)
- **Privacy:**
  - City-level location only (no exact coordinates shown)
  - Profile visibility controls
  - GDPR-compliant data export/deletion

### Post-MVP Enhancements

- Connection pooling (PgBouncer)
- Read replicas for scale
- E2E encryption for future DMs
- Advanced threat detection
- SOC2 compliance roadmap

---

## 8. Deployment & Operations

### Environments

- **Local:** Docker Compose with hot reload
- **Staging:** Optional, same stack as production
- **Production:** Single VM initially, with growth path to Kubernetes

### Infrastructure Setup

```
Internet → AWS ALB (HTTP:80 initially)
         ↓
    VM (Docker Compose)
    - Next.js App (port 3000)
    - FastAPI Server (port 8000)
    - PostgreSQL (port 5432)
    - Redis (port 6379)
```

### Deployment Process

1. GitHub Actions triggered on main branch push
2. Build Docker images
3. Push to registry
4. SSH to VM and pull new images
5. Docker Compose up with zero-downtime deployment
6. Run migrations if needed
7. Health check verification

### Monitoring & Backups

- Application logs to CloudWatch/Datadog
- Daily PostgreSQL backups to S3
- Uptime monitoring via Pingdom/UptimeRobot
- Error tracking with Sentry

---

## 9. Testing Strategy

### Test Coverage Goals

- Unit tests: 70% coverage on business logic
- Integration tests: Critical user flows
- E2E tests: Happy path for core features

### Test Types

- **Unit:** Pytest for Python backend, Jest for frontend TypeScript
- **Integration:** API endpoint testing with pytest + httpx TestClient
- **E2E:** Playwright for critical user journeys
- **Accessibility:** axe-core automated testing + manual screen reader testing
- **Performance:** Lighthouse CI for performance budgets

---

## 10. Roadmap

### MVP (Hackathon - 48 hours)

- ✓ GitHub OAuth authentication
- ✓ Profile creation and enhancement
- ✓ Tiptap article editor
- ✓ Tag-based content discovery
- ✓ Collaboration spaces with deep links
- ✓ Basic PWA setup
- ✓ Docker Compose deployment

### M2 (Week 1-2 Post-Hackathon)

- HTTPS with ACM certificate
- Admin dashboard with metrics
- Enhanced search (PostgreSQL full-text)
- Email notifications
- Performance optimizations
- Bug fixes from user feedback

### M3 (Month 1-2)

- Real-time collaboration features
- Advanced moderation tools
- API for third-party integrations
- Chapter event management
- Mobile app considerations
- Scale to multiple VMs/Kubernetes

### M4 (Month 3+)

- ML-powered content recommendations
- Video content support
- Advanced analytics
- Sponsor marketplace
- Global expansion features

---

## 11. Acceptance Criteria

The MVP is considered complete when:

1. **Authentication Flow:** Users can sign up and sign in via GitHub OAuth
2. **Profile Completion:** Users can enhance their profile with AI-specific information
3. **Content Creation:** Users can create rich-text articles with formatting and tags
4. **Content Discovery:** Users can browse global feed and filter by tags
5. **User Discovery:** Users can search for and view other member profiles
6. **Collaboration Spaces:** Users can create spaces and aggregate external links
7. **PWA Features:** App is installable and shows cached content offline
8. **Responsive Design:** UI works on mobile, tablet, and desktop
9. **Performance:** Page loads < 3s on 3G connection
10. **Accessibility:** Keyboard navigable with screen reader support

---

## 12. Risks & Mitigations

| Risk                     | Impact | Probability | Mitigation                                    |
| ------------------------ | ------ | ----------- | --------------------------------------------- |
| GitHub API rate limits   | High   | Medium      | Implement caching, request higher limits      |
| Tiptap editor complexity | Medium | Low         | Start with basic features, extensive testing  |
| Deep link validation     | Low    | Medium      | Strict URL parsing, graceful fallbacks        |
| Single VM scalability    | High   | High        | Clear architecture for horizontal scaling     |
| Data privacy concerns    | High   | Low         | Clear privacy policy, minimal data collection |
| Low initial adoption     | High   | Medium      | Seed content, onboard key influencers         |

---

## 13. Glossary

- **AI Collective:** Global community of AI pioneers
- **Chapter:** Local geographic group within the AI Collective
- **Collaboration Space:** Project dashboard aggregating external resources
- **Deep Link:** URL pointing to specific content within an external application
- **Interest Tag:** Controlled vocabulary term for categorizing content and expertise
- **PWA:** Progressive Web App, installable web application with offline support

---

## 14. References

1. World's Largest AI Community - https://www.aicollective.com/
2. GitHub OAuth Documentation - https://docs.github.com/en/rest/authentication
3. Tiptap Editor Framework - https://github.com/ueberdosis/tiptap
4. shadcn/ui Components - https://ui.shadcn.com/
5. Next.js App Router - https://nextjs.org/docs/app
6. PostgreSQL Full-Text Search - https://www.postgresql.org/docs/current/textsearch.html
7. AWS Application Load Balancer - https://docs.aws.amazon.com/elasticloadbalancing/
8. WCAG 2.2 Guidelines - https://www.w3.org/WAI/WCAG22/quickref/
