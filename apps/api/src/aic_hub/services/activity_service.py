"""Activity service for tracking user actions and generating activity streams."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Activity, Article, Space, User


class ActivityService:
    """Service for managing user activities and activity streams."""

    # Activity action types
    ARTICLE_PUBLISHED = "article_published"
    ARTICLE_UPDATED = "article_updated"
    ARTICLE_LIKED = "article_liked"
    SPACE_CREATED = "space_created"
    SPACE_JOINED = "space_joined"
    SPACE_LEFT = "space_left"
    USER_JOINED = "user_joined"
    USER_FOLLOWED = "user_followed"
    USER_UNFOLLOWED = "user_unfollowed"

    # Target types
    TARGET_ARTICLE = "article"
    TARGET_SPACE = "space"
    TARGET_USER = "user"

    @staticmethod
    async def record_activity(
        db: AsyncSession,
        actor_id: UUID,
        action: str,
        target_type: str,
        target_id: UUID,
        metadata: dict | None = None,
    ) -> Activity:
        """
        Record a user activity for feeds.

        Args:
            db: Database session
            actor_id: User performing the action
            action: Type of action performed
            target_type: Type of target entity
            target_id: ID of target entity
            metadata: Additional activity metadata

        Returns:
            Created activity record
        """
        activity = Activity(
            id=uuid4(),
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            activity_metadata=metadata or {},
        )

        db.add(activity)
        await db.commit()
        await db.refresh(activity)

        return activity

    @staticmethod
    async def get_activity_stream(
        db: AsyncSession,
        user_id: UUID | None,
        scope: str = "all",
        types: List[str] | None = None,
        since: datetime | None = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get activity stream for a user.

        Args:
            db: Database session
            user_id: User ID for filtered activities
            scope: Activity scope (following, spaces, all)
            types: Filter by activity types
            since: Get activities since this timestamp
            limit: Maximum number of activities

        Returns:
            List of formatted activities
        """
        # Base query
        query = select(Activity)

        # Apply scope filters
        if scope == "following" and user_id:
            # TODO: Implement when following system is ready
            # For now, just return user's own activities
            query = query.where(Activity.actor_id == user_id)
        elif scope == "spaces" and user_id:
            # Get activities from user's spaces
            # TODO: Filter by spaces the user is a member of
            query = query.where(
                Activity.target_type == ActivityService.TARGET_SPACE
            )

        # Filter by activity types
        if types:
            query = query.where(Activity.action.in_(types))

        # Filter by timestamp
        if since:
            query = query.where(Activity.created_at > since)

        # Load actor relationship
        query = query.options(selectinload(Activity.actor))

        # Order by creation time
        query = query.order_by(desc(Activity.created_at))

        # Apply limit
        query = query.limit(limit)

        result = await db.execute(query)
        activities = result.scalars().all()

        # Format activities
        formatted_activities = []
        for activity in activities:
            formatted_activity = await ActivityService._format_activity(db, activity)
            if formatted_activity:
                formatted_activities.append(formatted_activity)

        return formatted_activities

    @staticmethod
    async def get_user_activities(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get activities performed by a specific user.

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of activities
            offset: Pagination offset

        Returns:
            List of user activities
        """
        query = select(Activity).where(Activity.actor_id == user_id)
        query = query.options(selectinload(Activity.actor))
        query = query.order_by(desc(Activity.created_at))
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        activities = result.scalars().all()

        formatted_activities = []
        for activity in activities:
            formatted_activity = await ActivityService._format_activity(db, activity)
            if formatted_activity:
                formatted_activities.append(formatted_activity)

        return formatted_activities

    @staticmethod
    async def get_space_activities(
        db: AsyncSession,
        space_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get activities related to a specific space.

        Args:
            db: Database session
            space_id: Space ID
            limit: Maximum number of activities
            offset: Pagination offset

        Returns:
            List of space-related activities
        """
        query = select(Activity).where(
            and_(
                Activity.target_type == ActivityService.TARGET_SPACE,
                Activity.target_id == space_id
            )
        )
        query = query.options(selectinload(Activity.actor))
        query = query.order_by(desc(Activity.created_at))
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        activities = result.scalars().all()

        formatted_activities = []
        for activity in activities:
            formatted_activity = await ActivityService._format_activity(db, activity)
            if formatted_activity:
                formatted_activities.append(formatted_activity)

        return formatted_activities

    @staticmethod
    async def _format_activity(
        db: AsyncSession,
        activity: Activity
    ) -> Dict[str, Any] | None:
        """
        Format an activity for API response.

        Args:
            db: Database session
            activity: Activity to format

        Returns:
            Formatted activity or None if target not found
        """
        # Get target details based on type
        target_data = await ActivityService._get_target_data(
            db, activity.target_type, activity.target_id
        )

        if not target_data:
            return None

        return {
            "id": str(activity.id),
            "actor": {
                "id": str(activity.actor.id),
                "displayName": activity.actor.display_name or activity.actor.email,
                "email": activity.actor.email,
            },
            "action": activity.action,
            "target": {
                "type": activity.target_type,
                "id": str(activity.target_id),
                **target_data
            },
            "timestamp": activity.created_at.isoformat(),
            "metadata": activity.activity_metadata,
        }

    @staticmethod
    async def _get_target_data(
        db: AsyncSession,
        target_type: str,
        target_id: UUID
    ) -> Dict[str, Any] | None:
        """
        Get target entity data for activity formatting.

        Args:
            db: Database session
            target_type: Type of target
            target_id: ID of target

        Returns:
            Target data dictionary or None if not found
        """
        if target_type == ActivityService.TARGET_ARTICLE:
            article = await db.get(Article, target_id)
            if article:
                return {
                    "title": article.title,
                    "slug": article.slug,
                    "summary": article.summary,
                }

        elif target_type == ActivityService.TARGET_SPACE:
            space = await db.get(Space, target_id)
            if space:
                return {
                    "name": space.name,
                    "slug": space.slug,
                    "description": space.description,
                }

        elif target_type == ActivityService.TARGET_USER:
            user = await db.get(User, target_id)
            if user:
                return {
                    "displayName": user.display_name or user.email,
                    "email": user.email,
                }

        return None

    @staticmethod
    async def cleanup_old_activities(
        db: AsyncSession,
        days: int = 90
    ) -> int:
        """
        Clean up old activities from the database.

        Args:
            db: Database session
            days: Delete activities older than this many days

        Returns:
            Number of deleted activities
        """
        from datetime import timedelta

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Delete old activities
        query = select(Activity).where(Activity.created_at < cutoff_date)
        result = await db.execute(query)
        old_activities = result.scalars().all()

        count = len(old_activities)
        for activity in old_activities:
            await db.delete(activity)

        await db.commit()
        return count

    @staticmethod
    async def get_activity_summary(
        db: AsyncSession,
        user_id: UUID,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get summary of user's recent activity.

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to summarize

        Returns:
            Activity summary with counts
        """
        from datetime import timedelta

        since = datetime.now(timezone.utc) - timedelta(days=days)

        # Count activities by type
        query = select(
            Activity.action,
            func.count(Activity.id)
        ).where(
            and_(
                Activity.actor_id == user_id,
                Activity.created_at >= since
            )
        ).group_by(Activity.action)

        result = await db.execute(query)
        activity_counts = {action: count for action, count in result}

        return {
            "period_days": days,
            "since": since.isoformat(),
            "activity_counts": activity_counts,
            "total_activities": sum(activity_counts.values())
        }