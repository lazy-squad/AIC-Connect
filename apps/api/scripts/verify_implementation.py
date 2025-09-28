#!/usr/bin/env python3
"""Verify that the Spaces implementation is working correctly."""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from aic_hub.config import settings


async def verify_database_tables():
    """Verify that all required tables exist."""
    print("🗃️  Verifying database tables...")

    engine = create_async_engine(settings.async_database_url)
    async_session = async_sessionmaker(bind=engine)

    required_tables = [
        "users",
        "articles",
        "spaces",
        "space_members",
        "space_articles",
        "activities",
        "user_preferences"
    ]

    try:
        async with async_session() as db:
            for table in required_tables:
                result = await db.execute(
                    text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                )
                exists = result.scalar()
                if exists:
                    print(f"   ✅ {table}")
                else:
                    print(f"   ❌ {table} - MISSING")
                    return False

        await engine.dispose()
        return True

    except Exception as e:
        print(f"   ❌ Database error: {e}")
        await engine.dispose()
        return False


async def verify_database_relationships():
    """Verify foreign key relationships are working."""
    print("\n🔗 Verifying database relationships...")

    engine = create_async_engine(settings.async_database_url)
    async_session = async_sessionmaker(bind=engine)

    try:
        async with async_session() as db:
            # Check spaces table structure
            result = await db.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'spaces'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()

            required_columns = {'id', 'name', 'slug', 'owner_id', 'visibility', 'tags'}
            found_columns = {col[0] for col in columns}

            if required_columns.issubset(found_columns):
                print("   ✅ Spaces table structure")
            else:
                missing = required_columns - found_columns
                print(f"   ❌ Spaces table missing columns: {missing}")
                return False

            # Check foreign key constraints
            result = await db.execute(text("""
                SELECT tc.table_name, tc.constraint_name, kcu.column_name, ccu.table_name AS foreign_table_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_name IN ('spaces', 'space_members', 'space_articles')
            """))

            fks = result.fetchall()
            if len(fks) >= 5:  # Expected at least 5 foreign keys
                print("   ✅ Foreign key constraints")
            else:
                print(f"   ❌ Only found {len(fks)} foreign keys, expected at least 5")
                return False

        await engine.dispose()
        return True

    except Exception as e:
        print(f"   ❌ Relationship verification error: {e}")
        await engine.dispose()
        return False


async def verify_models_import():
    """Verify that all models can be imported."""
    print("\n📦 Verifying model imports...")

    try:
        from aic_hub.models import Space, SpaceArticle, space_members, Article, User, Activity
        print("   ✅ All models import successfully")

        # Check model attributes
        space_attrs = {'id', 'name', 'slug', 'owner_id', 'members', 'space_articles'}
        if space_attrs.issubset(set(dir(Space))):
            print("   ✅ Space model attributes")
        else:
            print("   ❌ Space model missing attributes")
            return False

        return True

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False


async def verify_services_import():
    """Verify that services can be imported and have required methods."""
    print("\n🔧 Verifying service imports...")

    try:
        from aic_hub.services import SpaceService, ActivityService
        print("   ✅ Services import successfully")

        # Check SpaceService methods
        required_methods = {
            'create_space', 'join_space', 'leave_space', 'share_article',
            'list_spaces', 'get_space_by_slug', 'update_space', 'delete_space'
        }

        space_methods = set(dir(SpaceService))
        if required_methods.issubset(space_methods):
            print("   ✅ SpaceService has all required methods")
        else:
            missing = required_methods - space_methods
            print(f"   ❌ SpaceService missing methods: {missing}")
            return False

        return True

    except ImportError as e:
        print(f"   ❌ Service import error: {e}")
        return False


async def verify_api_routes():
    """Verify that API routes are registered."""
    print("\n🌐 Verifying API routes...")

    try:
        from aic_hub.main import app

        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append((route.path, route.methods))

        # Check for spaces routes
        spaces_routes = [r for r in routes if '/spaces' in r[0]]

        expected_routes = [
            '/api/spaces',
            '/api/spaces/{slug}',
            '/api/spaces/{id}',
            '/api/spaces/{id}/join',
            '/api/spaces/{id}/leave',
            '/api/spaces/{id}/members',
            '/api/spaces/{id}/articles'
        ]

        found_routes = [r[0] for r in spaces_routes]

        if len(spaces_routes) >= 7:  # We expect at least 7 space-related routes
            print(f"   ✅ Found {len(spaces_routes)} spaces routes")
        else:
            print(f"   ❌ Only found {len(spaces_routes)} spaces routes, expected at least 7")
            print(f"   Found: {found_routes}")
            return False

        return True

    except Exception as e:
        print(f"   ❌ Route verification error: {e}")
        return False


async def verify_schemas():
    """Verify that Pydantic schemas are properly defined."""
    print("\n📋 Verifying schemas...")

    try:
        from aic_hub.schemas import (
            SpaceCreate, SpaceUpdate, Space, SpaceSummary,
            SpaceMember, SpaceArticle, SpaceListResponse
        )
        print("   ✅ All schemas import successfully")

        # Test schema creation
        space_create = SpaceCreate(
            name="Test Space",
            description="Test description",
            tags=["test"],
            visibility="public"
        )
        print("   ✅ SpaceCreate schema works")

        return True

    except Exception as e:
        print(f"   ❌ Schema verification error: {e}")
        return False


async def check_demo_data():
    """Check if demo data exists."""
    print("\n🎭 Checking demo data...")

    engine = create_async_engine(settings.async_database_url)
    async_session = async_sessionmaker(bind=engine)

    try:
        async with async_session() as db:
            # Check for demo users
            result = await db.execute(text("SELECT COUNT(*) FROM users WHERE email LIKE '%@example.com'"))
            user_count = result.scalar()

            # Check for demo spaces
            result = await db.execute(text("SELECT COUNT(*) FROM spaces"))
            space_count = result.scalar()

            # Check for demo articles
            result = await db.execute(text("SELECT COUNT(*) FROM articles"))
            article_count = result.scalar()

            if user_count > 0 and space_count > 0:
                print(f"   ✅ Found {user_count} demo users, {space_count} spaces, {article_count} articles")
                return True
            else:
                print(f"   ⚠️  Demo data not found. Run 'pnpm demo:setup' to create it.")
                print(f"      Users: {user_count}, Spaces: {space_count}, Articles: {article_count}")
                return False

        await engine.dispose()

    except Exception as e:
        print(f"   ❌ Demo data check error: {e}")
        await engine.dispose()
        return False


async def main():
    """Run all verification checks."""
    print("🔍 AIC Connect Spaces Implementation Verification")
    print("=" * 60)

    checks = [
        ("Database Tables", verify_database_tables),
        ("Database Relationships", verify_database_relationships),
        ("Model Imports", verify_models_import),
        ("Service Imports", verify_services_import),
        ("API Routes", verify_api_routes),
        ("Schemas", verify_schemas),
        ("Demo Data", check_demo_data),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = await check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ {name} check failed with exception: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)

    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {name}")
        if result:
            passed += 1

    print(f"\nResult: {passed}/{len(results)} checks passed")

    if passed == len(results):
        print("\n🎉 All checks passed! The Spaces implementation is ready.")
        print("\nNext steps:")
        print("1. Start the development server: pnpm dev")
        print("2. Create demo data: pnpm demo:setup")
        print("3. Test the API: cd apps/api && uv run python scripts/test_spaces_api.py")
        print("4. Visit http://localhost:3000 and explore the Spaces feature!")
    else:
        print(f"\n⚠️  {len(results) - passed} checks failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())