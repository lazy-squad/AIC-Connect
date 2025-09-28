# AIC Hub Tag System & Search Implementation

A comprehensive tag system and search functionality for the AIC Hub platform, enabling rich content discovery and organization.

## 🏷️ Tag System Overview

### Fixed AI Taxonomy
The system uses a curated set of 19 immutable AI tags covering:

**Core AI/ML**: LLMs, RAG, Agents, Fine-tuning, Prompting
**Infrastructure**: Vector DBs, Embeddings, Training, Inference
**Governance**: Ethics, Safety, Benchmarks, Datasets, Tools
**Applications**: Computer Vision, NLP, Speech, Robotics, RL

### Tag Features
- **Usage Tracking**: Automatic counting across articles, spaces, and user expertise
- **Trending Scores**: Algorithm combining recency, growth, and popularity
- **Relationships**: Pre-defined connections between related tags
- **Suggestions**: Content-based tag recommendations using keyword matching
- **Descriptions**: Rich descriptions for each tag for better understanding

## 🔍 Search System

### Full-Text Search
- **PostgreSQL Native**: Uses PostgreSQL's built-in full-text search capabilities
- **Multi-Entity**: Searches across articles, spaces, and users simultaneously
- **Ranking**: Combined scoring using relevance, popularity, and recency
- **Highlighting**: Marked search terms in results for better UX

### Search Features
- **Universal Search**: Single endpoint for all content types
- **Autocomplete**: Fast suggestions for tags, articles, and spaces
- **Faceted Search**: Filter results by type and tags
- **Search Index**: Dedicated table for optimized search performance

## 🛠️ Technical Implementation

### Database Models

#### TagUsage
```python
class TagUsage(Base):
    tag: str (PRIMARY KEY)
    article_count: int
    space_count: int
    user_count: int
    last_used_at: datetime
    trending_score: float
    week_count: int
    month_count: int
```

#### SearchIndex
```python
class SearchIndex(Base):
    id: UUID (PRIMARY KEY)
    entity_type: str  # article, space, user
    entity_id: UUID
    title: str
    content: str
    tags: list[str]
    search_vector: TSVector  # PostgreSQL full-text search
    created_at: datetime
    updated_at: datetime
```

### API Endpoints

#### Tags API
- `GET /api/tags` - Get all tags with usage statistics
- `GET /api/tags/{tag}` - Get detailed tag information
- `POST /api/tags/suggest` - Get tag suggestions for content

#### Search API
- `GET /api/search` - Universal search across platform
- `GET /api/search/autocomplete` - Autocomplete suggestions
- `POST /api/search/index` - Trigger search index update (admin)

### Service Layer

#### TagService
```python
class TagService:
    @staticmethod
    async def update_tag_usage(db, tag, entity_type, delta=1)
    async def calculate_trending_scores(db)
    async def suggest_tags(title, content, limit=5)
    async def get_tag_stats(db, tag)
    async def get_all_tags_with_stats(db, sort="popular")
```

#### SearchService
```python
class SearchService:
    @staticmethod
    async def search(db, query, search_type="all", tags=None)
    async def update_search_index(db, entity_type, entity_id, title, content, tags)
    async def autocomplete(db, query, limit=5)
```

## 🔄 Integration Points

### Article Lifecycle
- **Create**: Add tag usage and search index for published articles
- **Update**: Handle tag changes and publication status updates
- **Delete**: Clean up tag usage and remove from search index

### Space Lifecycle
- **Create**: Track tags for public spaces only
- **Update**: Handle visibility and tag changes
- **Delete**: Clean up tag usage and search index

### User Profiles
- **Expertise Tags**: Track user expertise in tag usage statistics
- **Search Integration**: Include users in universal search results

## 📊 Performance Optimizations

### Database Indexes
```sql
-- Tag usage indexes
CREATE INDEX idx_tag_usage_trending ON tag_usage (trending_score);
CREATE INDEX idx_tag_usage_counts ON tag_usage (article_count, space_count, user_count);

-- Search indexes
CREATE INDEX idx_search_vector ON search_index USING gin(search_vector);
CREATE INDEX idx_search_tags ON search_index USING gin(tags);
CREATE INDEX idx_search_entity ON search_index (entity_type, entity_id);

-- Full-text search on existing tables
CREATE INDEX idx_articles_search ON articles USING gin(
    to_tsvector('english', title || ' ' || COALESCE(summary, '') || ' ' || array_to_string(tags, ' '))
);
```

