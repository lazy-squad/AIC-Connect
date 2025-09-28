#!/usr/bin/env python
"""Create rich sample data for AIC Hub demo."""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from aic_hub.db import lifespan_session
from aic_hub.models import Article, Space, User, space_members
from aic_hub.services.tag_service import TagService
from aic_hub.services.search_service import SearchService
from aic_hub.constants import AI_TAGS


# Sample users with AI expertise
DEMO_USERS = [
    {
        "email": "alex.rag@airesearch.com",
        "display_name": "Alex Chen",
        "username": "alexchen",
        "github_username": "alexchen-rag",
        "bio": "AI Research Scientist specializing in Retrieval-Augmented Generation and Large Language Models. 5+ years building production RAG systems.",
        "company": "AI Research Lab",
        "location": "San Francisco, CA",
        "expertise_tags": ["RAG", "LLMs", "Vector DBs", "Embeddings", "Fine-tuning"],
        "avatar_url": "https://avatars.githubusercontent.com/u/1234567?v=4"
    },
    {
        "email": "sarah.agents@tech.ai",
        "display_name": "Sarah Rodriguez",
        "username": "sarodriguez",
        "github_username": "sarah-agents",
        "bio": "AI Engineer focused on autonomous agents and multi-agent systems. Building the future of AI automation.",
        "company": "TechAI Inc",
        "location": "New York, NY",
        "expertise_tags": ["Agents", "Tools", "Prompting", "LLMs"],
        "avatar_url": "https://avatars.githubusercontent.com/u/2345678?v=4"
    },
    {
        "email": "mike.vision@deeptech.com",
        "display_name": "Mike Thompson",
        "username": "mikethompson",
        "github_username": "mike-cv",
        "bio": "Computer Vision expert with deep learning background. Working on multimodal AI systems and vision-language models.",
        "company": "DeepTech Solutions",
        "location": "Austin, TX",
        "expertise_tags": ["Computer Vision", "Training", "Datasets", "Inference"],
        "avatar_url": "https://avatars.githubusercontent.com/u/3456789?v=4"
    },
    {
        "email": "lisa.nlp@stanford.edu",
        "display_name": "Dr. Lisa Wang",
        "username": "lisawang",
        "github_username": "lisa-nlp",
        "bio": "NLP Research Professor at Stanford. Expert in natural language understanding, prompt engineering, and AI safety.",
        "company": "Stanford University",
        "location": "Palo Alto, CA",
        "expertise_tags": ["NLP", "Prompting", "Safety", "Ethics", "Benchmarks"],
        "avatar_url": "https://avatars.githubusercontent.com/u/4567890?v=4"
    },
    {
        "email": "david.robotics@mit.edu",
        "display_name": "David Kim",
        "username": "davidkim",
        "github_username": "david-robotics",
        "bio": "Robotics researcher combining reinforcement learning with computer vision for embodied AI systems.",
        "company": "MIT CSAIL",
        "location": "Cambridge, MA",
        "expertise_tags": ["Robotics", "RL", "Computer Vision", "Training"],
        "avatar_url": "https://avatars.githubusercontent.com/u/5678901?v=4"
    },
    {
        "email": "anna.tools@openai.com",
        "display_name": "Anna Kowalski",
        "username": "annakowalski",
        "github_username": "anna-tools",
        "bio": "AI Tools Engineer at OpenAI. Building developer tools and frameworks for AI applications.",
        "company": "OpenAI",
        "location": "San Francisco, CA",
        "expertise_tags": ["Tools", "Inference", "Fine-tuning", "LLMs"],
        "avatar_url": "https://avatars.githubusercontent.com/u/6789012?v=4"
    }
]

