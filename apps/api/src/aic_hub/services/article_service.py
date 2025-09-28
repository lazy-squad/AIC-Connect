"""Article service layer for business logic."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..constants import AI_TAGS
from ..models import Article, User
from ..utils import slugify
# Import services conditionally to avoid circular imports
try:
    from .tag_service import TagService
    from .search_service import SearchService
except ImportError:
    # Services not available yet
    TagService = None
    SearchService = None


class ArticleService:
    """Service class for article-related operations."""

    @staticmethod
    async def create_article(
        db: AsyncSession,
        author_id: UUID,
        title: str,
        content: dict | str,
        summary: str | None = None,
        tags: list[str] | None = None,
        published: bool = False,
    ) -> Article:
        """Create a new article with unique slug generation.

        Args:
            db: Database session
            author_id: ID of the article author
            title: Article title
            content: Article content (Tiptap JSON or string)
            summary: Article summary (max 500 chars)
            tags: List of tags (validated against AI_TAGS)
            published: Whether to publish immediately

        Returns:
            Created article instance
        """
        # Validate tags
        if tags:
            invalid_tags = [tag for tag in tags if tag not in AI_TAGS]
            if invalid_tags:
                raise ValueError(f"Invalid tags: {invalid_tags}")
            # Limit to 5 tags
            if len(tags) > 5:
                raise ValueError("Maximum 5 tags allowed")
        else:
            tags = []

        # Validate summary length
        if summary and len(summary) > 500:
            raise ValueError("Summary must be 500 characters or less")

        # Generate unique slug
        slug = await ArticleService._generate_unique_slug(db, title)

        # Convert content to JSON string if needed
        if isinstance(content, dict):
            content_str = json.dumps(content)
        else:
            content_str = content

        # Create article
        article = Article(
            author_id=author_id,
            title=title,
            slug=slug,
            content=content_str,
            summary=summary,
            tags=tags,
            status="published" if published else "draft",
            published_at=datetime.utcnow() if published else None,
        )

        db.add(article)
        await db.commit()
        await db.refresh(article)

        # Update tag usage stats for published articles
        if published and tags and TagService:
            for tag in tags:
                await TagService.update_tag_usage(db, tag, "article", delta=1)

        # Update search index for published articles
        if published and SearchService:
            await SearchService.update_search_index(
                db=db,
                entity_type="article",
                entity_id=article.id,
                title=article.title,
                content=article.summary or "",
                tags=article.tags
            )

        return article

    @staticmethod
    async def _generate_unique_slug(
        db: AsyncSession, title: str, existing_id: UUID | None = None
    ) -> str:
        """Generate a unique slug from title.

        Args:
            db: Database session
            title: Title to convert to slug
            existing_id: ID of existing article (for updates)

        Returns:
            Unique slug string
        """
        base_slug = slugify(title)
        slug = base_slug
        counter = 1

        while True:
            # Check if slug exists (excluding current article if updating)
            stmt = select(Article).where(Article.slug == slug)
            if existing_id:
                stmt = stmt.where(Article.id != existing_id)

            result = await db.execute(stmt)
            if not result.scalar_one_or_none():
                return slug

            # Append number if slug exists
            slug = f"{base_slug}-{counter}"
            counter += 1

    @staticmethod
    async def get_articles(
        db: AsyncSession,
        tags: list[str] | None = None,
        author_username: str | None = None,
        search_query: str | None = None,
        published_only: bool = True,
        skip: int = 0,
        limit: int = 20,
        sort: str = "latest",
    ) -> tuple[list[Article], int]:
        """Get articles with filters and pagination.

        Args:
            db: Database session
            tags: Filter by tags (OR condition)
            author_username: Filter by author's username
            search_query: Search in title and summary
            published_only: Only show published articles
            skip: Number of articles to skip
            limit: Maximum number of articles to return
            sort: Sort order ('latest', 'popular', 'trending')

        Returns:
            Tuple of (articles list, total count)
        """
        # Base query with author relationship
        query = select(Article).options(selectinload(Article.author))
        count_query = select(func.count(Article.id))

        # Apply filters
        filters = []

        if published_only:
            filters.append(Article.status == "published")

        if tags:
            # OR condition for tags
            filters.append(Article.tags.overlap(tags))

        if author_username:
            # Join with User table for username filter
            query = query.join(User).where(User.email == author_username)
            count_query = count_query.join(User).where(User.email == author_username)

        if search_query:
            # Search in title and summary
            search_filter = or_(
                Article.title.ilike(f"%{search_query}%"),
                Article.summary.ilike(f"%{search_query}%"),
            )
            filters.append(search_filter)

        # Apply all filters
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Apply sorting
        if sort == "popular":
            query = query.order_by(Article.view_count.desc())
        elif sort == "trending":
            # Trending: recent articles with high view count
            query = query.order_by(
                Article.view_count.desc(),
                Article.created_at.desc()
            )
        else:  # latest
            query = query.order_by(Article.created_at.desc())

        # Get total count
        count_result = await db.execute(count_query)
        total = count_result.scalar_one()

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        result = await db.execute(query)
        articles = list(result.scalars().all())

        return articles, total

    @staticmethod
    async def get_article_by_slug(
        db: AsyncSession, slug: str, user_id: UUID | None = None
    ) -> Article | None:
        """Get article by slug.

        Args:
            db: Database session
            slug: Article slug
            user_id: Current user ID (for permission checks)

        Returns:
            Article instance or None
        """
        stmt = select(Article).options(selectinload(Article.author)).where(
            Article.slug == slug
        )
        result = await db.execute(stmt)
        article = result.scalar_one_or_none()

        # Check permissions for unpublished articles
        if article and article.status != "published":
            if not user_id or article.author_id != user_id:
                return None

        return article

    @staticmethod
    async def get_user_drafts(
        db: AsyncSession, user_id: UUID
    ) -> list[Article]:
        """Get user's draft articles.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of draft articles
        """
        stmt = (
            select(Article)
            .options(selectinload(Article.author))
            .where(
                and_(
                    Article.author_id == user_id,
                    Article.status == "draft"
                )
            )
            .order_by(Article.updated_at.desc().nullslast(), Article.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_article(
        db: AsyncSession,
        article_id: UUID,
        user_id: UUID,
        title: str | None = None,
        content: dict | str | None = None,
        summary: str | None = None,
        tags: list[str] | None = None,
        published: bool | None = None,
    ) -> Article | None:
        """Update an article.

        Args:
            db: Database session
            article_id: Article ID
            user_id: Current user ID (must be author)
            title: New title
            content: New content
            summary: New summary
            tags: New tags
            published: Publication status

        Returns:
            Updated article or None if not found/unauthorized
        """
        # Get article and check permissions
        stmt = select(Article).where(Article.id == article_id)
        result = await db.execute(stmt)
        article = result.scalar_one_or_none()

        if not article or article.author_id != user_id:
            return None

        # Store original state for tag and search updates
        original_tags = article.tags.copy() if article.tags else []
        original_published = article.status == "published"

        # Update fields
        if title is not None:
            article.title = title
            # Regenerate slug if title changed
            article.slug = await ArticleService._generate_unique_slug(
                db, title, article_id
            )

        if content is not None:
            if isinstance(content, dict):
                article.content = json.dumps(content)
            else:
                article.content = content

        if summary is not None:
            if len(summary) > 500:
                raise ValueError("Summary must be 500 characters or less")
            article.summary = summary

        if tags is not None:
            # Validate tags
            invalid_tags = [tag for tag in tags if tag not in AI_TAGS]
            if invalid_tags:
                raise ValueError(f"Invalid tags: {invalid_tags}")
            if len(tags) > 5:
                raise ValueError("Maximum 5 tags allowed")
            article.tags = tags

        if published is not None:
            if published and article.status == "draft":
                article.status = "published"
                article.published_at = datetime.utcnow()
            elif not published and article.status == "published":
                article.status = "draft"
                article.published_at = None

        article.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(article)

        # Handle tag usage updates
        current_published = article.status == "published"
        current_tags = article.tags if article.tags else []

        # If publication status changed
        if original_published != current_published and TagService:
            if current_published:  # Published now
                # Add tag usage for all current tags
                for tag in current_tags:
                    await TagService.update_tag_usage(db, tag, "article", delta=1)
            else:  # Unpublished now
                # Remove tag usage for all original tags
                for tag in original_tags:
                    await TagService.update_tag_usage(db, tag, "article", delta=-1)

        # If tags changed while published
        elif current_published and TagService:
            # Remove old tags
            removed_tags = set(original_tags) - set(current_tags)
            for tag in removed_tags:
                await TagService.update_tag_usage(db, tag, "article", delta=-1)

            # Add new tags
            added_tags = set(current_tags) - set(original_tags)
            for tag in added_tags:
                await TagService.update_tag_usage(db, tag, "article", delta=1)

        # Update search index for published articles
        if current_published and SearchService:
            await SearchService.update_search_index(
                db=db,
                entity_type="article",
                entity_id=article.id,
                title=article.title,
                content=article.summary or "",
                tags=article.tags
            )
        elif original_published and not current_published and SearchService:
            # Remove from search index if unpublished
            await SearchService.delete_from_search_index(
                db=db,
                entity_type="article",
                entity_id=article.id
            )

        return article

    @staticmethod
    async def delete_article(
        db: AsyncSession, article_id: UUID, user_id: UUID
    ) -> bool:
        """Delete an article.

        Args:
            db: Database session
            article_id: Article ID
            user_id: Current user ID (must be author)

        Returns:
            True if deleted, False if not found/unauthorized
        """
        # Get article and check permissions
        stmt = select(Article).where(Article.id == article_id)
        result = await db.execute(stmt)
        article = result.scalar_one_or_none()

        if not article or article.author_id != user_id:
            return False

        # Store state for cleanup
        was_published = article.status == "published"
        article_tags = article.tags if article.tags else []

        await db.delete(article)
        await db.commit()

        # Clean up tag usage and search index
        if was_published:
            # Remove tag usage
            if TagService:
                for tag in article_tags:
                    await TagService.update_tag_usage(db, tag, "article", delta=-1)

            # Remove from search index
            if SearchService:
                await SearchService.delete_from_search_index(
                    db=db,
                    entity_type="article",
                    entity_id=article.id
                )

        return True

    @staticmethod
    async def increment_view_count(db: AsyncSession, article_id: UUID) -> None:
        """Atomically increment article view count.

        Args:
            db: Database session
            article_id: Article ID
        """
        stmt = (
            update(Article)
            .where(Article.id == article_id)
            .values(view_count=Article.view_count + 1)
        )
        await db.execute(stmt)
        await db.commit()

    @staticmethod
    def validate_tiptap_content(content: dict) -> bool:
        """Validate Tiptap JSON structure.

        Args:
            content: Tiptap content to validate

        Returns:
            True if valid, False otherwise
        """
        # Basic validation for Tiptap structure
        if not isinstance(content, dict):
            return False

        if "type" not in content or content["type"] != "doc":
            return False

        if "content" not in content or not isinstance(content["content"], list):
            return False

        # Could add more detailed validation here
        return True