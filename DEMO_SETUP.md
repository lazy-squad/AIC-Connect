# AIC Hub Articles Feature Demo Setup

This guide will help you set up the Articles feature demo with rich sample data to showcase all functionality.

## 🚀 Quick Start

1. **Run Database Migration**
   ```bash
   cd apps/api
   uv run alembic upgrade head
   ```

2. **Seed Sample Data**
   ```bash
   cd apps/api/scripts
   uv run python run_seeding.py
   ```

3. **Start the Backend**
   ```bash
   cd apps/api
   uv run fastapi dev src/aic_hub/main.py
   ```

4. **Start the Frontend**
   ```bash
   cd apps/web
   npm run dev
   ```

5. **Open Your Browser**
   - Navigate to `http://localhost:3000`
   - Click "Articles" in the navigation

## 📝 Sample Data Overview

### Users Created
- **Dr. Alex Chen** - AI Research Scientist (OpenAI)
  - Expertise: LLMs, Fine-tuning, Prompting, Training
  - 2 articles + 1 draft

- **Sarah Williams** - RAG Systems Expert (Vector Labs)
  - Expertise: RAG, Vector DBs, Embeddings, Search
  - 1 article + 1 draft

- **Marcus Rodriguez** - AI Safety Researcher (Anthropic)
  - Expertise: Safety, Ethics, Benchmarks, RL
  - 1 article

- **Prof. Lisa Thompson** - Robotics Professor (MIT)
  - Expertise: Robotics, Computer Vision, RL, Training
  - 1 article

- **David Kim** - AI Tools Builder (AI Startup Inc)
  - Expertise: Tools, Inference, Agents, NLP
  - 1 article

### Articles Created

1. **"Building Production-Ready RAG Systems: Lessons from the Trenches"** by Sarah Williams
   - Tags: RAG, Vector DBs, Embeddings, Tools
   - Rich technical content with code examples
   - 1,247 views

2. **"The Future of AI Agents: Beyond Simple Chatbots"** by Dr. Alex Chen
   - Tags: Agents, LLMs, Prompting, Tools
   - Architectural patterns and examples
   - 892 views

3. **"AI Safety in Practice: Lessons from Deploying LLMs at Scale"** by Marcus Rodriguez
   - Tags: Safety, Ethics, LLMs, Benchmarks
   - Real-world safety measures and code
   - 645 views

4. **"Computer Vision Meets Robotics: Teaching Robots to See and Act"** by Prof. Lisa Thompson
   - Tags: Robotics, Computer Vision, Training, RL
   - Technical depth with NeRF and CLIP examples
   - 423 views

5. **"Building AI Tools That Developers Actually Want to Use"** by David Kim
   - Tags: Tools, Inference, Agents, NLP
   - Developer adoption insights and principles
   - 1,156 views

### Draft Articles

1. **"Understanding Transformer Architecture: A Visual Guide"** by Dr. Alex Chen
   - Work-in-progress technical guide
   - Demonstrates draft workflow

2. **"Scaling Vector Databases for Production RAG Systems"** by Sarah Williams
   - Performance optimization content
   - Shows collaborative editing potential

## 🎯 Demo Scenarios

### 1. Browse and Discover Articles
- Visit `/articles` to see the main articles page
- Use tag filtering to find articles by topic
- Try search functionality with terms like "RAG" or "safety"
- Test different sorting options (Latest, Popular, Trending)

### 2. Read Full Articles
- Click on any article to view the full content
- Notice the rich text formatting with:
  - Headings and subheadings
  - Code blocks with syntax highlighting
  - Bullet and numbered lists
  - Blockquotes for callouts
  - Inline text formatting

### 3. Author Experience
- Visit `/articles/new` to create a new article
- Use the Tiptap editor with full formatting toolbar
- Add tags from the AI taxonomy
- Save as draft or publish immediately

### 4. Draft Management
- Visit `/drafts` to see draft articles
- Edit existing drafts
- Publish drafts directly from the drafts page

### 5. User Profiles and Attribution
- Click on author names to see their profiles
- Notice article counts and expertise tags
- View articles by specific authors

## 🔧 Technical Features Demonstrated

### Backend
- ✅ Complete CRUD API for articles
- ✅ Slug generation with conflict resolution
- ✅ Tag validation against AI taxonomy
- ✅ View count tracking
- ✅ Draft/publish workflow
- ✅ Search and filtering
- ✅ Pagination
- ✅ User authentication and authorization

### Frontend
- ✅ Rich text editing with Tiptap
- ✅ Responsive design
- ✅ Real-time validation
- ✅ Tag-based filtering
- ✅ Search functionality
- ✅ Draft management
- ✅ Navigation integration

### Content Quality
- ✅ Realistic AI industry topics
- ✅ Technical depth appropriate for the audience
- ✅ Varied content types (tutorials, insights, research)
- ✅ Proper formatting and structure
- ✅ Code examples and technical details

## 🎨 Content Highlights

The sample articles showcase:
- **Technical tutorials** with step-by-step guides
- **Industry insights** from experienced practitioners
- **Code examples** with syntax highlighting
- **Best practices** and lessons learned
- **Cutting-edge research** in accessible language
- **Practical advice** for real-world applications

## 📊 Metrics and Engagement

Sample data includes:
- Realistic view counts (400-1200 per article)
- Varied publication dates (1-12 days ago)
- Like counts and engagement metrics
- Different user interaction patterns
- Time-based activity simulation

## 🔍 Testing Scenarios

1. **Create Content Flow**
   - Register a new user account
   - Create your first article
   - Use all formatting options
   - Save as draft, then publish

2. **Discovery Flow**
   - Search for specific topics
   - Filter by multiple tags
   - Navigate through pagination
   - Sort by different criteria

3. **Collaboration Flow**
   - View other users' articles
   - See author profiles and expertise
   - Discover related content by tags
   - Follow authorship attribution

4. **Content Management**
   - Edit existing drafts
   - Update published articles
   - Manage publication status
   - Delete unwanted content

## 🚨 Demo Notes

- All sample users have placeholder passwords (not set up for login)
- View counts increment on each article view
- Tag system uses the predefined AI taxonomy
- Content is designed to be technically accurate but simplified for demo purposes
- Search functionality works across titles and summaries

## 🎯 Success Criteria

The demo successfully showcases:
- ✅ Full article authoring experience
- ✅ Rich content browsing and discovery
- ✅ Professional-quality technical content
- ✅ Seamless integration with existing platform
- ✅ Scalable architecture for real-world use
- ✅ Mobile-responsive design
- ✅ Fast, smooth user experience

Ready to explore the future of AI knowledge sharing! 🚀