"""Tag service for managing and analyzing tags across the platform."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import AI_TAGS, TAG_DESCRIPTIONS, TAG_RELATIONSHIPS
from ..models import Article, Space, TagUsage, User


class TagService:
    """Service for tag management and analysis."""

    @staticmethod
    async def update_tag_usage(
        db: AsyncSession,
        tag: str,
        entity_type: str,
        delta: int = 1
    ) -> None:
        """Update tag usage counts when content is created/updated/deleted.

        Args:
            db: Database session
            tag: Tag name
            entity_type: Type of entity ('article', 'space', 'user')
            delta: Change amount (1 for add, -1 for remove)
        """
        if tag not in AI_TAGS:
            return  # Only track official AI tags

        # Get or create tag usage record
        result = await db.execute(
            select(TagUsage).where(TagUsage.tag == tag)
        )
        tag_usage = result.scalar_one_or_none()

        if not tag_usage:
            tag_usage = TagUsage(tag=tag)
            db.add(tag_usage)

        # Update appropriate count
        if entity_type == 'article':
            tag_usage.article_count = max(0, tag_usage.article_count + delta)
        elif entity_type == 'space':
            tag_usage.space_count = max(0, tag_usage.space_count + delta)
        elif entity_type == 'user':
            tag_usage.user_count = max(0, tag_usage.user_count + delta)

        # Update last used timestamp if adding
        if delta > 0:
            tag_usage.last_used_at = datetime.now(timezone.utc)
            # Update weekly/monthly counts
            tag_usage.week_count += 1
            tag_usage.month_count += 1

        await db.commit()

    @staticmethod
    async def calculate_trending_scores(db: AsyncSession) -> None:
        """Calculate trending scores for all tags based on recent usage.

        This should be run periodically (e.g., hourly) via a background job.
        """
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Get all tag usage records
        result = await db.execute(select(TagUsage))
        tag_usages = result.scalars().all()

        for tag_usage in tag_usages:
            # Calculate base score from total usage
            total_usage = (
                tag_usage.article_count +
                tag_usage.space_count +
                tag_usage.user_count
            )

            # Calculate recency factor (decay over time)
            if tag_usage.last_used_at:
                hours_since_use = (now - tag_usage.last_used_at).total_seconds() / 3600
                recency_factor = 1 / (1 + hours_since_use / 168)  # Week-based decay
            else:
                recency_factor = 0

            # Calculate growth factor (recent usage vs historical)
            growth_factor = 0
            if tag_usage.month_count > 0:
                week_ratio = tag_usage.week_count / max(1, tag_usage.month_count / 4)
                growth_factor = min(2.0, week_ratio)  # Cap at 2x

            # Combined trending score
            tag_usage.trending_score = (
                math.log(total_usage + 1) * 10 +  # Logarithmic base score
                recency_factor * 30 +  # Recency bonus
                growth_factor * 20  # Growth bonus
            )

        await db.commit()

    @staticmethod
    async def reset_periodic_counts(db: AsyncSession, period: str = 'week') -> None:
        """Reset weekly or monthly counts. Run via cron job.

        Args:
            db: Database session
            period: 'week' or 'month'
        """
        if period == 'week':
            await db.execute(
                update(TagUsage).values(week_count=0)
            )
        elif period == 'month':
            await db.execute(
                update(TagUsage).values(month_count=0, week_count=0)
            )
        await db.commit()

    @staticmethod
    async def get_related_tags(tag: str, limit: int = 5) -> List[str]:
        """Get related tags based on predefined relationships.

        Args:
            tag: Tag to find relationships for
            limit: Maximum number of related tags to return
        """
        related = TAG_RELATIONSHIPS.get(tag, [])
        return related[:limit]

    @staticmethod
    async def suggest_tags(
        title: str,
        content: str,
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """Suggest tags for content using keyword matching.

        For MVP, we use simple keyword matching.
        Future enhancement: Use embeddings for semantic matching.

        Args:
            title: Content title
            content: Content body
            limit: Maximum number of suggestions

        Returns:
            List of (tag, confidence) tuples
        """
        text = f"{title} {content}".lower()
        suggestions = []

        for tag in AI_TAGS:
            confidence = 0.0
            tag_lower = tag.lower()

            # Check exact match
            if tag_lower in text:
                confidence += 0.5

            # Check individual words for multi-word tags
            words = tag_lower.split()
            for word in words:
                if len(word) > 3 and word in text:  # Skip short words
                    confidence += 0.3 / len(words)

            # Check description keywords
            description = TAG_DESCRIPTIONS.get(tag, "").lower()
            desc_words = description.split()
            for word in desc_words:
                if len(word) > 4 and word in text:
                    confidence += 0.1

            # Special cases for common variations
            variations = {
                "LLMs": ["llm", "language model", "gpt", "claude", "llama"],
                "RAG": ["retrieval augmented", "retrieval-augmented"],
                "NLP": ["natural language", "text processing"],
                "Computer Vision": ["cv", "image", "vision"],
                "RL": ["reinforcement learning"],
                "Vector DBs": ["vector database", "vectordb", "embedding database"]
            }

            if tag in variations:
                for variant in variations[tag]:
                    if variant in text:
                        confidence += 0.4

            if confidence > 0:
                suggestions.append((tag, min(1.0, confidence)))

        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:limit]

    @staticmethod
    async def get_tag_stats(db: AsyncSession, tag: str) -> dict | None:
        """Get detailed statistics for a specific tag.

        Args:
            db: Database session
            tag: Tag name

        Returns:
            Dictionary with tag statistics or None if not found
        """
        result = await db.execute(
            select(TagUsage).where(TagUsage.tag == tag)
        )
        tag_usage = result.scalar_one_or_none()

        if not tag_usage:
            # Return zeros for valid tags that haven't been used yet
            if tag in AI_TAGS:
                return {
                    "name": tag,
                    "description": TAG_DESCRIPTIONS.get(tag, ""),
                    "stats": {
                        "articles": 0,
                        "spaces": 0,
                        "experts": 0,
                        "totalUsage": 0,
                        "trendingScore": 0.0
                    },
                    "related": TAG_RELATIONSHIPS.get(tag, [])
                }
            return None

        total = tag_usage.article_count + tag_usage.space_count + tag_usage.user_count

        # Calculate week-over-week growth
        weekly_growth = None
        if tag_usage.month_count > 0 and tag_usage.week_count > 0:
            prev_week_avg = (tag_usage.month_count - tag_usage.week_count) / 3
            if prev_week_avg > 0:
                growth_pct = ((tag_usage.week_count - prev_week_avg) / prev_week_avg) * 100
                weekly_growth = f"{'+' if growth_pct > 0 else ''}{growth_pct:.0f}%"

        return {
            "name": tag,
            "description": TAG_DESCRIPTIONS.get(tag, ""),
            "stats": {
                "articles": tag_usage.article_count,
                "spaces": tag_usage.space_count,
                "experts": tag_usage.user_count,
                "totalUsage": total,
                "weeklyGrowth": weekly_growth,
                "trendingScore": tag_usage.trending_score
            },
            "related": TAG_RELATIONSHIPS.get(tag, [])
        }

    @staticmethod
    async def get_all_tags_with_stats(
        db: AsyncSession,
        sort: str = "popular",
        category: str = "all",
        limit: int | None = None
    ) -> List[dict]:
        """Get all tags with their usage statistics.

        Args:
            db: Database session
            sort: Sort order ('alphabetical', 'popular', 'trending')
            category: Filter category ('all', 'with_content', 'with_experts')
            limit: Maximum number of tags to return
        """
        # Build query
        query = select(TagUsage)

        # Apply category filter
        if category == "with_content":
            query = query.where((TagUsage.article_count > 0) | (TagUsage.space_count > 0))
        elif category == "with_experts":
            query = query.where(TagUsage.user_count > 0)

        # Apply sorting
        if sort == "alphabetical":
            query = query.order_by(TagUsage.tag)
        elif sort == "trending":
            query = query.order_by(TagUsage.trending_score.desc())
        else:  # popular
            query = query.order_by(
                (TagUsage.article_count + TagUsage.space_count + TagUsage.user_count).desc()
            )

        if limit:
            query = query.limit(limit)

        result = await db.execute(query)
        tag_usages = result.scalars().all()

        # Build response including unused tags
        used_tags = {tu.tag: tu for tu in tag_usages}
        all_tag_stats = []

        for tag in AI_TAGS:
            if tag in used_tags:
                tu = used_tags[tag]
                total = tu.article_count + tu.space_count + tu.user_count

                # Calculate weekly growth
                weekly_growth = None
                if tu.month_count > 0 and tu.week_count > 0:
                    prev_week_avg = (tu.month_count - tu.week_count) / 3
                    if prev_week_avg > 0:
                        growth_pct = ((tu.week_count - prev_week_avg) / prev_week_avg) * 100
                        weekly_growth = f"{'+' if growth_pct > 0 else ''}{growth_pct:.0f}%"

                all_tag_stats.append({
                    "name": tag,
                    "description": TAG_DESCRIPTIONS.get(tag, ""),
                    "stats": {
                        "articles": tu.article_count,
                        "spaces": tu.space_count,
                        "experts": tu.user_count,
                        "totalUsage": total,
                        "weeklyGrowth": weekly_growth,
                        "trendingScore": tu.trending_score
                    },
                    "related": TAG_RELATIONSHIPS.get(tag, [])[:3]
                })
            elif category == "all":
                # Include unused tags when showing all
                all_tag_stats.append({
                    "name": tag,
                    "description": TAG_DESCRIPTIONS.get(tag, ""),
                    "stats": {
                        "articles": 0,
                        "spaces": 0,
                        "experts": 0,
                        "totalUsage": 0,
                        "weeklyGrowth": None,
                        "trendingScore": 0.0
                    },
                    "related": TAG_RELATIONSHIPS.get(tag, [])[:3]
                })

        # Re-sort if needed (to include unused tags)
        if sort == "alphabetical":
            all_tag_stats.sort(key=lambda x: x["name"])
        elif sort == "trending":
            all_tag_stats.sort(key=lambda x: x["stats"]["trendingScore"], reverse=True)
        elif sort == "popular":
            all_tag_stats.sort(key=lambda x: x["stats"]["totalUsage"], reverse=True)

        if limit:
            all_tag_stats = all_tag_stats[:limit]

        return all_tag_stats