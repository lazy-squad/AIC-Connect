"""Article routes for the AIC Hub API."""

from __future__ import annotations

import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db_session
from ..dependencies import get_current_user, get_current_user_optional
from ..models import User
from ..schemas import (
    Article,
    ArticleCreate,
    ArticleListResponse,
    ArticleSummary,
    ArticleUpdate,
    UserSummary,
)
from ..services import ArticleService

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.post("", response_model=Article, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_data: ArticleCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Article:
    """Create a new article."""
    try:
        # Parse content as JSON if it's a string representation
        content = article_data.content
        try:
            content_dict = json.loads(content) if isinstance(content, str) else content
        except json.JSONDecodeError:
            # If it's not JSON, store as text
            content_dict = {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": content}]}]}

        article = await ArticleService.create_article(
            db=db,
            author_id=current_user.id,
            title=article_data.title,
            content=content_dict,
            summary=article_data.summary,
            tags=article_data.tags,
            published=False,  # Always start as draft
        )

        # Convert author to UserSummary
        author_summary = UserSummary(
            id=article.author.id,
            username=article.author.email.split("@")[0],  # Use email prefix as username for now
            display_name=article.author.display_name,
            avatar_url=None,  # Will be added when user profiles are complete
        )

        return Article(
            id=article.id,
            title=article.title,
            slug=article.slug,
            summary=article.summary,
            content=article.content,
            tags=article.tags,
            status=article.status,
            author=author_summary,
            view_count=article.view_count,
            like_count=article.like_count,
            published_at=article.published_at,
            created_at=article.created_at,
            updated_at=article.updated_at,
            is_author=True,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    tags: list[str] | None = Query(default=None),
    author: str | None = Query(default=None),
    q: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="latest", regex="^(latest|popular|trending)$"),
) -> ArticleListResponse:
    """List published articles with filters."""
    articles, total = await ArticleService.get_articles(
        db=db,
        tags=tags,
        author_username=author,
        search_query=q,
        published_only=True,
        skip=skip,
        limit=limit,
        sort=sort,
    )

    # Convert to response models
    article_summaries = []
    for article in articles:
        author_summary = UserSummary(
            id=article.author.id,
            username=article.author.email.split("@")[0],
            display_name=article.author.display_name,
            avatar_url=None,
        )

        article_summaries.append(
            ArticleSummary(
                id=article.id,
                title=article.title,
                slug=article.slug,
                summary=article.summary,
                tags=article.tags,
                author=author_summary,
                view_count=article.view_count,
                like_count=article.like_count,
                published_at=article.published_at,
                created_at=article.created_at,
            )
        )

    return ArticleListResponse(
        articles=article_summaries,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/drafts", response_model=list[ArticleSummary])
async def get_drafts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[ArticleSummary]:
    """Get current user's draft articles."""
    drafts = await ArticleService.get_user_drafts(db=db, user_id=current_user.id)

    # Convert to response models
    draft_summaries = []
    for article in drafts:
        author_summary = UserSummary(
            id=article.author.id,
            username=article.author.email.split("@")[0],
            display_name=article.author.display_name,
            avatar_url=None,
        )

        draft_summaries.append(
            ArticleSummary(
                id=article.id,
                title=article.title,
                slug=article.slug,
                summary=article.summary,
                tags=article.tags,
                author=author_summary,
                view_count=article.view_count,
                like_count=article.like_count,
                published_at=article.published_at,
                created_at=article.created_at,
            )
        )

    return draft_summaries


@router.get("/{slug}", response_model=Article)
async def get_article(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: User | None = Depends(get_current_user_optional),
) -> Article:
    """Get article by slug."""
    # Get article
    article = await ArticleService.get_article_by_slug(
        db=db,
        slug=slug,
        user_id=current_user.id if current_user else None
    )

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    # Increment view count for published articles
    if article.status == "published":
        await ArticleService.increment_view_count(db=db, article_id=article.id)
        article.view_count += 1  # Update local copy

    # Convert author to UserSummary
    author_summary = UserSummary(
        id=article.author.id,
        username=article.author.email.split("@")[0],
        display_name=article.author.display_name,
        avatar_url=None,
    )

    return Article(
        id=article.id,
        title=article.title,
        slug=article.slug,
        summary=article.summary,
        content=article.content,
        tags=article.tags,
        status=article.status,
        author=author_summary,
        view_count=article.view_count,
        like_count=article.like_count,
        published_at=article.published_at,
        created_at=article.created_at,
        updated_at=article.updated_at,
        is_author=current_user and article.author_id == current_user.id,
    )


@router.patch("/{id}", response_model=Article)
async def update_article(
    id: UUID,
    article_update: ArticleUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Article:
    """Update an article."""
    try:
        # Parse content if provided
        content = None
        if article_update.content:
            try:
                content = json.loads(article_update.content) if isinstance(article_update.content, str) else article_update.content
            except json.JSONDecodeError:
                # If it's not JSON, create basic structure
                content = {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": article_update.content}]}]}

        # Determine published status from status field
        published = None
        if article_update.status:
            published = article_update.status == "published"

        article = await ArticleService.update_article(
            db=db,
            article_id=id,
            user_id=current_user.id,
            title=article_update.title,
            content=content,
            summary=article_update.summary,
            tags=article_update.tags,
            published=published,
        )

        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found or you don't have permission to edit it",
            )

        # Convert author to UserSummary
        author_summary = UserSummary(
            id=article.author.id,
            username=article.author.email.split("@")[0],
            display_name=article.author.display_name,
            avatar_url=None,
        )

        return Article(
            id=article.id,
            title=article.title,
            slug=article.slug,
            summary=article.summary,
            content=article.content,
            tags=article.tags,
            status=article.status,
            author=author_summary,
            view_count=article.view_count,
            like_count=article.like_count,
            published_at=article.published_at,
            created_at=article.created_at,
            updated_at=article.updated_at,
            is_author=True,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """Delete an article."""
    success = await ArticleService.delete_article(
        db=db, article_id=id, user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found or you don't have permission to delete it",
        )


@router.post("/{id}/publish", response_model=Article)
async def publish_article(
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Article:
    """Publish a draft article."""
    article = await ArticleService.update_article(
        db=db,
        article_id=id,
        user_id=current_user.id,
        published=True,
    )

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found or you don't have permission to publish it",
        )

    # Convert author to UserSummary
    author_summary = UserSummary(
        id=article.author.id,
        username=article.author.email.split("@")[0],
        display_name=article.author.display_name,
        avatar_url=None,
    )

    return Article(
        id=article.id,
        title=article.title,
        slug=article.slug,
        summary=article.summary,
        content=article.content,
        tags=article.tags,
        status=article.status,
        author=author_summary,
        view_count=article.view_count,
        like_count=article.like_count,
        published_at=article.published_at,
        created_at=article.created_at,
        updated_at=article.updated_at,
        is_author=True,
    )


@router.post("/{id}/unpublish", response_model=Article)
async def unpublish_article(
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Article:
    """Unpublish an article (revert to draft)."""
    article = await ArticleService.update_article(
        db=db,
        article_id=id,
        user_id=current_user.id,
        published=False,
    )

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found or you don't have permission to unpublish it",
        )

    # Convert author to UserSummary
    author_summary = UserSummary(
        id=article.author.id,
        username=article.author.email.split("@")[0],
        display_name=article.author.display_name,
        avatar_url=None,
    )

    return Article(
        id=article.id,
        title=article.title,
        slug=article.slug,
        summary=article.summary,
        content=article.content,
        tags=article.tags,
        status=article.status,
        author=author_summary,
        view_count=article.view_count,
        like_count=article.like_count,
        published_at=article.published_at,
        created_at=article.created_at,
        updated_at=article.updated_at,
        is_author=True,
    )