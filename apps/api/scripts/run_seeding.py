#!/usr/bin/env python3
"""
Simple runner script for seeding demo data.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

async def main():
    """Run all seeding scripts."""
    print("🌱 Starting AIC Hub demo data seeding...")

    try:
        # Import and run article seeding
        from seed_articles_data import main as seed_articles
        await seed_articles()

        print("\n✅ Demo data seeding completed successfully!")
        print("\n📝 Sample data created:")
        print("  • 5 sample users with diverse AI expertise")
        print("  • 5 published articles covering different AI topics")
        print("  • 2 draft articles for testing draft functionality")
        print("  • Realistic view counts and engagement metrics")

        print("\n🚀 You can now:")
        print("  • Browse articles at /articles")
        print("  • View individual articles by slug")
        print("  • Test article creation and editing")
        print("  • Explore tag-based filtering")
        print("  • Check out user drafts")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())