### Caching Strategy
- Tag statistics cached for 5 minutes
- Trending scores pre-calculated hourly
- Search results benefit from PostgreSQL query caching
- Autocomplete queries are lightweight and fast

## 🎯 Demo Data Structure

### Sample Users (6 experts)
- **Alex Chen**: RAG, LLMs, Vector DBs, Embeddings, Fine-tuning
- **Sarah Rodriguez**: Agents, Tools, Prompting, LLMs
- **Dr. Lisa Wang**: NLP, Prompting, Safety, Ethics, Benchmarks
- **Mike Thompson**: Computer Vision, Training, Datasets, Inference
- **David Kim**: Robotics, RL, Computer Vision, Training
- **Anna Kowalski**: Tools, Inference, Fine-tuning, LLMs

### Sample Spaces (6 communities)
- **RAG Systems**: Community for RAG discussions (156 members)
- **AI Agents Hub**: Multi-agent systems exploration (89 members)
- **Computer Vision Research**: CV developments (134 members)
- **AI Safety & Ethics**: Responsible AI discussion (234 members)
- **Embodied AI Lab**: Robotics meets AI (67 members)
- **AI Engineering Tools**: Developer tools focus (112 members)

### Sample Articles (10 detailed posts)
- **"Building Production RAG Systems"** by Alex Chen
- **"Multi-Agent Systems: Orchestrating AI Collaboration"** by Sarah Rodriguez
- **"AI Safety in Production: Monitoring and Guardrails"** by Dr. Lisa Wang
- **"Vision-Language Models: Bridging Pixels and Text"** by Mike Thompson
- **"Reinforcement Learning for Robotics"** by David Kim
- Plus 5 more covering various AI topics

## 🚀 Demo Scenarios

### Search Examples
1. **"RAG systems"** → 3 articles, 1 space, 2 experts
2. **"AI agents"** → 2 articles, 1 space, 3 experts
3. **"vector database"** → 4 articles, 1 space, 1 expert
4. **"prompt engineering"** → 2 articles, 0 spaces, 2 experts
5. **"computer vision"** → 3 articles, 1 space, 2 experts

### Tag Suggestions
- **Input**: "Building RAG Systems with Vector Databases"
- **Output**: RAG (0.95), Vector DBs (0.75), Embeddings (0.90), LLMs (0.40)

### Trending Tags
- **RAG**: 85.5 trending score, +15% weekly growth
- **Agents**: 73.2 trending score, +12% weekly growth
- **Safety**: 68.9 trending score, +8% weekly growth

## 🔧 Setup Instructions

### 1. Database Migration
```bash
uv run alembic upgrade head
```

### 2. Create Demo Data
```bash
uv run python create_demo_data.py
```

### 3. Test Functionality
```bash
# Test tag suggestions
uv run python -c "
from aic_hub.services.tag_service import TagService
import asyncio
result = asyncio.run(TagService.suggest_tags('RAG Systems', 'vector databases embeddings'))
print(result)
"
```

## 📈 Analytics & Monitoring

### Tag Usage Metrics
- Track tag adoption over time
- Monitor trending scores and weekly growth
- Identify popular vs. underutilized tags

### Search Performance
- Query processing times (target: <100ms)
- Search result relevance scoring
- Autocomplete suggestion quality

### User Engagement
- Most searched terms and tags
- Content discovery patterns
- Tag-based content filtering usage

## 🔮 Future Enhancements

### Advanced Search
- **Semantic Search**: Use embeddings for better relevance
- **Personalization**: Tailor results based on user interests
- **Saved Searches**: Allow users to save and monitor searches

### Enhanced Tag System
- **Tag Hierarchies**: Organize tags in categories and subcategories
- **User-Generated Tags**: Allow community tag creation with moderation
- **Tag Synonyms**: Handle alternative terms and aliases

### Machine Learning
- **ML-Based Suggestions**: Train models on tagging patterns
- **Content Similarity**: Find related content using embeddings
- **Recommendation Engine**: Suggest content based on user activity

## 🎉 Ready for Demo!

The tag system and search functionality provide a solid foundation for content discovery in the AIC Hub. The implementation includes:

✅ **Complete Backend**: Models, services, and APIs
✅ **Database Schema**: Optimized for performance and scalability
✅ **Rich Demo Data**: Realistic content for demonstration
✅ **Integration Ready**: Properly integrated with existing features
✅ **Performance Optimized**: Efficient queries and indexing
✅ **Extensible Design**: Easy to enhance and expand

The system enables users to discover content through multiple pathways: searching, browsing tags, exploring relationships, and following recommendations.