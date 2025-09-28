"""Feed service for generating personalized feeds and calculating trending content."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Activity, Article, Space, User, UserPreferences


class FeedService:
    """Service for managing feeds, trending content, and recommendations."""

    @staticmethod
    async def get_personalized_feed(
        db: AsyncSession,
        user_id: UUID | None,
        view: str = "latest",
        tags: List[str] | None = None,
        time_range: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Generate personalized feed based on user preferences.

        Args:
            db: Database session
            user_id: Current user ID
            view: Feed view type (latest, trending, following, recommended)
            tags: Filter by specific tags
            time_range: Time range for trending (24h, 7d, 30d, all)
            skip: Pagination offset
            limit: Page size

        Returns:
            Feed response with items, total count, and metadata
        """
        items = []
        total = 0

        if view == "latest":
            # Get latest published articles
            query = select(Article).where(Article.status == "published")

            # Apply tag filters
            if tags:
                query = query.where(Article.tags.overlap(tags))

            # Add author relationship
            query = query.options(selectinload(Article.author))

            # Order by published date
            query = query.order_by(desc(Article.published_at))

            # Apply pagination
            query = query.offset(skip).limit(limit)

            result = await db.execute(query)
            articles = result.scalars().all()

            # Count total
            count_query = select(func.count()).select_from(Article).where(Article.status == "published")
            if tags:
                count_query = count_query.where(Article.tags.overlap(tags))
            total_result = await db.execute(count_query)
            total = total_result.scalar() or 0

            # Format items
            for article in articles:
                items.append({
                    "type": "article",
                    "article": {
                        "id": str(article.id),
                        "title": article.title,
                        "slug": article.slug,
                        "summary": article.summary,
                        "tags": article.tags,
                        "viewCount": article.view_count,
                        "publishedAt": article.published_at.isoformat() if article.published_at else None,
                        "author": {
                            "id": str(article.author.id),
                            "displayName": article.author.display_name or article.author.email,
                            "email": article.author.email,
                        }
                    }
                })

        elif view == "trending":
            # Calculate trending content
            items = await FeedService._get_trending_items(db, tags, time_range, skip, limit)
            total = len(items)  # Simplified for now

        elif view == "following":
            # TODO: Implement following feed when follow system is ready
            pass

        elif view == "recommended":
            # Get recommendations based on user preferences
            if user_id:
                items = await FeedService._get_recommendations(db, user_id, tags, skip, limit)
                total = len(items)

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "nextCursor": None  # TODO: Implement cursor-based pagination
        }

    @staticmethod
    async def calculate_trending(
        db: AsyncSession,
        time_range: str = "24h",
        content_type: str = "all",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Calculate trending content using view velocity and engagement.

        Args:
            db: Database session
            time_range: Time range for calculation (24h, 7d, 30d)
            content_type: Type of content (articles, spaces, tags, all)
            limit: Number of results

        Returns:
            List of trending items with scores
        """
        trending_items = []

        # Calculate time boundary
        now = datetime.now(timezone.utc)
        if time_range == "24h":
            time_boundary = now - timedelta(hours=24)
        elif time_range == "7d":
            time_boundary = now - timedelta(days=7)
        elif time_range == "30d":
            time_boundary = now - timedelta(days=30)
        else:
            time_boundary = None

        if content_type in ["articles", "all"]:
            # Get trending articles
            query = select(Article).where(Article.status == "published")

            if time_boundary:
                query = query.where(Article.published_at >= time_boundary)

            query = query.options(selectinload(Article.author))
            query = query.order_by(desc(Article.view_count))
            query = query.limit(limit)

            result = await db.execute(query)
            articles = result.scalars().all()

            for article in articles:
                # Calculate trending score
                age_hours = (now - article.published_at).total_seconds() / 3600 if article.published_at else 1
                score = FeedService.calculate_trending_score(
                    article.view_count,
                    age_hours,
                    article.like_count
                )

                trending_items.append({
                    "type": "article",
                    "data": {
                        "id": str(article.id),
                        "title": article.title,
                        "slug": article.slug,
                        "summary": article.summary,
                        "tags": article.tags,
                        "viewCount": article.view_count,
                        "author": {
                            "id": str(article.author.id),
                            "displayName": article.author.display_name or article.author.email,
                        }
                    },
                    "score": score,
                    "viewsInPeriod": article.view_count,
                    "trend": "rising"  # TODO: Calculate actual trend
                })

        if content_type in ["spaces", "all"]:
            # Get trending spaces
            query = select(Space).where(Space.visibility == "public")

            if time_boundary:
                query = query.where(Space.created_at >= time_boundary)

            query = query.order_by(desc(Space.member_count))
            query = query.limit(limit)

            result = await db.execute(query)
            spaces = result.scalars().all()

            for space in spaces:
                trending_items.append({
                    "type": "space",
                    "data": {
                        "id": str(space.id),
                        "name": space.name,
                        "slug": space.slug,
                        "description": space.description,
                        "tags": space.tags,
                        "memberCount": space.member_count,
                        "articleCount": space.article_count,
                    },
                    "newMembers": space.member_count,  # TODO: Calculate actual new members
                    "activityScore": space.member_count * 10 + space.article_count * 5
                })

        # Sort by score/activity
        if content_type == "all":
            trending_items.sort(key=lambda x: x.get("score", x.get("activityScore", 0)), reverse=True)
            trending_items = trending_items[:limit]

        return trending_items

    @staticmethod
    async def get_discovery_content(
        db: AsyncSession,
        category: str,
        exclude_seen: bool = False,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get content for discovery based on category.

        Args:
            db: Database session
            category: Discovery category (new_users, rising_articles, active_spaces)
            exclude_seen: Exclude previously seen content
            limit: Number of results

        Returns:
            Discovery response with items and refresh time
        """
        items = []

        if category == "rising_articles":
            # Get articles with high view velocity
            now = datetime.now(timezone.utc)
            recent_boundary = now - timedelta(hours=6)

            query = select(Article).where(
                and_(
                    Article.status == "published",
                    Article.published_at >= recent_boundary
                )
            )
            query = query.options(selectinload(Article.author))
            query = query.order_by(desc(Article.view_count))
            query = query.limit(limit)

            result = await db.execute(query)
            articles = result.scalars().all()

            for article in articles:
                age_hours = (now - article.published_at).total_seconds() / 3600 if article.published_at else 1
                view_velocity = article.view_count / max(age_hours, 1)

                items.append({
                    "article": {
                        "id": str(article.id),
                        "title": article.title,
                        "slug": article.slug,
                        "summary": article.summary,
                        "tags": article.tags,
                        "author": {
                            "id": str(article.author.id),
                            "displayName": article.author.display_name or article.author.email,
                        }
                    },
                    "metrics": {
                        "viewVelocity": round(view_velocity, 2),
                        "viewCount": article.view_count,
                        "firstSeen": article.published_at.isoformat() if article.published_at else None
                    }
                })

        elif category == "active_spaces":
            # Get spaces with recent activity
            query = select(Space).where(Space.visibility == "public")
            query = query.order_by(desc(Space.updated_at))
            query = query.limit(limit)

            result = await db.execute(query)
            spaces = result.scalars().all()

            for space in spaces:
                items.append({
                    "space": {
                        "id": str(space.id),
                        "name": space.name,
                        "slug": space.slug,
                        "description": space.description,
                        "tags": space.tags,
                        "memberCount": space.member_count,
                        "articleCount": space.article_count,
                    }
                })

        elif category == "new_users":
            # Get recently joined users
            recent_boundary = datetime.now(timezone.utc) - timedelta(days=7)

            query = select(User).where(User.created_at >= recent_boundary)
            query = query.order_by(desc(User.created_at))
            query = query.limit(limit)

            result = await db.execute(query)
            users = result.scalars().all()

            for user in users:
                items.append({
                    "user": {
                        "id": str(user.id),
                        "displayName": user.display_name or user.email,
                        "email": user.email,
                        "joinedAt": user.created_at.isoformat()
                    }
                })

        return {
            "category": category,
            "items": items,
            "refreshAt": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        }

    @staticmethod
    async def get_recommendations(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 10,
    ) -> List[Article]:
        """
        Get recommended articles based on user activity and preferences.

        Args:
            db: Database session
            user_id: User ID for recommendations
            limit: Number of recommendations

        Returns:
            List of recommended articles
        """
        # Get user preferences
        preferences = await db.get(UserPreferences, user_id)

        # Base query for articles
        query = select(Article).where(Article.status == "published")

        # If user has preferred tags, prioritize them
        if preferences and preferences.preferred_tags:
            query = query.where(Article.tags.overlap(preferences.preferred_tags))

        # Exclude articles the user has already seen (simplified for now)
        # TODO: Track user views and exclude them

        query = query.options(selectinload(Article.author))
        query = query.order_by(desc(Article.view_count))
        query = query.limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    def calculate_trending_score(
        views: int,
        age_hours: float,
        interactions: int = 0
    ) -> float:
        """
        Calculate trending score using time decay.

        Formula: Score = (views + interactions * 2) / (age_hours + 2) ^ 1.5

        Args:
            views: Number of views
            age_hours: Age of content in hours
            interactions: Number of interactions (likes, comments, etc.)

        Returns:
            Trending score
        """
        base_score = views + (interactions * 2)
        time_penalty = pow(age_hours + 2, 1.5)
        return base_score / time_penalty

    @staticmethod
    async def _get_trending_items(
        db: AsyncSession,
        tags: List[str] | None,
        time_range: str | None,
        skip: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get trending items for feed."""
        trending = await FeedService.calculate_trending(
            db, time_range or "24h", "articles", limit
        )

        # Filter by tags if provided
        if tags:
            trending = [
                item for item in trending
                if any(tag in item["data"].get("tags", []) for tag in tags)
            ]

        # Apply pagination
        trending = trending[skip:skip + limit]

        # Format for feed
        items = []
        for item in trending:
            items.append({
                "type": "article",
                "article": item["data"],
                "reason": "trending_in_period",
                "score": item["score"]
            })

        return items

    @staticmethod
    async def _get_recommendations(
        db: AsyncSession,
        user_id: UUID,
        tags: List[str] | None,
        skip: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get recommended items for feed."""
        articles = await FeedService.get_recommendations(db, user_id, limit)

        items = []
        for article in articles:
            items.append({
                "type": "article",
                "article": {
                    "id": str(article.id),
                    "title": article.title,
                    "slug": article.slug,
                    "summary": article.summary,
                    "tags": article.tags,
                    "viewCount": article.view_count,
                    "publishedAt": article.published_at.isoformat() if article.published_at else None,
                    "author": {
                        "id": str(article.author.id),
                        "displayName": article.author.display_name or article.author.email,
                    }
                },
                "reason": "recommended"
            })

        return items