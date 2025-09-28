"""Tag-related API endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db_session
from ..services.tag_service import TagService

router = APIRouter(prefix="/api/tags", tags=["tags"])


# Request/Response models
class TagStats(BaseModel):
    """Tag usage statistics."""

    articles: int
    spaces: int
    experts: int
    totalUsage: int
    weeklyGrowth: Optional[str] = None
    trendingScore: float


class TagResponse(BaseModel):
    """Tag with metadata and statistics."""

    name: str
    description: str
    stats: TagStats
    related: List[str]


class TagDetailResponse(TagResponse):
    """Detailed tag information including top content."""

    topArticles: List[Dict[str, Any]] = []
    topSpaces: List[Dict[str, Any]] = []
    topExperts: List[Dict[str, Any]] = []
    trendHistory: List[Dict[str, Any]] = []


class TagSuggestRequest(BaseModel):
    """Request for tag suggestions."""

    title: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1)


class TagSuggestResponse(BaseModel):
    """Tag suggestions with confidence scores."""

    suggestedTags: List[str]
    confidence: Dict[str, float]


# Endpoints
@router.get("", response_model=Dict[str, List[TagResponse]])
async def get_tags(
    sort: str = Query("popular", regex="^(alphabetical|popular|trending)$"),
    category: str = Query("all", regex="^(all|with_content|with_experts)$"),
    limit: Optional[int] = Query(None, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get all tags with usage statistics.

    Args:
        sort: Sort order (alphabetical, popular, trending)
        category: Filter category (all, with_content, with_experts)
        limit: Maximum number of tags to return
        db: Database session

    Returns:
        Dictionary with 'tags' key containing list of tags
    """
    tags = await TagService.get_all_tags_with_stats(
        db, sort=sort, category=category, limit=limit
    )

    # Convert to response format
    tag_responses = []
    for tag in tags:
        tag_responses.append(
            TagResponse(
                name=tag["name"],
                description=tag["description"],
                stats=TagStats(**tag["stats"]),
                related=tag["related"],
            )
        )

    return {"tags": tag_responses}


@router.get("/{tag}", response_model=TagDetailResponse)
async def get_tag_detail(
    tag: str,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get detailed information about a specific tag.

    Args:
        tag: Tag name
        db: Database session

    Returns:
        Detailed tag information
    """
    tag_data = await TagService.get_tag_stats(db, tag)

    if not tag_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag '{tag}' not found",
        )

    # TODO: Fetch top articles, spaces, and experts with this tag
    # This will be implemented when we have the proper queries

    return TagDetailResponse(
        name=tag_data["name"],
        description=tag_data["description"],
        stats=TagStats(**tag_data["stats"]),
        related=tag_data["related"],
        topArticles=[],  # To be implemented
        topSpaces=[],  # To be implemented
        topExperts=[],  # To be implemented
        trendHistory=[],  # To be implemented
    )


@router.post("/suggest", response_model=TagSuggestResponse)
async def suggest_tags(
    request: TagSuggestRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get tag suggestions based on content.

    Args:
        request: Title and content to analyze
        db: Database session

    Returns:
        Suggested tags with confidence scores
    """
    suggestions = await TagService.suggest_tags(
        request.title,
        request.content,
        limit=5
    )

    # Format response
    suggested_tags = [tag for tag, _ in suggestions]
    confidence = {tag: score for tag, score in suggestions}

    return TagSuggestResponse(
        suggestedTags=suggested_tags,
        confidence=confidence,
    )