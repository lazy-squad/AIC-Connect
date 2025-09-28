# 🎬 AIC Connect Demo Guide

This guide helps you set up and explore the demo data for AIC Connect, featuring the new **Collaboration Spaces** functionality.

## 🚀 Quick Setup

1. **Start the services**:
   ```bash
   pnpm compose:up    # Start database
   pnpm dev          # Start API and web servers
   ```

2. **Create demo data**:
   ```bash
   cd apps/api
   uv run python scripts/create_demo_data.py
   ```

3. **Visit the app**: http://localhost:3000

## 👥 Demo Users

All demo users use the password: `demopassword123`

| User | Email | Role | Expertise |
|------|-------|------|-----------|
| **Alice Chen** | alice@example.com | AI Researcher @ OpenAI | RAG, Vector DBs, LLMs |
| **Bob Rodriguez** | bob@example.com | ML Engineer @ Anthropic | MLOps, LLMs, Fine-tuning |
| **Carol Kim** | carol@example.com | AI Engineer @ Hugging Face | NLP, Transformers, RAG |
| **David Thompson** | david@example.com | Full-stack @ Vercel | RAG, AI Integration |
| **Dr. Eva Nakamura** | eva@example.com | AI Safety Researcher | AI Safety, Interpretability |

## 🏠 Demo Spaces

### Public Spaces

1. **RAG Enthusiasts** (Owner: Alice)
   - Focus: Retrieval-Augmented Generation systems
   - Members: Bob, Carol, David
   - Tags: RAG, Vector DBs, Embeddings

2. **LLM Fine-tuning Masters** (Owner: Bob)
   - Focus: Fine-tuning large language models
   - Members: Alice, Carol, Eva
   - Tags: Fine-tuning, LLMs, Training

3. **Vector Database Deep Dive** (Owner: Carol)
   - Focus: Vector database comparisons and implementations
   - Members: Alice, Bob, David
   - Tags: Vector DBs, Embeddings, Search

4. **Production AI Systems** (Owner: David)
   - Focus: Real-world AI deployment experiences
   - Members: Alice, Bob, Carol
   - Tags: MLOps, Production, LLMs

5. **Embeddings & Semantic Search** (Owner: Alice)
   - Focus: Embeddings and semantic search techniques
   - Members: Bob, Carol, David
   - Tags: Embeddings, Search, NLP

### Private Spaces

6. **AI Safety Research Group** (Owner: Eva)
   - Focus: AI safety and alignment research
   - Members: Alice, Bob (invited only)
   - Tags: AI Safety, Research, LLMs

## 📝 Demo Articles

1. **"Building a Production RAG System with 10M+ Documents"** by Alice
   - Comprehensive guide to scaling RAG systems
   - Shared in: RAG Enthusiasts, Production AI Systems

2. **"Fine-tuning LLaMA 2 for Domain-Specific Tasks"** by Bob
   - Complete guide to LLaMA 2 fine-tuning
   - Shared in: LLM Fine-tuning Masters, Production AI Systems

3. **"Vector Database Comparison: Pinecone vs Weaviate vs Chroma"** by Carol
   - Detailed comparison of popular vector databases
   - Shared in: Vector Database Deep Dive, RAG Enthusiasts, Embeddings & Semantic Search

## 🎯 Demo Scenarios

### Scenario 1: Exploring Public Spaces
1. Log in as **David** (david@example.com)
2. Visit `/spaces` to browse all public spaces
3. Join "RAG Enthusiasts" space
4. Browse shared articles in the space
5. Try creating a new space

### Scenario 2: Space Management
1. Log in as **Alice** (alice@example.com)
2. Visit "My Spaces" to see owned spaces
3. Go to "RAG Enthusiasts" space details
4. View members and their roles
5. Try sharing an article to the space

### Scenario 3: Private Space Access
1. Log in as **Carol** (carol@example.com)
2. Try to access "AI Safety Research Group" (should be blocked)
3. Log in as **Eva** (eva@example.com)
4. Access the private space successfully
5. Invite new members to the private space

### Scenario 4: Cross-Feature Integration
1. Log in as **Bob** (bob@example.com)
2. Browse the activity feed to see space activities
3. Search for spaces using tags
4. View user profiles and their space memberships
5. Create and publish a new article, then share it to relevant spaces

## 🔧 Demo Features Showcase

### ✅ Spaces Core Features
- [x] Public and private space visibility
- [x] Space creation with rich metadata
- [x] Member management with roles (owner, moderator, member)
- [x] Join/leave functionality
- [x] Article sharing to spaces
- [x] Tag-based space discovery

### ✅ Integration Features
- [x] Activity tracking for feeds
- [x] Search integration (spaces appear in search)
- [x] Tag usage analytics
- [x] User profile space counts
- [x] Navigation integration

### ✅ UI/UX Features
- [x] Responsive space cards
- [x] Tabbed space detail pages
- [x] Member list with role badges
- [x] Real-time membership updates
- [x] "My Spaces" filtering

## 🎮 Interactive Demo Flow

1. **Start as a New User**:
   - Create account or log in as David
   - Explore the spaces directory
   - Join 2-3 interesting spaces
   - Browse articles shared in those spaces

2. **Become a Space Creator**:
   - Create your own space about a topic you're passionate about
   - Write a description and add relevant tags
   - Invite other demo users to join

3. **Experience Community Features**:
   - Share existing articles to relevant spaces
   - Pin important articles in spaces you moderate
   - Update member roles in spaces you own

4. **Test Edge Cases**:
   - Try accessing private spaces you're not a member of
   - Attempt to leave a space you own (should be blocked)
   - Test space search and filtering

## 🧹 Cleanup

To clear demo data:
```bash
cd apps/api
uv run python scripts/create_demo_data.py --clear
```

## 📊 Demo Metrics

The demo data includes:
- **5 users** with diverse backgrounds and expertise
- **6 spaces** (5 public, 1 private) covering different AI topics
- **3 high-quality articles** with realistic content
- **15+ space memberships** creating an active community
- **7 article shares** distributed across relevant spaces
- **Activity records** for feed integration

## 🎯 Key Demo Talking Points

1. **Rich Community Building**: Spaces enable topic-focused communities
2. **Flexible Visibility**: Public spaces for discovery, private for exclusive groups
3. **Content Curation**: Article sharing creates curated knowledge bases
4. **Role-based Management**: Owners and moderators can manage community quality
5. **Cross-feature Integration**: Spaces work seamlessly with articles, feeds, and search
6. **Scalable Architecture**: Ready for real-world usage with proper indexing and caching

---

**Happy exploring! 🚀**

The Spaces feature transforms AIC Connect from individual content consumption to collaborative knowledge sharing. Each space becomes a focused community where experts can share insights, discuss challenges, and build together.