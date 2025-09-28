#!/usr/bin/env python3
"""
Demo Data Seeder for AIC Hub

Creates rich sample data including diverse user profiles with realistic
GitHub-style data for demonstration purposes.
"""

import asyncio
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.aic_hub.constants import AI_TAGS
from src.aic_hub.db import get_engine
from src.aic_hub.models import User
from src.aic_hub.security import hash_password

# Sample user data with diverse profiles
SAMPLE_USERS = [
    {
        "email": "sarah.chen@example.com",
        "display_name": "Sarah Chen",
        "username": "sarahchen",
        "github_username": "sarahchen",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345?v=4",
        "bio": "AI researcher working on multimodal LLMs and responsible AI. Former OpenAI, now building ethical AI systems.",
        "company": "Anthropic",
        "location": "San Francisco, CA",
        "expertise_tags": ["LLMs", "Ethics", "Safety", "NLP"],
        "password": "demo123"
    },
    {
        "email": "alex.rivera@example.com",
        "display_name": "Alex Rivera",
        "username": "alexrivera",
        "github_username": "alex-rivera",
        "avatar_url": "https://avatars.githubusercontent.com/u/23456?v=4",
        "bio": "Building the next generation of RAG systems. Open source contributor to LangChain and vector databases.",
        "company": "Pinecone",
        "location": "New York, NY",
        "expertise_tags": ["RAG", "Vector DBs", "Embeddings", "Tools"],
        "password": "demo123"
    },
    {
        "email": "yuki.tanaka@example.com",
        "display_name": "Yuki Tanaka",
        "username": "yukitanaka",
        "github_username": "yuki-tanaka",
        "avatar_url": "https://avatars.githubusercontent.com/u/34567?v=4",
        "bio": "Computer vision researcher specializing in autonomous driving. PhD from MIT, 10+ papers on perception systems.",
        "company": "Waymo",
        "location": "Tokyo, Japan",
        "expertise_tags": ["Computer Vision", "Robotics", "Training", "Datasets"],
        "password": "demo123"
    },
    {
        "email": "marcus.johnson@example.com",
        "display_name": "Marcus Johnson",
        "username": "marcusj",
        "github_username": "marcus-johnson",
        "avatar_url": "https://avatars.githubusercontent.com/u/45678?v=4",
        "bio": "AI agent architect and prompt engineering expert. Building autonomous systems that can reason and plan.",
        "company": "DeepMind",
        "location": "London, UK",
        "expertise_tags": ["Agents", "Prompting", "RL", "LLMs"],
        "password": "demo123"
    },
    {
        "email": "priya.patel@example.com",
        "display_name": "Dr. Priya Patel",
        "username": "priyapatel",
        "github_username": "priya-patel",
        "avatar_url": "https://avatars.githubusercontent.com/u/56789?v=4",
        "bio": "NLP researcher and startup founder. Building conversational AI for healthcare. Former Google Brain.",
        "company": "HealthTalk AI",
        "location": "Bangalore, India",
        "expertise_tags": ["NLP", "LLMs", "Ethics", "Fine-tuning"],
        "password": "demo123"
    },
    {
        "email": "david.kim@example.com",
        "display_name": "David Kim",
        "username": "davidkim",
        "github_username": "david-kim-ml",
        "avatar_url": "https://avatars.githubusercontent.com/u/67890?v=4",
        "bio": "MLOps engineer focused on model training infrastructure. Scaling AI training from 0 to production.",
        "company": "Scale AI",
        "location": "Seattle, WA",
        "expertise_tags": ["Training", "Inference", "Tools", "Datasets"],
        "password": "demo123"
    },
    {
        "email": "elena.volkov@example.com",
        "display_name": "Elena Volkov",
        "username": "elenav",
        "github_username": "elena-volkov",
        "avatar_url": "https://avatars.githubusercontent.com/u/78901?v=4",
        "bio": "AI safety researcher and alignment theorist. Working on making AGI beneficial for humanity.",
        "company": "Alignment Research Center",
        "location": "Oxford, UK",
        "expertise_tags": ["Safety", "Ethics", "LLMs", "Benchmarks"],
        "password": "demo123"
    },
    {
        "email": "carlos.mendoza@example.com",
        "display_name": "Carlos Mendoza",
        "username": "carlosm",
        "github_username": "carlos-mendoza",
        "avatar_url": "https://avatars.githubusercontent.com/u/89012?v=4",
        "bio": "Fine-tuning specialist and dataset curator. Created 50+ specialized models for various industries.",
        "company": "Hugging Face",
        "location": "Barcelona, Spain",
        "expertise_tags": ["Fine-tuning", "Datasets", "LLMs", "Tools"],
        "password": "demo123"
    },
    {
        "email": "aisha.okonkwo@example.com",
        "display_name": "Aisha Okonkwo",
        "username": "aishao",
        "github_username": "aisha-okonkwo",
        "avatar_url": "https://avatars.githubusercontent.com/u/90123?v=4",
        "bio": "Speech recognition expert building voice interfaces for African languages. Democratizing AI access.",
        "company": "Mozilla",
        "location": "Lagos, Nigeria",
        "expertise_tags": ["Speech", "NLP", "Ethics", "Datasets"],
        "password": "demo123"
    },
    {
        "email": "jin.wang@example.com",
        "display_name": "Jin Wang",
        "username": "jinwang",
        "github_username": "jin-wang-ai",
        "avatar_url": "https://avatars.githubusercontent.com/u/01234?v=4",
        "bio": "Robotics engineer integrating AI with physical systems. Building the future of human-robot collaboration.",
        "company": "Boston Dynamics",
        "location": "Boston, MA",
        "expertise_tags": ["Robotics", "RL", "Computer Vision", "Training"],
        "password": "demo123"
    },
    {
        "email": "lisa.zhang@example.com",
        "display_name": "Lisa Zhang",
        "username": "lisazhang",
        "github_username": "lisa-zhang",
        "avatar_url": "https://avatars.githubusercontent.com/u/11111?v=4",
        "bio": "AI tools and frameworks developer. Making AI accessible to developers worldwide through better APIs.",
        "company": "OpenAI",
        "location": "San Francisco, CA",
        "expertise_tags": ["Tools", "LLMs", "Inference", "Embeddings"],
        "password": "demo123"
    },
    {
        "email": "ahmed.hassan@example.com",
        "display_name": "Ahmed Hassan",
        "username": "ahmedh",
        "github_username": "ahmed-hassan",
        "avatar_url": "https://avatars.githubusercontent.com/u/22222?v=4",
        "bio": "AI benchmarking and evaluation expert. Creating standards for measuring AI progress and capabilities.",
        "company": "AI21 Labs",
        "location": "Tel Aviv, Israel",
        "expertise_tags": ["Benchmarks", "Datasets", "LLMs", "Safety"],
        "password": "demo123"
    },
    {
        "email": "sophie.martin@example.com",
        "display_name": "Sophie Martin",
        "username": "sophiem",
        "github_username": "sophie-martin",
        "avatar_url": "https://avatars.githubusercontent.com/u/33333?v=4",
        "bio": "Independent AI consultant helping startups integrate LLMs. Former tech lead at multiple unicorns.",
        "company": "Freelance",
        "location": "Paris, France",
        "expertise_tags": ["LLMs", "Fine-tuning", "Tools", "Prompting"],
        "password": "demo123"
    },
    {
        "email": "raj.gupta@example.com",
        "display_name": "Raj Gupta",
        "username": "rajgupta",
        "github_username": "raj-gupta",
        "avatar_url": "https://avatars.githubusercontent.com/u/44444?v=4",
        "bio": "PhD student researching multimodal foundation models. Bridging the gap between vision and language.",
        "company": "Stanford University",
        "location": "Palo Alto, CA",
        "expertise_tags": ["Computer Vision", "NLP", "LLMs", "Training"],
        "password": "demo123"
    },
    {
        "email": "maria.silva@example.com",
        "display_name": "Maria Silva",
        "username": "mariasilva",
        "github_username": "maria-silva",
        "avatar_url": "https://avatars.githubusercontent.com/u/55555?v=4",
        "bio": "AI product manager with technical background. Shipped 3 major AI products used by millions.",
        "company": "Microsoft",
        "location": "São Paulo, Brazil",
        "expertise_tags": ["LLMs", "Tools", "Ethics", "Inference"],
        "password": "demo123"
    }
]


