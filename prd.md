# AIC HUB — Product Requirements Document (PRD)

> **Status:** Approved MVP scope • **Deploy target:** Single VM behind AWS ALB (HTTP first, HTTPS/ACM last) • **Audience:** Engineering, Product, Design, DevOps • **Doc type:** Planning (no code)

---

## 0) Vision

AIC HUB is a web‑first, installable community app (PWA) for the AI Collective ecosystem. It enables members to join, discover chapters via interests and location, view a global and local feed, and message one another in real time. Organizers get a lightweight dashboard for chapter health. The MVP is open‑source, packaged for Docker Compose, and deployable to a single VM fronted by an AWS Application Load Balancer (ALB). HTTPS via ACM is attached post‑MVP.

**North‑star outcomes**

* A single place where members connect with people, chapters, and events.
* An opinionated, privacy‑respecting social layer that’s easy to adopt.
* An organizer view that surfaces health signals without heavy ops.

---

## 1) Objectives & Non‑Goals

**Objectives (MVP)**

1. Frictionless join via magic link; set interests and location.
2. Chapter suggestions ranked by distance and interest overlap.
3. Global and Local feeds with simple posting (text, image, link preview).
4. In‑app 1:1 DMs with opt‑in and basic safety (block, visibility controls).
5. Admin Dashboard (lite) with chapter health and CSV export.
6. Lean architecture ready for future scale (partitioning, pooling, replicas).

**Non‑Goals (MVP)**

* Native mobile apps, advanced moderation/E2EE, sponsor integrations, ALB access logs, SSO, or complex workflows (judge routing, check‑in).

---

## 2) Stakeholders & Roles

* **Member**: join, set profile, discover chapters, post/read feeds, DM.
* **Chapter Admin**: moderate posts/reports for their chapter; view chapter metrics.
* **Global Admin**: org‑wide metrics; manage chapters; export CSV.
* **Engineering**: build web, API, real‑time, and data layers.
* **DevOps**: VM provisioning, ALB configuration, TLS rollout, backups.
* **Design**: shadcn/ui + Radix implementation, responsive “luxury” style, accessibility.

---

## 3) Assumptions & Constraints

* **Infrastructure**: Single VM, Docker Compose, fronted by **AWS ALB**. Start with **HTTP:80**, enable **HTTPS:443 + ACM** after MVP.
* **WebSockets**: ALB supports WS; keep idle timeout default; app sends periodic pings.
* **Data scope**: user‑provided data (email, name, avatar, interests, city/lat/lon, optional LinkedIn); chapter membership and posting activity. No geo residency limits.
* **Privacy posture**: city‑level visibility by default; lat/lon not exposed to other users.
* **Branding**: neutral OSS branding as **AIC HUB**.

---

## 4) Personas & Top Tasks

**P1—New Member**: create account, set interests/location, join chapter, read local feed, DM a peer.
**P2—Returning Member**: browse global feed, post an update, reply/like, discover a nearby chapter.
**P3—Chapter Admin**: view activity trends, resolve a report, remove an off‑topic post, download CSV for outreach.
**P4—Global Admin**: check org‑wide engagement, identify rising cities/interests, plan programming.

**Definition of success**

* Time‑to‑first‑post < 5 minutes.
* 60% of new members accept at least one chapter suggestion.
* Message delivery appears real‑time (< 1s perceived) on local stack.
* Admins can answer “Is my chapter healthy this month?” at a glance.

---

## 5) Functional Requirements

### 5.1 Authentication & Profile

* Passwordless email sign‑in (magic link).
* Profile fields: display name, avatar, optional LinkedIn URL, interests (tags), city/lat/lon, visibility (public/community/hidden), DM opt‑in.
* Controls: show/hide profile to others; allow DMs; block specific users.

### 5.2 Chapter Suggestions

* Inputs: user city/lat/lon, selected interests, basic chapter activity score.
* Ranking: distance (Haversine) + shared‑interest score + recent chapter activity.
* UX: suggestions list with “Join” and “Save for later”; show rationale (e.g., “2 shared interests · 5 km”).