# Sample spaces
DEMO_SPACES = [
    {
        "name": "RAG Systems",
        "slug": "rag-systems",
        "description": "Community for discussing Retrieval-Augmented Generation architectures, best practices, and implementations. Share your RAG experiments and learn from others.",
        "tags": ["RAG", "Vector DBs", "Embeddings", "LLMs"],
        "visibility": "public",
        "owner_username": "alexchen"
    },
    {
        "name": "AI Agents Hub",
        "slug": "ai-agents-hub",
        "description": "Exploring autonomous AI agents, multi-agent systems, and tool-using AI. Discuss frameworks, architectures, and real-world applications.",
        "tags": ["Agents", "Tools", "Prompting"],
        "visibility": "public",
        "owner_username": "sarodriguez"
    },
    {
        "name": "Computer Vision Research",
        "slug": "cv-research",
        "description": "Latest developments in computer vision, multimodal AI, and vision-language models. Academic and industry perspectives welcome.",
        "tags": ["Computer Vision", "Training", "Datasets"],
        "visibility": "public",
        "owner_username": "mikethompson"
    },
    {
        "name": "AI Safety & Ethics",
        "slug": "ai-safety-ethics",
        "description": "Discussing responsible AI development, safety measures, alignment research, and ethical considerations in AI systems.",
        "tags": ["Safety", "Ethics", "Benchmarks"],
        "visibility": "public",
        "owner_username": "lisawang"
    },
    {
        "name": "Embodied AI Lab",
        "slug": "embodied-ai-lab",
        "description": "Robotics meets AI. Exploring embodied intelligence, robot learning, and physical AI systems.",
        "tags": ["Robotics", "RL", "Computer Vision"],
        "visibility": "public",
        "owner_username": "davidkim"
    },
    {
        "name": "AI Engineering Tools",
        "slug": "ai-engineering-tools",
        "description": "Developer tools, frameworks, and infrastructure for building AI applications. Focus on production deployment and MLOps.",
        "tags": ["Tools", "Inference", "Training"],
        "visibility": "public",
        "owner_username": "annakowalski"
    }
]