async def create_demo_users():
    """Create demo users with realistic profiles."""

    engine = get_engine()
    async_session = async_sessionmaker(engine)

    async with async_session() as session:
        # Check if demo users already exist
        existing_users = await session.execute(
            select(User).where(User.email.in_([user["email"] for user in SAMPLE_USERS]))
        )
        existing_emails = {user.email for user in existing_users.scalars().all()}

        created_count = 0
        updated_count = 0

        for user_data in SAMPLE_USERS:
            email = user_data["email"]

            if email in existing_emails:
                print(f"User {email} already exists, skipping...")
                continue

            # Hash the demo password
            password_hash = hash_password(user_data["password"])

            # Create user with profile data
            user = User(
                id=uuid.uuid4(),
                email=email,
                password_hash=password_hash,
                display_name=user_data["display_name"],
                username=user_data["username"],
                github_username=user_data.get("github_username"),
                avatar_url=user_data.get("avatar_url"),
                bio=user_data.get("bio"),
                company=user_data.get("company"),
                location=user_data.get("location"),
                expertise_tags=user_data.get("expertise_tags", []),
                created_at=datetime.utcnow() - timedelta(days=30, hours=created_count * 2),  # Stagger creation times
            )

            session.add(user)
            created_count += 1
            print(f"Created user: {user_data['display_name']} ({email})")

        # Commit all changes
        await session.commit()

        print(f"\n✅ Demo data creation complete!")
        print(f"   Created: {created_count} new users")
        print(f"   Skipped: {len(existing_emails)} existing users")

        # Display summary of expertise distribution
        all_tags = []
        for user_data in SAMPLE_USERS:
            all_tags.extend(user_data.get("expertise_tags", []))

        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        print(f"\n📊 Expertise Tag Distribution:")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {tag}: {count} users")

    await engine.dispose()


