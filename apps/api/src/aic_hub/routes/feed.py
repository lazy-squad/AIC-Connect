"""Feed API routes for personalized content and discovery."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_user_optional, get_current_user_required, get_db_session
from ..models import User, UserPreferences
from ..services import ActivityService, FeedService

router = APIRouter(prefix="/api/feed", tags=["feed"])


# Pydantic models for request/response
class FeedResponse(BaseModel):
    """Response model for feed endpoints."""

    items: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int
    nextCursor: Optional[str] = None


class TrendingResponse(BaseModel):
    """Response model for trending content."""

    articles: List[Dict[str, Any]] = []
    spaces: List[Dict[str, Any]] = []
    tags: List[Dict[str, Any]] = []


class DiscoveryResponse(BaseModel):
    """Response model for discovery content."""

    category: str
    items: List[Dict[str, Any]]
    refreshAt: str


class ActivityResponse(BaseModel):
    """Response model for activity stream."""

    activities: List[Dict[str, Any]]
    hasMore: bool
    oldestTimestamp: Optional[str] = None


class UserPreferencesUpdate(BaseModel):
    """Request model for updating user preferences."""

    preferredTags: Optional[List[str]] = Field(None, alias="preferred_tags")
    feedView: Optional[str] = Field(None, alias="feed_view")

    class Config:
        populate_by_name = True


class InteractionRequest(BaseModel):
    """Request model for tracking user interactions."""

    type: str  # view, click, share, save
    targetType: str = Field(..., alias="target_type")
    targetId: str = Field(..., alias="target_id")
    duration: Optional[int] = None  # Duration in seconds for view events
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True


@router.get("/", response_model=FeedResponse)
async def get_personalized_feed(
    view: str = Query("latest", description="Feed view type"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    time_range: Optional[str] = Query(None, description="Time range for trending"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> FeedResponse:
    """
    Get personalized feed for the current user.

    Available views:
    - latest: Most recent content
    - trending: Trending content
    - following: Content from followed users (when implemented)
    - recommended: Personalized recommendations
    """
    user_id = current_user.id if current_user else None

    feed_data = await FeedService.get_personalized_feed(
        db=db,
        user_id=user_id,
        view=view,
        tags=tags,
        time_range=time_range,
        skip=skip,
        limit=limit,
    )

    return FeedResponse(**feed_data)


@router.get("/trending", response_model=TrendingResponse)
async def get_trending_content(
    type: str = Query("all", description="Content type to get"),
    time_range: str = Query("24h", description="Time range for calculation"),
    limit: int = Query(10, ge=1, le=50, description="Number of items per type"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> TrendingResponse:
    """
    Get trending content across the platform.

    Content types:
    - articles: Trending articles
    - spaces: Trending spaces
    - tags: Trending tags
    - all: All content types
    """
    trending_items = await FeedService.calculate_trending(
        db=db,
        time_range=time_range,
        content_type=type,
        limit=limit,
    )

    # Organize by type
    response = TrendingResponse()

    for item in trending_items:
        if item["type"] == "article":
            response.articles.append(item)
        elif item["type"] == "space":
            response.spaces.append(item)
        elif item["type"] == "tag":
            response.tags.append(item)

    return response


@router.get("/discover", response_model=DiscoveryResponse)
async def get_discovery_content(
    category: str = Query(..., description="Discovery category"),
    exclude_seen: bool = Query(False, description="Exclude previously seen content"),
    limit: int = Query(10, ge=1, le=50, description="Number of items"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> DiscoveryResponse:
    """
    Get content for discovery.

    Categories:
    - new_users: Recently joined users
    - rising_articles: Articles with high view velocity
    - active_spaces: Spaces with recent activity
    """
    discovery_data = await FeedService.get_discovery_content(
        db=db,
        category=category,
        exclude_seen=exclude_seen,
        limit=limit,
    )

    return DiscoveryResponse(**discovery_data)


@router.get("/activity", response_model=ActivityResponse)
async def get_activity_stream(
    scope: str = Query("all", description="Activity scope"),
    types: Optional[List[str]] = Query(None, description="Activity types to include"),
    since: Optional[datetime] = Query(None, description="Get activities since timestamp"),
    limit: int = Query(50, ge=1, le=100, description="Number of activities"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_required),
) -> ActivityResponse:
    """
    Get activity stream for the current user.

    Scopes:
    - following: Activities from followed users
    - spaces: Activities from joined spaces
    - all: All activities
    """
    activities = await ActivityService.get_activity_stream(
        db=db,
        user_id=current_user.id,
        scope=scope,
        types=types,
        since=since,
        limit=limit,
    )

    # Determine if there are more activities
    has_more = len(activities) == limit
    oldest_timestamp = activities[-1]["timestamp"] if activities else None

    return ActivityResponse(
        activities=activities,
        hasMore=has_more,
        oldestTimestamp=oldest_timestamp,
    )


@router.patch("/preferences", response_model=UserPreferencesUpdate)
async def update_feed_preferences(
    preferences: UserPreferencesUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_required),
) -> UserPreferencesUpdate:
    """Update feed preferences for the current user."""
    # Get or create user preferences
    user_prefs = await db.get(UserPreferences, current_user.id)

    if not user_prefs:
        user_prefs = UserPreferences(user_id=current_user.id)
        db.add(user_prefs)

    # Update preferences
    if preferences.preferredTags is not None:
        user_prefs.preferred_tags = preferences.preferredTags

    if preferences.feedView is not None:
        if preferences.feedView not in ["latest", "trending", "following"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid feed view type",
            )
        user_prefs.feed_view = preferences.feedView

    await db.commit()
    await db.refresh(user_prefs)

    return UserPreferencesUpdate(
        preferred_tags=user_prefs.preferred_tags,
        feed_view=user_prefs.feed_view,
    )


@router.post("/interactions", status_code=status.HTTP_204_NO_CONTENT)
async def track_interaction(
    interaction: InteractionRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_required),
) -> None:
    """
    Track user interactions for recommendations.

    Interaction types:
    - view: User viewed content
    - click: User clicked on content
    - share: User shared content
    - save: User saved content
    """
    # Record the interaction as an activity
    action_map = {
        "view": f"{interaction.targetType}_viewed",
        "click": f"{interaction.targetType}_clicked",
        "share": f"{interaction.targetType}_shared",
        "save": f"{interaction.targetType}_saved",
    }

    action = action_map.get(interaction.type)
    if not action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid interaction type",
        )

    # Create metadata with duration if provided
    metadata = interaction.metadata or {}
    if interaction.duration:
        metadata["duration_seconds"] = interaction.duration

    await ActivityService.record_activity(
        db=db,
        actor_id=current_user.id,
        action=action,
        target_type=interaction.targetType,
        target_id=UUID(interaction.targetId),
        metadata=metadata,
    )

    return None


@router.get("/recommendations", response_model=FeedResponse)
async def get_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_required),
) -> FeedResponse:
    """Get personalized content recommendations for the current user."""
    articles = await FeedService.get_recommendations(
        db=db,
        user_id=current_user.id,
        limit=limit,
    )

    # Format as feed response
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

    return FeedResponse(
        items=items,
        total=len(items),
        skip=0,
        limit=limit,
        nextCursor=None,
    )