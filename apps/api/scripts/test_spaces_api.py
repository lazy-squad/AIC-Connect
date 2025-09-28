#!/usr/bin/env python3
"""Test script for Spaces API endpoints."""

import asyncio
import httpx
import json
from typing import Dict, Any


BASE_URL = "http://localhost:4000"
DEMO_USER = {
    "email": "alice@example.com",
    "password": "demopassword123"
}


class SpacesAPITester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL)
        self.session_cookie = None

    async def login(self) -> bool:
        """Login and get session cookie."""
        try:
            response = await self.client.post("/api/auth/login", json=DEMO_USER)
            if response.status_code == 200:
                # Get session cookie from response
                cookies = response.cookies
                self.session_cookie = cookies.get("session")
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    async def test_list_spaces(self) -> bool:
        """Test listing all spaces."""
        try:
            response = await self.client.get("/api/spaces")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Listed {len(data['spaces'])} spaces")
                return True
            else:
                print(f"❌ List spaces failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ List spaces error: {e}")
            return False

    async def test_get_space(self, slug: str) -> bool:
        """Test getting a specific space."""
        try:
            response = await self.client.get(f"/api/spaces/{slug}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Retrieved space: {data['name']}")
                return True
            else:
                print(f"❌ Get space failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Get space error: {e}")
            return False

    async def test_create_space(self) -> str | None:
        """Test creating a new space."""
        space_data = {
            "name": "Test Space API Demo",
            "description": "A space created by the API test script",
            "tags": ["Testing", "API"],
            "visibility": "public"
        }

        try:
            headers = {"Cookie": f"session={self.session_cookie}"} if self.session_cookie else {}
            response = await self.client.post("/api/spaces", json=space_data, headers=headers)

            if response.status_code == 201:
                data = response.json()
                print(f"✅ Created space: {data['name']} (slug: {data['slug']})")
                return data['slug']
            else:
                print(f"❌ Create space failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Create space error: {e}")
            return None

    async def test_join_space(self, space_id: str) -> bool:
        """Test joining a space."""
        try:
            headers = {"Cookie": f"session={self.session_cookie}"} if self.session_cookie else {}
            response = await self.client.post(f"/api/spaces/{space_id}/join", headers=headers)

            if response.status_code == 200:
                print("✅ Joined space successfully")
                return True
            else:
                print(f"❌ Join space failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Join space error: {e}")
            return False

    async def test_my_spaces(self) -> bool:
        """Test listing user's spaces."""
        try:
            headers = {"Cookie": f"session={self.session_cookie}"} if self.session_cookie else {}
            response = await self.client.get("/api/spaces?my_spaces=true", headers=headers)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data['spaces'])} user spaces")
                return True
            else:
                print(f"❌ My spaces failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ My spaces error: {e}")
            return False

    async def test_search_spaces(self) -> bool:
        """Test searching spaces by tag."""
        try:
            response = await self.client.get("/api/spaces?tags=RAG")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data['spaces'])} spaces with RAG tag")
                return True
            else:
                print(f"❌ Search spaces failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Search spaces error: {e}")
            return False

    async def run_all_tests(self):
        """Run all API tests."""
        print("🧪 Testing Spaces API endpoints...")
        print("=" * 50)

        # Test without authentication first
        print("\n📋 Testing public endpoints:")
        await self.test_list_spaces()
        await self.test_search_spaces()
        await self.test_get_space("rag-enthusiasts")

        # Test with authentication
        print("\n🔐 Testing authenticated endpoints:")
        if await self.login():
            await self.test_my_spaces()

            # Create a test space
            test_slug = await self.test_create_space()

            # Test joining an existing space (use a demo space)
            print("\n🤝 Testing space membership:")
            await self.test_join_space("vector-database-deep-dive")

        print("\n" + "=" * 50)
        print("🎉 API testing completed!")

        await self.client.aclose()


async def main():
    """Main test function."""
    tester = SpacesAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("🚀 AIC Connect Spaces API Tester")
    print("Make sure the API server is running on http://localhost:4000")
    print("And that demo data has been created.\n")

    asyncio.run(main())