async def clean_demo_data():
    """Remove all demo users (for testing purposes)."""

    engine = get_engine()
    async_session = async_sessionmaker(engine)

    async with async_session() as session:
        # Delete users by email
        demo_emails = [user["email"] for user in SAMPLE_USERS]

        result = await session.execute(
            select(User).where(User.email.in_(demo_emails))
        )
        users_to_delete = result.scalars().all()

        for user in users_to_delete:
            session.delete(user)
            print(f"Deleted user: {user.display_name} ({user.email})")

        await session.commit()
        print(f"\n🗑️  Cleaned {len(users_to_delete)} demo users")

    await engine.dispose()


async def show_demo_stats():
    """Show statistics about the demo data."""

    engine = get_engine()
    async_session = async_sessionmaker(engine)

    async with async_session() as session:
        # Get all users
        result = await session.execute(select(User))
        all_users = result.scalars().all()

        # Get demo users
        demo_emails = [user["email"] for user in SAMPLE_USERS]
        demo_result = await session.execute(
            select(User).where(User.email.in_(demo_emails))
        )
        demo_users = demo_result.scalars().all()

        print(f"📈 Database Statistics:")
        print(f"   Total users: {len(all_users)}")
        print(f"   Demo users: {len(demo_users)}")
        print(f"   Other users: {len(all_users) - len(demo_users)}")

        # Company distribution
        companies = {}
        for user in demo_users:
            if user.company:
                companies[user.company] = companies.get(user.company, 0) + 1

        print(f"\n🏢 Company Distribution:")
        for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True):
            print(f"   {company}: {count} users")

        # Location distribution
        locations = {}
        for user in demo_users:
            if user.location:
                locations[user.location] = locations.get(user.location, 0) + 1

        print(f"\n🌍 Location Distribution:")
        for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True):
            print(f"   {location}: {count} users")

    await engine.dispose()


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("🚀 AIC Hub Demo Data Manager")
    print("=" * 60)

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "create":
            print("🌱 Creating demo data...")
            asyncio.run(create_demo_users())
        elif command == "clean":
            print("🗑️  Cleaning demo data...")
            asyncio.run(clean_demo_data())
        elif command == "stats":
            print("📊 Showing demo statistics...")
            asyncio.run(show_demo_stats())
        else:
            print("\n❌ Invalid command!")
            print("\nUsage:")
            print("  python seed_demo_data.py create  - Create demo users")
            print("  python seed_demo_data.py clean   - Remove demo users")
            print("  python seed_demo_data.py stats   - Show statistics")
            print("  python seed_demo_data.py         - Create demo users (default)")
    else:
        print("🌱 Creating demo data...")
        asyncio.run(create_demo_users())