### 5.3 Feeds & Posts

* **Global feed**: public posts across the network (rate‑limited; paginated).
* **Local feed**: posts from joined and nearby chapters.
* Post types: text, image (uploaded to object storage), link preview (Open Graph).
* Interactions: like; simple replies (optional toggle); report (sends to AuditLog).
* Offline behavior: shell available; last N posts cached for read‑only.

### 5.4 Direct Messages (DMs)

* 1:1 in‑app messaging over WebSockets; online presence (basic).
* Safety: opt‑in DMs, block user, hide profile.
* Delivery semantics: best‑effort fan‑out; client shows send/seen states; reconnect and re‑fetch window on resume.

### 5.5 Admin Dashboard (Lite)

* Chapter Health: actives (7/30d), new joins, posts/day, DM starts.
* Growth: top cities, interest heatmap, chapter comparisons.
* Data handling: non‑PII by default; no per‑user drill‑down in MVP.
* Export: CSV of aggregate metrics and chapter rosters (where consented).

### 5.6 Accessibility & Internationalization

* Target **WCAG 2.2 AA** with Radix focus mgmt and ARIA patterns.
* English first; copy structured for future i18n.

---

## 6) Information Architecture

**Core entities**

* **User**: identity, profile, preferences, visibility, DM settings.
* **InterestTag**: canonical interest label (e.g., “LLM Agents”, “Data Viz”).
* **Chapter**: geo point (city/lat/lon), name, slug, activity score.
* **Membership**: user ↔ chapter relationship + role (member|chapter_admin).
* **Role**: global_admin flag at user level.
* **Post**: author, optional chapter scope, body, media metadata, OG metadata, visibility, timestamps.
* **Conversation**: pairwise thread between two users.
* **Message**: body, sender, timestamps, delivery metadata.
* **AuditLog**: actor, action, target, timestamp for security and moderation.

**Key relationships**

* User ↔ Membership ↔ Chapter (many‑to‑many).
* User ↔ InterestTag (many‑to‑many).
* User ↔ Post (one‑to‑many), Chapter ↔ Post (optional one‑to‑many).
* Conversation ↔ Message (one‑to‑many).

**Data retention & deletion**

* Users can delete posts and disable DMs. Account deletion removes profile and DMs; posts may be anonymized for aggregate metrics.

---

## 7) System Architecture (Narrative)

* **Frontend**: Next.js (App Router) PWA using shadcn/ui (Radix primitives + Tailwind); responsive, accessible, themeable.
* **Backend**: Node/TypeScript API for CRUD + real‑time WS gateway. JSON payloads with schema validation.
* **Storage**: PostgreSQL 16 for primary data; design tables to support future partitioning (e.g., posts/messages by time). Redis for caching/sessions and Pub/Sub for real‑time fan‑out.
* **Media**: Object storage for images (e.g., S3) with pre‑signed URLs; thumbnails generated server‑side or deferred post‑MVP.
* **Topology**: Browser → AWS ALB → VM (Compose services). ALB terminates HTTP (add HTTPS w/ ACM later). WebSocket upgrade flows through ALB to the API. Keep ALB idle timeout default; clients send WS pings periodically.

---

## 8) Deployment & Operations (MVP)

* **Environments**: Local (Compose), Staging (optional), Production (single VM).
* **Ingress**: ALB public DNS; HTTP:80 initially. Post‑MVP: add HTTPS:443 listener with ACM; redirect HTTP→HTTPS if desired.
* **Secrets**: environment variables for database, cache, mail, and storage credentials (rotation plan post‑MVP).
* **Backups**: daily database snapshot plan; media stored durably in object storage.
* **Runbooks**: start/stop stack, health verification (feed, post, DM echo), simple troubleshooting (logs, WS connectivity, storage reachability).

---

## 9) Security & Privacy

**Baseline (MVP)**

