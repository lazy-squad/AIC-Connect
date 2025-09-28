from __future__ import annotations

import uuid
from typing import Optional

from slugify import slugify
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Activity, Article, Space, SpaceArticle, User, space_members
from ..schemas import SpaceCreate, SpaceUpdate
from .activity_service import ActivityService

# Import services conditionally to avoid circular imports
try:
    from .tag_service import TagService
    from .search_service import SearchService
except ImportError:
    # Services not available yet
    TagService = None
    SearchService = None


class SpaceService:
    @staticmethod
    async def create_space(
        db: AsyncSession,
        owner_id: uuid.UUID,
        data: SpaceCreate
    ) -> Space:
        """Create space with owner as first member"""
        # Generate unique slug
        base_slug = slugify(data.name)
        slug = base_slug
        counter = 1

        while True:
            existing = await db.execute(
                select(Space).where(Space.slug == slug)
            )
            if not existing.scalar_one_or_none():
                break
            slug = f"{base_slug}-{counter}"
            counter += 1

        space = Space(
            name=data.name,
            slug=slug,
            description=data.description,
            tags=data.tags,
            visibility=data.visibility,
            owner_id=owner_id,
            member_count=1,
            article_count=0
        )

        db.add(space)
        await db.flush()

        # Add owner as first member with owner role
        await db.execute(
            space_members.insert().values(
                space_id=space.id,
                user_id=owner_id,
                role="owner"
            )
        )

        await db.commit()
        await db.refresh(space)

        # Update tag usage for public spaces
        if TagService and space.visibility == "public" and space.tags:
            for tag in space.tags:
                await TagService.update_tag_usage(db, tag, "space", delta=1)

        # Update search index for public spaces
        if SearchService and space.visibility == "public":
            await SearchService.update_search_index(
                db=db,
                entity_type="space",
                entity_id=space.id,
                title=space.name,
                content=space.description or "",
                tags=space.tags or []
            )

        # Record activity
        await ActivityService.record_activity(
            db=db,
            actor_id=owner_id,
            action=ActivityService.SPACE_CREATED,
            target_type=ActivityService.TARGET_SPACE,
            target_id=space.id,
            metadata={"space_name": space.name, "visibility": space.visibility}
        )

        return space

    @staticmethod
    async def can_access_space(
        space: Space,
        user_id: uuid.UUID | None,
        db: AsyncSession
    ) -> bool:
        """Check if user can access space (public or member)"""
        if space.visibility == "public":
            return True

        if not user_id:
            return False

        # Check if user is member
        result = await db.execute(
            select(space_members).where(
                and_(
                    space_members.c.space_id == space.id,
                    space_members.c.user_id == user_id
                )
            )
        )

        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_member_role(
        db: AsyncSession,
        space_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> str | None:
        """Get user's role in space"""
        result = await db.execute(
            select(space_members.c.role).where(
                and_(
                    space_members.c.space_id == space_id,
                    space_members.c.user_id == user_id
                )
            )
        )

        row = result.scalar_one_or_none()
        return row if row else None

    @staticmethod
    async def join_space(
        db: AsyncSession,
        space_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str = "member"
    ) -> dict:
        """Add user to space"""
        # Check if already member
        existing = await SpaceService.get_member_role(db, space_id, user_id)
        if existing:
            return {"already_member": True, "role": existing}

        # Add member
        await db.execute(
            space_members.insert().values(
                space_id=space_id,
                user_id=user_id,
                role=role
            )
        )

        # Update member count
        await db.execute(
            select(Space).where(Space.id == space_id).with_for_update()
        )
        await db.execute(
            Space.__table__.update()
            .where(Space.id == space_id)
            .values(member_count=Space.member_count + 1)
        )

        await db.commit()

        # Record activity
        await ActivityService.record_activity(
            db=db,
            actor_id=user_id,
            action=ActivityService.SPACE_JOINED,
            target_type=ActivityService.TARGET_SPACE,
            target_id=space_id,
            metadata={"role": role}
        )

        return {"success": True, "role": role}

    @staticmethod
    async def leave_space(
        db: AsyncSession,
        space_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Remove user from space (not owner)"""
        # Check if user is owner
        space = await db.get(Space, space_id)
        if not space or space.owner_id == user_id:
            return False

        # Check if member
        role = await SpaceService.get_member_role(db, space_id, user_id)
        if not role:
            return False

        # Remove member
        await db.execute(
            space_members.delete().where(
                and_(
                    space_members.c.space_id == space_id,
                    space_members.c.user_id == user_id
                )
            )
        )

        # Update member count
        await db.execute(
            Space.__table__.update()
            .where(Space.id == space_id)
            .values(member_count=Space.member_count - 1)
        )

        await db.commit()

        # Record activity
        await ActivityService.record_activity(
            db=db,
            actor_id=user_id,
            action=ActivityService.SPACE_LEFT,
            target_type=ActivityService.TARGET_SPACE,
            target_id=space_id,
            metadata={}
        )

        return True

    @staticmethod
    async def share_article(
        db: AsyncSession,
        space_id: uuid.UUID,
        article_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> SpaceArticle | None:
        """Share article to space"""
        # Check if user is member
        role = await SpaceService.get_member_role(db, space_id, user_id)
        if not role:
            return None

        # Check if article exists and is published
        article = await db.get(Article, article_id)
        if not article or article.status != "published":
            return None

        # Check if already shared
        existing = await db.execute(
            select(SpaceArticle).where(
                and_(
                    SpaceArticle.space_id == space_id,
                    SpaceArticle.article_id == article_id
                )
            )
        )
        if existing.scalar_one_or_none():
            return None

        # Share article
        space_article = SpaceArticle(
            space_id=space_id,
            article_id=article_id,
            added_by=user_id,
            pinned=False
        )

        db.add(space_article)

        # Update article count
        await db.execute(
            Space.__table__.update()
            .where(Space.id == space_id)
            .values(article_count=Space.article_count + 1)
        )

        await db.commit()
        await db.refresh(space_article)

        return space_article

    @staticmethod
    async def update_member_role(
        db: AsyncSession,
        space_id: uuid.UUID,
        user_id: uuid.UUID,
        new_role: str
    ) -> bool:
        """Update member role (cannot change owner)"""
        # Check current role
        current_role = await SpaceService.get_member_role(db, space_id, user_id)
        if not current_role or current_role == "owner":
            return False

        # Update role
        await db.execute(
            space_members.update()
            .where(
                and_(
                    space_members.c.space_id == space_id,
                    space_members.c.user_id == user_id
                )
            )
            .values(role=new_role)
        )

        await db.commit()
        return True

    @staticmethod
    async def list_spaces(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        tags: list[str] | None = None,
        search: str | None = None,
        user_id: uuid.UUID | None = None,
        my_spaces: bool = False
    ) -> tuple[list[Space], int]:
        """List spaces with filters"""
        query = select(Space).options(selectinload(Space.owner))

        # Filter by visibility or membership
        if user_id and my_spaces:
            # Get user's spaces
            subquery = (
                select(space_members.c.space_id)
                .where(space_members.c.user_id == user_id)
            )
            query = query.where(Space.id.in_(subquery))
        else:
            # Public spaces + user's private spaces
            if user_id:
                member_subquery = (
                    select(space_members.c.space_id)
                    .where(space_members.c.user_id == user_id)
                )
                query = query.where(
                    or_(
                        Space.visibility == "public",
                        Space.id.in_(member_subquery)
                    )
                )
            else:
                query = query.where(Space.visibility == "public")

        # Filter by tags
        if tags:
            for tag in tags:
                query = query.where(Space.tags.contains([tag]))

        # Search
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Space.name.ilike(search_term),
                    Space.description.ilike(search_term)
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Space.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        spaces = result.scalars().all()

        return spaces, total

    @staticmethod
    async def get_space_by_slug(
        db: AsyncSession,
        slug: str
    ) -> Space | None:
        """Get space by slug"""
        result = await db.execute(
            select(Space)
            .options(selectinload(Space.owner))
            .where(Space.slug == slug)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def update_space(
        db: AsyncSession,
        space_id: uuid.UUID,
        data: SpaceUpdate
    ) -> Space | None:
        """Update space details"""
        space = await db.get(Space, space_id)
        if not space:
            return None

        # Store original state for tag and search updates
        original_tags = space.tags.copy() if space.tags else []
        original_visibility = space.visibility
        original_public = original_visibility == "public"

        # Update fields if provided
        if data.name is not None:
            space.name = data.name
        if data.description is not None:
            space.description = data.description
        if data.tags is not None:
            space.tags = data.tags
        if data.visibility is not None:
            space.visibility = data.visibility

        await db.commit()
        await db.refresh(space)

        # Handle tag usage updates
        current_public = space.visibility == "public"
        current_tags = space.tags if space.tags else []

        # If visibility changed
        if TagService and original_public != current_public:
            if current_public:  # Now public
                # Add tag usage for all current tags
                for tag in current_tags:
                    await TagService.update_tag_usage(db, tag, "space", delta=1)
            else:  # Now private
                # Remove tag usage for all original tags
                for tag in original_tags:
                    await TagService.update_tag_usage(db, tag, "space", delta=-1)

        # If tags changed while public
        elif TagService and current_public:
            # Remove old tags
            removed_tags = set(original_tags) - set(current_tags)
            for tag in removed_tags:
                await TagService.update_tag_usage(db, tag, "space", delta=-1)

            # Add new tags
            added_tags = set(current_tags) - set(original_tags)
            for tag in added_tags:
                await TagService.update_tag_usage(db, tag, "space", delta=1)

        # Update search index for public spaces
        if SearchService and current_public:
            await SearchService.update_search_index(
                db=db,
                entity_type="space",
                entity_id=space.id,
                title=space.name,
                content=space.description or "",
                tags=space.tags or []
            )
        elif SearchService and original_public and not current_public:
            # Remove from search index if made private
            await SearchService.delete_from_search_index(
                db=db,
                entity_type="space",
                entity_id=space.id
            )

        return space

    @staticmethod
    async def delete_space(
        db: AsyncSession,
        space_id: uuid.UUID
    ) -> bool:
        """Delete space and all associations"""
        space = await db.get(Space, space_id)
        if not space:
            return False

        # Store state for cleanup
        was_public = space.visibility == "public"
        space_tags = space.tags if space.tags else []

        await db.delete(space)
        await db.commit()

        # Clean up tag usage and search index
        if was_public:
            # Remove tag usage
            if TagService:
                for tag in space_tags:
                    await TagService.update_tag_usage(db, tag, "space", delta=-1)

            # Remove from search index
            if SearchService:
                await SearchService.delete_from_search_index(
                    db=db,
                    entity_type="space",
                    entity_id=space_id
                )

        return True