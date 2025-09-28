"""Search-related API endpoints."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db_session
from ..services.search_service import SearchService

router = APIRouter(prefix="/api/search", tags=["search"])


# Response models
class SearchHighlights(BaseModel):
    """Highlighted search result snippets."""

    title: Optional[str] = None
    content: Optional[str] = None


class SearchResultItem(BaseModel):
    """Individual search result."""

    type: str  # article, space, user
    score: float
    item: Dict[str, Any]  # Flexible structure for different types


class SearchFacets(BaseModel):
    """Search result facets for filtering."""

    types: Dict[str, int]
    tags: Dict[str, int]


class SearchResponse(BaseModel):
    """Search results with metadata."""

    results: List[SearchResultItem]
    total: int
    facets: SearchFacets
    skip: int
    limit: int
    processingTime: int  # milliseconds


class AutocompleteSuggestion(BaseModel):
    """Autocomplete suggestion."""

    type: str  # query, tag, article, space, user
    text: str
    count: Optional[int] = None
    slug: Optional[str] = None


class AutocompleteResponse(BaseModel):
    """Autocomplete suggestions."""

    suggestions: List[AutocompleteSuggestion]


# Endpoints
@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    type: str = Query("all", regex="^(all|articles|spaces|users)$"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    sort: str = Query("relevance", regex="^(relevance|latest|popular)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Universal search across the platform.

    Args:
        q: Search query (required)
        type: Entity type to search (all, articles, spaces, users)
        tags: Filter results by tags
        sort: Sort order (relevance, latest, popular)
        skip: Pagination offset
        limit: Page size
        db: Database session

    Returns:
        Search results with facets and metadata
    """
    start_time = time.time()

    # Perform search
    search_results = await SearchService.search(
        db,
        query=q,
        search_type=type,
        tags=tags,
        skip=skip,
        limit=limit,
    )

    # Calculate processing time
    processing_time = int((time.time() - start_time) * 1000)

    return SearchResponse(
        results=[
            SearchResultItem(
                type=result["type"],
                score=result["score"],
                item=result["item"],
            )
            for result in search_results["results"]
        ],
        total=search_results["total"],
        facets=SearchFacets(
            types=search_results["facets"]["types"],
            tags=search_results["facets"]["tags"],
        ),
        skip=skip,
        limit=limit,
        processingTime=processing_time,
    )


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(
    q: str = Query(..., min_length=2, max_length=50, description="Partial query"),
    limit: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get search suggestions as user types.

    Args:
        q: Partial query (minimum 2 characters)
        limit: Maximum suggestions (default: 5)
        db: Database session

    Returns:
        List of suggestions
    """
    suggestions = await SearchService.autocomplete(db, q, limit)

    return AutocompleteResponse(
        suggestions=[
            AutocompleteSuggestion(
                type=s["type"],
                text=s["text"],
                count=s.get("count"),
                slug=s.get("slug"),
            )
            for s in suggestions
        ]
    )


@router.post("/index", status_code=status.HTTP_202_ACCEPTED)
async def update_search_index(
    db: AsyncSession = Depends(get_db_session),
):
    """
    Manually trigger search index update.

    This endpoint is for admin use only to force a search index rebuild.
    In production, this would be protected by admin authentication.

    Args:
        db: Database session

    Returns:
        202 Accepted status
    """
    # TODO: Implement admin authentication check
    # TODO: Trigger background job to rebuild search index

    return {"message": "Search index update triggered"}