* OWASP ASVS L1 controls: auth/session integrity, input validation, output encoding, rate limiting, logging of auth/admin actions.
* Security headers: HSTS (after HTTPS), CSP (report‑only at first), X‑Content‑Type‑Options, X‑Frame‑Options, Permissions‑Policy.
* Access controls: RBAC (member, chapter_admin, global_admin). Role checks enforced server‑side.
* Privacy: explicit DM opt‑in; city‑level visibility by default; no raw coords shared with other users.

**Backlog (post‑MVP)**

* Connection pooling (PgBouncer), read replica, table partitioning.
* Moderation queue, abuse heuristics, spam throttles.
* Secrets management, key rotation, CSP enforcement, signed downloads by role.

---

## 10) Metrics & KPIs

* **Activation**: % completing profile; time to first post; chapter join rate.
* **Engagement**: DAU/WAU/MAU; posts per user; DM starts per day; like rate.
* **Chapter health**: actives 7/30d; RSVP click‑outs (if integrated later); new joins.
* **Quality signals**: report rate; block rate; retention (week‑over‑week).

---

## 11) Acceptance Criteria (Demo‑ready)

1. A new user can join via magic link, set interests and city, and see **≥3** chapter suggestions with rationale.
2. Global and Local feeds render, paginate, and accept new posts (text, image, link preview).
3. Two distinct users can exchange DMs in real time via ALB, with basic presence and block capability.
4. Admin Dashboard shows non‑PII chapter metrics and supports a CSV export.
5. PWA is installable (manifest present) and caches a small set of recent posts for offline read.

---

## 12) Testing Strategy (Planning)

* **Unit**: entity validation, ranking logic, feed pagination rules, WS message schema.
* **Integration**: auth flow (magic link), posting with OG preview, DM persistence and reconnection behavior.
* **E2E**: join → personalize → suggest → post → DM → admin metrics → export.
* **Accessibility**: keyboard navigation, landmarks, color contrast, focus visibility.
* **Performance**: measure P50/P95 feed reads and DM RTT under nominal dev load.

---

## 13) Risks & Mitigations

* **Realtime message loss (at‑most‑once)**: show transient state, fetch recent window after reconnect, allow user resend.
* **Spam/abuse on global feed**: rate limits, cooldowns, quick report, admin removal.
* **OG scraping latency**: strict timeouts and allowlist; degrade gracefully if preview fails.
* **Single‑VM limits**: set expectations; plan PgBouncer/replicas/partitions in roadmap.

---

## 14) Roadmap

* **MVP (Hackathon)**: full flow + Admin lite + PWA installability + VM/ALB HTTP.
* **M2 (Post‑MVP)**: HTTPS w/ ACM; PgBouncer; moderation queue; analytics polish; image thumbnailing.
* **M3 (Scale)**: read replica; partitions; vector search for matchmaking; events/check‑in; SSO; EKS migration path.

---

## 15) Launch & Demo Plan

* Seed dataset (chapters, users, interests, posts, conversations) for consistent demos.
* 90‑second script: join → suggest → local post → DM → admin metrics → CSV.
* Post‑demo checklist: HTTPS enablement, performance pass, backlog triage.

---

## 16) Governance & Ways of Working

* **Change control**: maintain a lightweight decision log in the repo.
* **Design reviews**: UI/UX review against accessibility and style checklist.
* **Security reviews**: pre‑release header check, auth/session review.
* **Ops**: simple on‑call rotation (during hackathon), incident notes in repo.

---

## 17) Glossary

* **Global feed**: network‑wide public posts.
* **Local feed**: posts scoped to user’s joined/nearby chapters.
* **DM**: direct message between two members.
* **Chapter health**: aggregate engagement metrics over 7/30 days.

---

## 18) Decisions (to date)

* ALB first on HTTP:80; HTTPS/ACM added post‑MVP.
* No ALB access logs in MVP; rely on app logs.
* No geo limits; city‑level visibility only.
* DMs strictly in‑app; no SMS/email relays.
* Neutral OSS branding as **AIC HUB**.
