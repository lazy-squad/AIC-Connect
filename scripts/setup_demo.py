#!/usr/bin/env python3
"""Setup demo data for AIC Connect."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'api', 'src'))

import asyncio
from apps.api.scripts.create_demo_data import create_demo_data, clear_demo_data


async def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        await clear_demo_data()
        print("✅ Demo data cleared!")
    else:
        print("🚀 Setting up demo data...")
        await clear_demo_data()
        await create_demo_data()
        print("🎉 Demo setup complete!")

        print("\n🌐 You can now:")
        print("   1. Start the development server: pnpm dev")
        print("   2. Visit http://localhost:3000")
        print("   3. Log in with any demo user (password: demopassword123)")
        print("   4. Explore the Spaces feature!")


if __name__ == "__main__":
    asyncio.run(main())