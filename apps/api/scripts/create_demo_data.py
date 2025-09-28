#!/usr/bin/env python3
"""Create rich demo data for AIC Connect Spaces feature."""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.sql import text

from aic_hub.config import settings
from aic_hub.models import User, Article, Space, SpaceArticle, space_members
from aic_hub.security import hash_password
from aic_hub.services import SpaceService, ActivityService


# Demo users data
DEMO_USERS = [
    {
        "email": "alice@example.com",
        "username": "alice_ai",
        "display_name": "Alice Chen",
        "bio": "AI Researcher specializing in RAG systems and vector databases. PhD in Computer Science from Stanford.",
        "company": "OpenAI",
        "location": "San Francisco, CA",
        "expertise_tags": ["RAG", "Vector DBs", "LLMs", "Fine-tuning"],
        "github_username": "alice-chen-ai"
    },
    {
        "email": "bob@example.com",
        "username": "bob_ml",
        "display_name": "Bob Rodriguez",
        "bio": "Machine Learning Engineer with 8 years experience. Love building production ML systems.",
        "company": "Anthropic",
        "location": "London, UK",
        "expertise_tags": ["MLOps", "LLMs", "Embeddings", "Fine-tuning"],
        "github_username": "bob-ml-eng"
    },
    {
        "email": "carol@example.com",
        "username": "carol_data",
        "display_name": "Carol Kim",
        "bio": "Data Scientist turned AI Engineer. Passionate about making AI accessible to everyone.",
        "company": "Hugging Face",
        "location": "Paris, France",
        "expertise_tags": ["NLP", "Transformers", "RAG", "Vector DBs"],
        "github_username": "carol-data-sci"
    },
    {
        "email": "david@example.com",
        "username": "david_dev",
        "display_name": "David Thompson",
        "bio": "Full-stack developer exploring AI integration. Building the future of human-AI collaboration.",
        "company": "Vercel",
        "location": "New York, NY",
        "expertise_tags": ["RAG", "LLMs", "AI Integration"],
        "github_username": "david-fullstack"
    },
    {
        "email": "eva@example.com",
        "username": "eva_research",
        "display_name": "Dr. Eva Nakamura",
        "bio": "Research Scientist in AI Safety. Working on alignment and interpretability of large language models.",
        "company": "Alignment Research Center",
        "location": "Berkeley, CA",
        "expertise_tags": ["AI Safety", "LLMs", "Fine-tuning", "Interpretability"],
        "github_username": "eva-ai-safety"
    }
]

# Demo spaces data
DEMO_SPACES = [
    {
        "name": "RAG Enthusiasts",
        "description": "A community for discussing Retrieval-Augmented Generation systems, sharing implementations, and solving common challenges. From basic RAG to advanced techniques like multi-hop reasoning.",
        "tags": ["RAG", "Vector DBs", "Embeddings"],
        "visibility": "public",
        "owner_email": "alice@example.com"
    },
    {
        "name": "LLM Fine-tuning Masters",
        "description": "Share your experiences with fine-tuning large language models. Discuss techniques, datasets, hardware requirements, and optimization strategies.",
        "tags": ["Fine-tuning", "LLMs", "Training"],
        "visibility": "public",
        "owner_email": "bob@example.com"
    },
    {
        "name": "Vector Database Deep Dive",
        "description": "Everything about vector databases: Pinecone, Weaviate, Chroma, Qdrant, and more. Performance comparisons, use cases, and implementation guides.",
        "tags": ["Vector DBs", "Embeddings", "Search"],
        "visibility": "public",
        "owner_email": "carol@example.com"
    },
    {
        "name": "AI Safety Research Group",
        "description": "Private group for researchers working on AI safety, alignment, and interpretability. Share papers, discuss methodologies, and collaborate on projects.",
        "tags": ["AI Safety", "Research", "LLMs"],
        "visibility": "private",
        "owner_email": "eva@example.com"
    },
    {
        "name": "Production AI Systems",
        "description": "Real-world experiences deploying AI systems in production. Discuss scaling, monitoring, costs, and lessons learned from production deployments.",
        "tags": ["MLOps", "Production", "LLMs"],
        "visibility": "public",
        "owner_email": "david@example.com"
    },
    {
        "name": "Embeddings & Semantic Search",
        "description": "Explore the world of embeddings and semantic search. From basic sentence transformers to advanced multimodal embeddings.",
        "tags": ["Embeddings", "Search", "NLP"],
        "visibility": "public",
        "owner_email": "alice@example.com"
    }
]