# Sample articles with rich content
DEMO_ARTICLES = [
    {
        "title": "Building Production RAG Systems: Lessons from the Trenches",
        "summary": "After building 5+ RAG systems in production, here are the key lessons learned about vector databases, embedding strategies, and retrieval optimization.",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Introduction"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Retrieval-Augmented Generation (RAG) has become the go-to architecture for building AI applications that need to ground their responses in external knowledge. However, moving from prototype to production reveals numerous challenges that aren't apparent in simple demos."}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Vector Database Selection"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "The choice of vector database significantly impacts both performance and cost. We've tested Pinecone, Weaviate, and Qdrant across different scales:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Pinecone: Best for rapid prototyping and scaling"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Weaviate: Excellent for complex filtering and hybrid search"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Qdrant: Cost-effective for self-hosted deployments"}]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Embedding Strategy"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "The embedding model choice is crucial. We found that domain-specific fine-tuning of models like BGE or E5 often outperforms generic models like OpenAI's text-embedding-ada-002, especially for technical content."}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Retrieval Optimization"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Key optimizations that made a significant difference:"}
                    ]
                },
                {
                    "type": "orderedList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Hybrid search combining semantic and keyword search"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Query rewriting and expansion"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Metadata filtering for relevance"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Re-ranking with cross-encoders"}]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Conclusion"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Building production RAG systems requires careful consideration of the entire pipeline. Focus on evaluation metrics early, and don't underestimate the importance of data quality and preprocessing."}
                    ]
                }
            ]
        },
        "tags": ["RAG", "Vector DBs", "Embeddings", "LLMs"],
        "author_username": "alexchen",
        "published": True,
        "days_ago": 2
    },
    {
        "title": "Multi-Agent Systems: Orchestrating AI Collaboration",
        "summary": "Exploring patterns and frameworks for building systems where multiple AI agents work together to solve complex tasks through coordination and communication.",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Multi-agent systems represent a paradigm shift from single-agent AI applications to collaborative networks of specialized agents working together."}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Agent Patterns"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "We've identified several successful patterns for agent collaboration:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Supervisor-Worker: Central coordinator delegates tasks"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Pipeline: Sequential processing with handoffs"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Marketplace: Agents bid for tasks based on capabilities"}]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "tags": ["Agents", "Tools", "Prompting"],
        "author_username": "sarodriguez",
        "published": True,
        "days_ago": 5
    },
    {
        "title": "Vision-Language Models: Bridging Pixels and Text",
        "summary": "A deep dive into multimodal AI systems that understand both images and text, covering architectures, training techniques, and practical applications.",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Vision-language models have revolutionized how AI systems understand and generate content across modalities. This article explores the key architectures and training techniques."}
                    ]
                }
            ]
        },
        "tags": ["Computer Vision", "NLP", "Training", "Datasets"],
        "author_username": "mikethompson",
        "published": True,
        "days_ago": 7
    },
    {
        "title": "Prompt Engineering: From Art to Science",
        "summary": "Systematic approaches to prompt engineering, including techniques for few-shot learning, chain-of-thought reasoning, and prompt optimization.",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Prompt engineering has evolved from trial-and-error to systematic methodologies. Here's a comprehensive guide to modern prompting techniques."}
                    ]
                }
            ]
        },
        "tags": ["Prompting", "LLMs", "Fine-tuning"],
        "author_username": "lisawang",
        "published": True,
        "days_ago": 3
    },
    {
        "title": "AI Safety in Production: Monitoring and Guardrails",
        "summary": "Practical approaches to implementing AI safety measures in production systems, including monitoring, content filtering, and bias detection.",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "As AI systems become more powerful and widespread, implementing robust safety measures becomes critical. This article covers practical safety implementations."}
                    ]
                }
            ]
        },
        "tags": ["Safety", "Ethics", "Benchmarks", "Tools"],
        "author_username": "lisawang",
        "published": True,
        "days_ago": 1
    },
    {
        "title": "Reinforcement Learning for Robotics: Real-World Challenges",
        "summary": "Exploring the challenges and solutions in applying RL to real-world robotics, including sim-to-real transfer and safety considerations.",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Applying reinforcement learning to robotics presents unique challenges not found in simulated environments. This article explores practical solutions."}
                    ]
                }
            ]
        },
        "tags": ["Robotics", "RL", "Training", "Safety"],
        "author_username": "davidkim",
        "published": True,
        "days_ago": 4
    },
    {
        "title": "Building AI Tools: Developer Experience Matters",
        "summary": "Lessons learned from building developer tools for AI applications, focusing on APIs, SDKs, and developer experience design.",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Great AI tools require more than just powerful models - they need excellent developer experience. Here's what we've learned building tools at OpenAI."}
                    ]
                }
            ]
        },
        "tags": ["Tools", "Inference", "Fine-tuning"],
        "author_username": "annakowalski",
        "published": True,
        "days_ago": 6
    },
    {
        "title": "Vector Database Performance: Scaling to Billions",
        "summary": "Performance optimization techniques for vector databases at scale, including indexing strategies, memory management, and distributed architectures.",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "As vector databases grow to billions of embeddings, performance optimization becomes crucial. This article covers advanced scaling techniques."}
                    ]
                }
            ]
        },
        "tags": ["Vector DBs", "Embeddings", "Inference"],
        "author_username": "alexchen",
        "published": True,
        "days_ago": 8
    },
    {
        "title": "The Future of Speech AI: Beyond Transcription",
        "summary": "Exploring advanced speech AI applications including real-time translation, voice cloning, and multimodal speech understanding.",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Speech AI has evolved far beyond simple transcription. This article explores the cutting-edge applications and future possibilities."}
                    ]
                }
            ]
        },
        "tags": ["Speech", "NLP", "Training"],
        "author_username": "mikethompson",
        "published": True,
        "days_ago": 10
    },
    {
        "title": "Fine-tuning LLMs: A Practitioner's Guide",
        "summary": "Comprehensive guide to fine-tuning large language models, covering data preparation, training strategies, and evaluation methods.",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Fine-tuning large language models requires careful consideration of data, compute, and evaluation. This guide covers everything you need to know."}
                    ]
                }
            ]
        },
        "tags": ["Fine-tuning", "LLMs", "Training", "Datasets"],
        "author_username": "annakowalski",
        "published": True,
        "days_ago": 9
    }
]


