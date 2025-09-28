"""Search service for full-text search across the platform."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import AI_TAGS
from ..models import Article, SearchIndex, Space, User


class SearchService:
    """Service for full-text search and search index management."""

    @staticmethod
    async def search(
        db: AsyncSession,
        query: str,
        search_type: str = "all",
        tags: List[str] | None = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Full-text search across articles, spaces, and users.

        Args:
            db: Database session
            query: Search query
            search_type: Type to search ('all', 'articles', 'spaces', 'users')
            tags: Filter by specific tags
            skip: Pagination offset
            limit: Page size

        Returns:
            Search results with facets and metadata
        """
        results = []
        facets = {"types": {}, "tags": {}}

        # Search articles
        if search_type in ["all", "articles"]:
            article_results = await SearchService._search_articles(
                db, query, tags
            )
            results.extend(article_results)
            facets["types"]["articles"] = len(article_results)

        # Search spaces
        if search_type in ["all", "spaces"]:
            space_results = await SearchService._search_spaces(
                db, query, tags
            )
            results.extend(space_results)
            facets["types"]["spaces"] = len(space_results)

        # Search users
        if search_type in ["all", "users"]:
            user_results = await SearchService._search_users(
                db, query, tags
            )
            results.extend(user_results)
            facets["types"]["users"] = len(user_results)

        # Sort results by score
        results.sort(key=lambda x: x["score"], reverse=True)

        # Calculate tag facets from results
        tag_counts = {}
        for result in results:
            if "tags" in result["item"]:
                for tag in result["item"]["tags"]:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        facets["tags"] = tag_counts

        # Apply pagination
        paginated_results = results[skip:skip + limit]

        return {
            "results": paginated_results,
            "total": len(results),
            "facets": facets,
            "skip": skip,
            "limit": limit,
            "processingTime": 0  # Will be calculated by endpoint
        }

    @staticmethod
    async def _search_articles(
        db: AsyncSession,
        query: str,
        tags: List[str] | None = None
    ) -> List[Dict[str, Any]]:
        """Search articles using PostgreSQL full-text search."""
        # Build base query with text search
        search_query = text("""
            SELECT
                a.id,
                a.title,
                a.slug,
                a.summary,
                a.tags,
                a.author_id,
                a.view_count,
                a.like_count,
                a.created_at,
                a.published_at,
                u.display_name as author_name,
                u.email as author_email,
                ts_rank(
                    to_tsvector('english', a.title || ' ' || COALESCE(a.summary, '') || ' ' || array_to_string(a.tags, ' ')),
                    plainto_tsquery('english', :query)
                ) as rank
            FROM articles a
            JOIN users u ON a.author_id = u.id
            WHERE a.status = 'published'
            AND to_tsvector('english', a.title || ' ' || COALESCE(a.summary, '') || ' ' || array_to_string(a.tags, ' '))
                @@ plainto_tsquery('english', :query)
        """)

        # Execute search
        result = await db.execute(search_query, {"query": query})
        rows = result.fetchall()

        articles = []
        for row in rows:
            # Apply tag filter if specified
            if tags and not any(tag in row.tags for tag in tags):
                continue

            # Calculate combined score
            text_rank = row.rank
            popularity = math.log(row.view_count + 1)
            recency = 0
            if row.published_at:
                days_old = (datetime.now(timezone.utc) - row.published_at).days
                recency = 1 / (1 + days_old / 30)

            score = (text_rank * 100) + (popularity * 10) + (recency * 20)

            # Check for exact tag match bonus
            if tags and any(tag in row.tags for tag in tags):
                score *= 1.5

            # Create highlighted snippets
            highlights = SearchService._create_highlights(
                row.title, row.summary or "", query
            )

            articles.append({
                "type": "article",
                "score": score,
                "item": {
                    "id": str(row.id),
                    "title": row.title,
                    "slug": row.slug,
                    "summary": row.summary,
                    "tags": row.tags,
                    "author": {
                        "id": str(row.author_id),
                        "displayName": row.author_name,
                        "email": row.author_email
                    },
                    "viewCount": row.view_count,
                    "likeCount": row.like_count,
                    "publishedAt": row.published_at.isoformat() if row.published_at else None,
                    "highlights": highlights
                }
            })

        return articles

    @staticmethod
    async def _search_spaces(
        db: AsyncSession,
        query: str,
        tags: List[str] | None = None
    ) -> List[Dict[str, Any]]:
        """Search spaces using PostgreSQL full-text search."""
        search_query = text("""
            SELECT
                s.id,
                s.name,
                s.slug,
                s.description,
                s.tags,
                s.member_count,
                s.article_count,
                s.visibility,
                s.created_at,
                s.owner_id,
                u.display_name as owner_name,
                u.email as owner_email,
                ts_rank(
                    to_tsvector('english', s.name || ' ' || COALESCE(s.description, '') || ' ' || array_to_string(s.tags, ' ')),
                    plainto_tsquery('english', :query)
                ) as rank
            FROM spaces s
            JOIN users u ON s.owner_id = u.id
            WHERE s.visibility = 'public'
            AND to_tsvector('english', s.name || ' ' || COALESCE(s.description, '') || ' ' || array_to_string(s.tags, ' '))
                @@ plainto_tsquery('english', :query)
        """)

        result = await db.execute(search_query, {"query": query})
        rows = result.fetchall()

        spaces = []
        for row in rows:
            # Apply tag filter
            if tags and not any(tag in row.tags for tag in tags):
                continue

            # Calculate score
            text_rank = row.rank
            popularity = math.log(row.member_count + 1)
            activity = math.log(row.article_count + 1)

            score = (text_rank * 100) * 0.9 + (popularity * 10) + (activity * 5)

            # Tag match bonus
            if tags and any(tag in row.tags for tag in tags):
                score *= 1.5

            highlights = SearchService._create_highlights(
                row.name, row.description or "", query
            )

            spaces.append({
                "type": "space",
                "score": score,
                "item": {
                    "id": str(row.id),
                    "name": row.name,
                    "slug": row.slug,
                    "description": row.description,
                    "tags": row.tags,
                    "memberCount": row.member_count,
                    "articleCount": row.article_count,
                    "visibility": row.visibility,
                    "owner": {
                        "id": str(row.owner_id),
                        "displayName": row.owner_name,
                        "email": row.owner_email
                    },
                    "createdAt": row.created_at.isoformat() if row.created_at else None,
                    "highlights": highlights
                }
            })

        return spaces

    @staticmethod
    async def _search_users(
        db: AsyncSession,
        query: str,
        tags: List[str] | None = None
    ) -> List[Dict[str, Any]]:
        """Search users by name, bio, and expertise."""
        # Note: User model needs bio and expertise_tags fields added
        # For now, we'll search by display_name and email
        search_query = text("""
            SELECT
                u.id,
                u.email,
                u.display_name,
                u.created_at,
                ts_rank(
                    to_tsvector('english', COALESCE(u.display_name, '') || ' ' || u.email),
                    plainto_tsquery('english', :query)
                ) as rank
            FROM users u
            WHERE to_tsvector('english', COALESCE(u.display_name, '') || ' ' || u.email)
                @@ plainto_tsquery('english', :query)
        """)

        result = await db.execute(search_query, {"query": query})
        rows = result.fetchall()

        users = []
        for row in rows:
            score = row.rank * 100 * 0.8  # Users have lower base relevance

            users.append({
                "type": "user",
                "score": score,
                "item": {
                    "id": str(row.id),
                    "email": row.email,
                    "displayName": row.display_name,
                    "createdAt": row.created_at.isoformat() if row.created_at else None
                }
            })

        return users

    @staticmethod
    def _create_highlights(title: str, content: str, query: str) -> Dict[str, str]:
        """Create highlighted snippets for search results."""
        highlights = {}
        query_terms = query.lower().split()

        # Highlight title
        highlighted_title = title
        for term in query_terms:
            if term in title.lower():
                # Simple case-insensitive replacement
                import re
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted_title = pattern.sub(f"<mark>{term}</mark>", highlighted_title)
        highlights["title"] = highlighted_title

        # Highlight content snippet
        if content:
            # Find first occurrence of query term
            content_lower = content.lower()
            best_pos = len(content)
            for term in query_terms:
                pos = content_lower.find(term)
                if pos != -1 and pos < best_pos:
                    best_pos = pos

            # Extract snippet around the match
            if best_pos < len(content):
                start = max(0, best_pos - 50)
                end = min(len(content), best_pos + 150)
                snippet = content[start:end]

                # Add ellipsis if needed
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."

                # Highlight terms in snippet
                for term in query_terms:
                    if term in snippet.lower():
                        import re
                        pattern = re.compile(re.escape(term), re.IGNORECASE)
                        snippet = pattern.sub(f"<mark>{term}</mark>", snippet)

                highlights["content"] = snippet

        return highlights

    @staticmethod
    async def update_search_index(
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID,
        title: str,
        content: str,
        tags: List[str]
    ) -> None:
        """Update search index for an entity.

        Args:
            db: Database session
            entity_type: Type of entity ('article', 'space', 'user')
            entity_id: Entity ID
            title: Entity title/name
            content: Entity content/description
            tags: Associated tags
        """
        # Check if index entry exists
        result = await db.execute(
            select(SearchIndex).where(
                and_(
                    SearchIndex.entity_type == entity_type,
                    SearchIndex.entity_id == entity_id
                )
            )
        )
        search_index = result.scalar_one_or_none()

        if search_index:
            # Update existing entry
            search_index.title = title
            search_index.content = content
            search_index.tags = tags
            search_index.updated_at = datetime.now(timezone.utc)
        else:
            # Create new entry
            search_index = SearchIndex(
                entity_type=entity_type,
                entity_id=entity_id,
                title=title,
                content=content,
                tags=tags
            )
            db.add(search_index)

        await db.commit()

    @staticmethod
    async def delete_from_search_index(
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID
    ) -> None:
        """Remove entity from search index.

        Args:
            db: Database session
            entity_type: Type of entity
            entity_id: Entity ID
        """
        from sqlalchemy import delete
        await db.execute(
            delete(SearchIndex).where(
                and_(
                    SearchIndex.entity_type == entity_type,
                    SearchIndex.entity_id == entity_id
                )
            )
        )
        await db.commit()

    @staticmethod
    async def autocomplete(
        db: AsyncSession,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate autocomplete suggestions.

        Args:
            db: Database session
            query: Partial query (min 2 chars)
            limit: Maximum suggestions

        Returns:
            List of suggestions
        """
        if len(query) < 2:
            return []

        suggestions = []
        query_lower = query.lower()

        # Tag suggestions
        matching_tags = [
            tag for tag in AI_TAGS
            if query_lower in tag.lower()
        ][:3]

        for tag in matching_tags:
            # Get tag usage count
            tag_query = text("""
                SELECT article_count + space_count + user_count as total
                FROM tag_usage
                WHERE tag = :tag
            """)
            result = await db.execute(tag_query, {"tag": tag})
            row = result.fetchone()
            count = row.total if row else 0

            suggestions.append({
                "type": "tag",
                "text": tag,
                "count": count
            })

        # Article title suggestions
        article_query = text("""
            SELECT title, slug, view_count
            FROM articles
            WHERE status = 'published'
            AND LOWER(title) LIKE :pattern
            ORDER BY view_count DESC
            LIMIT :limit
        """)
        result = await db.execute(
            article_query,
            {"pattern": f"%{query_lower}%", "limit": limit - len(suggestions)}
        )

        for row in result:
            suggestions.append({
                "type": "article",
                "text": row.title,
                "slug": row.slug,
                "count": row.view_count
            })

        # Space name suggestions
        if len(suggestions) < limit:
            space_query = text("""
                SELECT name, slug, member_count
                FROM spaces
                WHERE visibility = 'public'
                AND LOWER(name) LIKE :pattern
                ORDER BY member_count DESC
                LIMIT :limit
            """)
            result = await db.execute(
                space_query,
                {"pattern": f"%{query_lower}%", "limit": limit - len(suggestions)}
            )

            for row in result:
                suggestions.append({
                    "type": "space",
                    "text": row.name,
                    "slug": row.slug,
                    "count": row.member_count
                })

        return suggestions[:limit]