# Demo articles data
DEMO_ARTICLES = [
    {
        "title": "Building a Production RAG System with 10M+ Documents",
        "slug": "production-rag-system-10m-documents",
        "summary": "A comprehensive guide to building and scaling a RAG system that can handle millions of documents with sub-second query times.",
        "content": """# Building a Production RAG System with 10M+ Documents

## Introduction

Retrieval-Augmented Generation (RAG) has revolutionized how we build AI applications that need to work with large knowledge bases. However, scaling RAG systems to handle millions of documents while maintaining fast query times presents unique challenges.

## Architecture Overview

Our system processes over 10 million technical documents with an average query time of 200ms. Here's how we did it:

### 1. Document Processing Pipeline

- **Chunking Strategy**: We use a hybrid approach combining semantic chunking with fixed-size overlaps
- **Embedding Model**: Fine-tuned sentence-transformers/all-MiniLM-L6-v2 for our domain
- **Vector Storage**: Pinecone with 1536-dimensional vectors

### 2. Retrieval Optimization

- **Hierarchical Search**: Two-stage retrieval with coarse and fine-grained matching
- **Query Expansion**: Automatic query rewriting using smaller LLMs
- **Hybrid Search**: Combining dense and sparse retrieval methods

### 3. Generation Pipeline

- **Model Selection**: GPT-4-turbo for production, with Claude-3 as fallback
- **Context Management**: Dynamic context window optimization
- **Response Caching**: Redis-based caching for common queries

## Performance Metrics

- **Query Latency**: P99 < 500ms, P95 < 300ms
- **Retrieval Accuracy**: 92% relevant documents in top-5 results
- **System Uptime**: 99.9% availability over 6 months

## Lessons Learned

1. **Embedding Quality Matters More Than Size**: A well-fine-tuned smaller model outperforms a generic larger one
2. **Chunk Overlap is Critical**: 20% overlap between chunks significantly improved recall
3. **Monitor Everything**: Comprehensive logging saved us countless debugging hours

## Code Examples

```python
# Example chunk processing
def create_chunks(document, chunk_size=512, overlap=0.2):
    sentences = split_into_sentences(document)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        if current_length + len(sentence) > chunk_size and current_chunk:
            # Create chunk with metadata
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "metadata": extract_metadata(chunk_text)
            })

            # Start new chunk with overlap
            overlap_size = int(len(current_chunk) * overlap)
            current_chunk = current_chunk[-overlap_size:] if overlap_size > 0 else []
            current_length = sum(len(s) for s in current_chunk)

        current_chunk.append(sentence)
        current_length += len(sentence)

    return chunks
```

## Next Steps

We're working on multimodal RAG to handle images and tables, and exploring graph-based retrieval for complex reasoning tasks.

What challenges have you faced scaling RAG systems? Share your experiences!""",
        "tags": ["RAG", "Vector DBs", "Production", "Scaling"],
        "author_email": "alice@example.com",
        "status": "published"
    },
    {
        "title": "Fine-tuning LLaMA 2 for Domain-Specific Tasks: A Complete Guide",
        "slug": "fine-tuning-llama2-domain-specific-complete-guide",
        "summary": "Step-by-step guide to fine-tuning LLaMA 2 for specialized domains, including data preparation, training strategies, and evaluation methods.",
        "content": """# Fine-tuning LLaMA 2 for Domain-Specific Tasks: A Complete Guide

## Why Fine-tune?

While general-purpose LLMs are incredibly capable, fine-tuning for specific domains can significantly improve performance, reduce hallucinations, and enable specialized behaviors.

## Dataset Preparation

### 1. Data Collection
- **Quality over Quantity**: 10k high-quality examples > 100k mediocre ones
- **Diverse Sources**: Mix of internal docs, public datasets, and synthetic data
- **Format Consistency**: Standardize input/output formats early

### 2. Data Cleaning Pipeline
```python
def clean_training_data(examples):
    cleaned = []
    for example in examples:
        # Remove low-quality examples
        if len(example['output']) < 10:
            continue

        # Filter inappropriate content
        if contains_harmful_content(example['input']):
            continue

        # Normalize formatting
        example['input'] = normalize_text(example['input'])
        example['output'] = normalize_text(example['output'])

        cleaned.append(example)

    return cleaned
```

## Training Configuration

### Hardware Requirements
- **Minimum**: 1x A100 (80GB) for 7B model with LoRA
- **Recommended**: 4x A100 (80GB) for full fine-tuning
- **Memory Optimization**: DeepSpeed ZeRO-3 + gradient checkpointing

### Training Parameters
```yaml
model_name: "meta-llama/Llama-2-7b-hf"
learning_rate: 2e-4
batch_size: 4
gradient_accumulation_steps: 8
max_steps: 1000
warmup_steps: 100
weight_decay: 0.01
lora_r: 16
lora_alpha: 32
lora_dropout: 0.1
```

## Evaluation Strategies

### Automated Metrics
- **Perplexity**: Measure model confidence
- **BLEU/ROUGE**: For generation tasks
- **Custom Metrics**: Domain-specific evaluation

### Human Evaluation
- **A/B Testing**: Compare with baseline models
- **Expert Review**: Domain experts rate outputs
- **Real-world Testing**: Deploy to subset of users

## Results & Insights

Our fine-tuned model showed:
- **40% improvement** in domain-specific accuracy
- **60% reduction** in hallucinations
- **2x faster** convergence on downstream tasks

## Common Pitfalls

1. **Overfitting**: Monitor validation loss carefully
2. **Catastrophic Forgetting**: Include general examples in training
3. **Data Leakage**: Ensure train/test split integrity
4. **Evaluation Bias**: Use diverse evaluation sets

## Production Deployment

```python
# Model serving with vLLM
from vllm import LLM, SamplingParams

model = LLM(
    model="./fine-tuned-llama2",
    tensor_parallel_size=2,
    max_model_len=4096
)

sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=512
)

def generate_response(prompt):
    outputs = model.generate([prompt], sampling_params)
    return outputs[0].outputs[0].text
```

## Conclusion

Fine-tuning LLaMA 2 requires careful planning but delivers substantial improvements for domain-specific tasks. Start small, measure everything, and iterate based on real user feedback.

What's your experience with fine-tuning? Any specific challenges you'd like to discuss?""",
        "tags": ["Fine-tuning", "LLMs", "LLaMA", "Training"],
        "author_email": "bob@example.com",
        "status": "published"
    },
    {
        "title": "Vector Database Comparison: Pinecone vs Weaviate vs Chroma",
        "slug": "vector-database-comparison-pinecone-weaviate-chroma",
        "summary": "Comprehensive comparison of popular vector databases based on performance, features, cost, and ease of use for different AI applications.",
        "content": """# Vector Database Comparison: Pinecone vs Weaviate vs Chroma

## Introduction

Choosing the right vector database is crucial for AI applications. This comparison covers the three most popular options based on real-world testing with 1M+ vectors.

## Feature Comparison

| Feature | Pinecone | Weaviate | Chroma |
|---------|----------|----------|--------|
| **Deployment** | Cloud Only | Cloud + Self-hosted | Self-hosted |
| **Scalability** | Excellent | Good | Good |
| **Query Speed** | Fast | Very Fast | Fast |
| **Cost** | $$$ | $$ | $ |
| **Ease of Use** | Excellent | Good | Excellent |

## Performance Benchmarks

### Query Latency (1M vectors, 1536 dimensions)

- **Pinecone**: P95 < 50ms, P99 < 100ms
- **Weaviate**: P95 < 30ms, P99 < 80ms
- **Chroma**: P95 < 60ms, P99 < 120ms

### Throughput (queries per second)

- **Pinecone**: 1000 QPS (p1.x1 pod)
- **Weaviate**: 1200 QPS (8-core instance)
- **Chroma**: 800 QPS (local deployment)

## Detailed Analysis

### Pinecone
**Pros:**
- Excellent developer experience
- Automatic scaling and management
- Strong consistency guarantees
- Great documentation and support

**Cons:**
- Cloud-only (vendor lock-in)
- Higher costs at scale
- Limited customization options

**Best for:** Production applications needing minimal ops overhead

### Weaviate
**Pros:**
- Fastest query performance
- Rich feature set (hybrid search, modules)
- Self-hosting option
- Active open-source community

**Cons:**
- More complex setup and management
- Steeper learning curve
- Resource intensive

**Best for:** Applications needing maximum performance and flexibility

### Chroma
**Pros:**
- Completely free and open-source
- Simple API and setup
- Good for prototyping
- Local development friendly

**Cons:**
- Limited production features
- Basic scaling capabilities
- Fewer advanced features

**Best for:** Development, prototyping, and small-scale applications

## Code Examples

### Pinecone
```python
import pinecone

pinecone.init(api_key="your-key", environment="us-west1-gcp")
index = pinecone.Index("example-index")

# Insert vectors
index.upsert(vectors=[
    ("vec1", [0.1, 0.2, 0.3], {"text": "example"}),
    ("vec2", [0.4, 0.5, 0.6], {"text": "another"})
])

# Query
results = index.query(
    vector=[0.1, 0.2, 0.3],
    top_k=5,
    include_metadata=True
)
```

### Weaviate
```python
import weaviate

client = weaviate.Client("http://localhost:8080")

# Insert
client.data_object.create(
    data_object={"text": "example"},
    class_name="Document",
    vector=[0.1, 0.2, 0.3]
)

# Query
result = client.query.get("Document", ["text"]).with_near_vector({
    "vector": [0.1, 0.2, 0.3]
}).with_limit(5).do()
```

### Chroma
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("documents")

# Insert
collection.add(
    documents=["example text"],
    embeddings=[[0.1, 0.2, 0.3]],
    ids=["doc1"]
)

# Query
results = collection.query(
    query_embeddings=[[0.1, 0.2, 0.3]],
    n_results=5
)
```

## Cost Analysis

### Monthly costs for 1M vectors (1536 dims, 100 QPS):

- **Pinecone**: ~$70/month (p1.x1 pod)
- **Weaviate Cloud**: ~$200/month (managed)
- **Weaviate Self-hosted**: ~$50/month (AWS t3.large)
- **Chroma**: $0 (self-hosted only)

## Migration Considerations

### From Pinecone to Weaviate
- Export vectors via Pinecone API
- Transform metadata format
- Rebuild indexes in Weaviate

### Universal Migration Script
```python
def migrate_vectors(source_db, target_db, batch_size=1000):
    total_migrated = 0

    for batch in source_db.get_vectors(batch_size=batch_size):
        target_batch = []
        for vector in batch:
            target_batch.append({
                'id': vector['id'],
                'vector': vector['values'],
                'metadata': transform_metadata(vector['metadata'])
            })

        target_db.upsert(target_batch)
        total_migrated += len(target_batch)
        print(f"Migrated {total_migrated} vectors")
```

## Recommendations

### Choose Pinecone if:
- You want minimal operational overhead
- Budget allows for premium pricing
- You're building a production application
- Developer experience is priority

### Choose Weaviate if:
- You need maximum query performance
- You want hybrid search capabilities
- You have ops expertise for self-hosting
- You need advanced filtering

### Choose Chroma if:
- You're prototyping or learning
- Budget is very constrained
- You have simple use cases
- You prefer open-source solutions

## Conclusion

All three databases are solid choices depending on your specific needs. Start with your requirements around cost, performance, and operational complexity to guide your decision.

What has been your experience with these vector databases? Any other comparisons you'd like to see?""",
        "tags": ["Vector DBs", "Comparison", "Pinecone", "Weaviate", "Chroma"],
        "author_email": "carol@example.com",
        "status": "published"
    }
]