async def create_demo_data():
    """Create comprehensive demo data for the AIC Hub."""
    async with lifespan_session() as db:
        print("🚀 Creating demo data for AIC Hub...")

        # Create users
        print("\n👥 Creating demo users...")
        users_map = {}

        for user_data in DEMO_USERS:
            user = User(
                id=uuid4(),
                email=user_data["email"],
                display_name=user_data["display_name"],
                username=user_data["username"],
                github_username=user_data["github_username"],
                bio=user_data["bio"],
                company=user_data["company"],
                location=user_data["location"],
                expertise_tags=user_data["expertise_tags"],
                avatar_url=user_data["avatar_url"],
                created_at=datetime.now(timezone.utc) - timedelta(days=30),
                password_hash=None  # OAuth only users
            )
            db.add(user)
            users_map[user_data["username"]] = user
            print(f"   ✅ Created user: {user.display_name} (@{user.username})")

        await db.commit()

        # Update tag usage for user expertise
        print("\n🏷️  Updating tag usage for user expertise...")
        for user in users_map.values():
            if user.expertise_tags:
                for tag in user.expertise_tags:
                    await TagService.update_tag_usage(db, tag, "user", delta=1)
                print(f"   ✅ Updated tags for {user.display_name}: {', '.join(user.expertise_tags)}")

        # Create spaces
        print("\n🏢 Creating demo spaces...")
        spaces_map = {}

        for space_data in DEMO_SPACES:
            owner = users_map[space_data["owner_username"]]
            space = Space(
                id=uuid4(),
                name=space_data["name"],
                slug=space_data["slug"],
                description=space_data["description"],
                tags=space_data["tags"],
                visibility=space_data["visibility"],
                owner_id=owner.id,
                member_count=1,
                article_count=0,
                created_at=datetime.now(timezone.utc) - timedelta(days=25)
            )
            db.add(space)
            spaces_map[space_data["slug"]] = space
            print(f"   ✅ Created space: {space.name}")

        await db.flush()

        # Add owners as members
        for space_data in DEMO_SPACES:
            space = spaces_map[space_data["slug"]]
            owner = users_map[space_data["owner_username"]]

            await db.execute(
                space_members.insert().values(
                    space_id=space.id,
                    user_id=owner.id,
                    role="owner"
                )
            )

        await db.commit()

        # Update tag usage and search index for spaces
        print("\n🔍 Updating search index for spaces...")
        for space in spaces_map.values():
            if space.visibility == "public" and space.tags:
                for tag in space.tags:
                    await TagService.update_tag_usage(db, tag, "space", delta=1)

                await SearchService.update_search_index(
                    db=db,
                    entity_type="space",
                    entity_id=space.id,
                    title=space.name,
                    content=space.description or "",
                    tags=space.tags
                )
            print(f"   ✅ Indexed space: {space.name}")

        # Create articles
        print("\n📝 Creating demo articles...")

        for article_data in DEMO_ARTICLES:
            author = users_map[article_data["author_username"]]

            # Generate unique slug
            base_slug = article_data["title"].lower().replace(" ", "-").replace(":", "").replace(",", "")
            base_slug = "".join(c for c in base_slug if c.isalnum() or c == "-")

            article = Article(
                id=uuid4(),
                title=article_data["title"],
                slug=base_slug,
                summary=article_data["summary"],
                content=json.dumps(article_data["content"]),
                tags=article_data["tags"],
                status="published" if article_data["published"] else "draft",
                author_id=author.id,
                view_count=0,
                like_count=0,
                published_at=datetime.now(timezone.utc) - timedelta(days=article_data["days_ago"]) if article_data["published"] else None,
                created_at=datetime.now(timezone.utc) - timedelta(days=article_data["days_ago"]),
                updated_at=None
            )
            db.add(article)
            print(f"   ✅ Created article: {article.title}")

        await db.commit()

        # Update tag usage and search index for published articles
        print("\n🔍 Updating search index for articles...")
        from sqlalchemy import select
        articles = await db.execute(select(Article).where(Article.status == "published"))

        for article in articles.scalars():
            if article.tags:
                for tag in article.tags:
                    await TagService.update_tag_usage(db, tag, "article", delta=1)

            await SearchService.update_search_index(
                db=db,
                entity_type="article",
                entity_id=article.id,
                title=article.title,
                content=article.summary or "",
                tags=article.tags
            )
            print(f"   ✅ Indexed article: {article.title}")

        # Calculate trending scores
        print("\n📈 Calculating trending scores...")
        await TagService.calculate_trending_scores(db)

        # Print summary
        print("\n" + "="*60)
        print("🎉 Demo data creation complete!")
        print("="*60)
        print(f"👥 Users created: {len(DEMO_USERS)}")
        print(f"🏢 Spaces created: {len(DEMO_SPACES)}")
        print(f"📝 Articles created: {len(DEMO_ARTICLES)}")
        print(f"🏷️  Tags in use: {len(AI_TAGS)}")
        print("\n💡 Try these demo scenarios:")
        print("   • Search for 'RAG systems' to find relevant content")
        print("   • Browse tags like 'LLMs', 'Agents', 'Computer Vision'")
        print("   • Explore spaces like 'RAG Systems' and 'AI Agents Hub'")
        print("   • Check user profiles with expertise tags")
        print("   • Test autocomplete with partial searches")
        print("\n🌟 The AIC Hub is ready for demo!")


if __name__ == "__main__":
    asyncio.run(create_demo_data())