# Space membership data (which users join which spaces)
SPACE_MEMBERSHIPS = {
    "RAG Enthusiasts": ["bob@example.com", "carol@example.com", "david@example.com"],
    "LLM Fine-tuning Masters": ["alice@example.com", "carol@example.com", "eva@example.com"],
    "Vector Database Deep Dive": ["alice@example.com", "bob@example.com", "david@example.com"],
    "AI Safety Research Group": ["alice@example.com", "bob@example.com"],  # Private group
    "Production AI Systems": ["alice@example.com", "bob@example.com", "carol@example.com"],
    "Embeddings & Semantic Search": ["bob@example.com", "carol@example.com", "david@example.com"]
}

# Article sharing to spaces
ARTICLE_SHARES = {
    "Building a Production RAG System with 10M+ Documents": ["RAG Enthusiasts", "Production AI Systems"],
    "Fine-tuning LLaMA 2 for Domain-Specific Tasks: A Complete Guide": ["LLM Fine-tuning Masters", "Production AI Systems"],
    "Vector Database Comparison: Pinecone vs Weaviate vs Chroma": ["Vector Database Deep Dive", "RAG Enthusiasts", "Embeddings & Semantic Search"]
}


async def create_demo_data():
    """Create all demo data."""
    print("🚀 Creating AIC Connect demo data...")

    # Create async engine and session
    engine = create_async_engine(settings.async_database_url)
    async_session = async_sessionmaker(bind=engine)

    async with async_session() as db:
        try:
            # Create users
            print("👥 Creating demo users...")
            user_map = {}
            for user_data in DEMO_USERS:
                user = User(
                    email=user_data["email"],
                    username=user_data["username"],
                    display_name=user_data["display_name"],
                    bio=user_data["bio"],
                    company=user_data["company"],
                    location=user_data["location"],
                    expertise_tags=user_data["expertise_tags"],
                    github_username=user_data["github_username"],
                    password_hash=hash_password("demopassword123"),  # Same password for all demo users
                    created_at=datetime.utcnow() - timedelta(days=30)
                )
                db.add(user)
                user_map[user_data["email"]] = user

            await db.flush()  # Get user IDs
            print(f"   ✅ Created {len(DEMO_USERS)} users")

            # Create articles
            print("📝 Creating demo articles...")
            article_map = {}
            for article_data in DEMO_ARTICLES:
                author = user_map[article_data["author_email"]]
                article = Article(
                    title=article_data["title"],
                    slug=article_data["slug"],
                    summary=article_data["summary"],
                    content=article_data["content"],
                    tags=article_data["tags"],
                    author_id=author.id,
                    status=article_data["status"],
                    published_at=datetime.utcnow() - timedelta(days=15),
                    created_at=datetime.utcnow() - timedelta(days=20)
                )
                db.add(article)
                article_map[article_data["title"]] = article

            await db.flush()
            print(f"   ✅ Created {len(DEMO_ARTICLES)} articles")

            # Create spaces using SpaceService
            print("🏠 Creating demo spaces...")
            space_map = {}
            for space_data in DEMO_SPACES:
                owner = user_map[space_data["owner_email"]]

                # Use SpaceService to create space (handles owner membership automatically)
                from aic_hub.schemas import SpaceCreate
                space_create = SpaceCreate(
                    name=space_data["name"],
                    description=space_data["description"],
                    tags=space_data["tags"],
                    visibility=space_data["visibility"]
                )

                space = await SpaceService.create_space(
                    db=db,
                    owner_id=owner.id,
                    data=space_create
                )
                space_map[space_data["name"]] = space

            print(f"   ✅ Created {len(DEMO_SPACES)} spaces")

            # Add members to spaces
            print("👥 Adding space memberships...")
            total_memberships = 0
            for space_name, member_emails in SPACE_MEMBERSHIPS.items():
                space = space_map[space_name]
                for email in member_emails:
                    user = user_map[email]
                    # Use SpaceService to join space (handles activity tracking)
                    await SpaceService.join_space(
                        db=db,
                        space_id=space.id,
                        user_id=user.id
                    )
                    total_memberships += 1

            print(f"   ✅ Added {total_memberships} space memberships")

            # Share articles to spaces
            print("📤 Sharing articles to spaces...")
            total_shares = 0
            for article_title, space_names in ARTICLE_SHARES.items():
                article = article_map[article_title]
                author = user_map[DEMO_ARTICLES[0]["author_email"]]  # Use first author for sharing

                for space_name in space_names:
                    space = space_map[space_name]
                    # Use SpaceService to share article
                    await SpaceService.share_article(
                        db=db,
                        space_id=space.id,
                        article_id=article.id,
                        user_id=author.id
                    )
                    total_shares += 1

            print(f"   ✅ Shared articles {total_shares} times")

            await db.commit()
            print("✨ Demo data creation completed successfully!")

            # Print summary
            print("\n📊 Demo Data Summary:")
            print(f"   👥 Users: {len(DEMO_USERS)}")
            print(f"   📝 Articles: {len(DEMO_ARTICLES)}")
            print(f"   🏠 Spaces: {len(DEMO_SPACES)}")
            print(f"   🤝 Memberships: {total_memberships}")
            print(f"   📤 Article Shares: {total_shares}")

            print("\n🔑 Demo Login Credentials:")
            print("   Password for all users: demopassword123")
            print("   Users:")
            for user_data in DEMO_USERS:
                print(f"   • {user_data['email']} ({user_data['display_name']})")

        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating demo data: {e}")
            raise
        finally:
            await engine.dispose()


async def clear_demo_data():
    """Clear all demo data."""
    print("🧹 Clearing existing demo data...")

    engine = create_async_engine(settings.async_database_url)
    async_session = async_sessionmaker(bind=engine)

    async with async_session() as db:
        try:
            # Clear in reverse dependency order
            await db.execute(text("DELETE FROM space_articles"))
            await db.execute(text("DELETE FROM space_members"))
            await db.execute(text("DELETE FROM activities"))
            await db.execute(text("DELETE FROM spaces"))
            await db.execute(text("DELETE FROM articles"))
            await db.execute(text("DELETE FROM oauth_accounts"))
            await db.execute(text("DELETE FROM user_preferences"))
            await db.execute(text("DELETE FROM users WHERE email LIKE '%@example.com'"))

            await db.commit()
            print("   ✅ Demo data cleared")

        except Exception as e:
            await db.rollback()
            print(f"❌ Error clearing demo data: {e}")
            raise
        finally:
            await engine.dispose()


async def main():
    """Main function to create demo data."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        await clear_demo_data()
    else:
        await clear_demo_data()  # Clear first
        await create_demo_data()


if __name__ == "__main__":
    asyncio.run(main())