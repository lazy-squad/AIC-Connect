from __future__ import annotations

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_user_optional, get_current_user_required, get_db_session
from ..models import User, Space as SpaceModel
from ..schemas import (
    MemberListResponse,
    Space,
    SpaceArticleListResponse,
    SpaceCreate,
    SpaceListResponse,
    SpaceSummary,
    SpaceUpdate,
    UserSummary,
)
from ..services import SpaceService

router = APIRouter(prefix="/api/spaces", tags=["spaces"])


@router.post("", response_model=Space, status_code=status.HTTP_201_CREATED)
async def create_space(
    data: SpaceCreate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user_required)],
):
    """Create new space"""
    space = await SpaceService.create_space(
        db=db,
        owner_id=current_user.id,
        data=data
    )

    # Convert to response model
    return Space(
        id=space.id,
        name=space.name,
        slug=space.slug,
        description=space.description,
        tags=space.tags,
        visibility=space.visibility,
        memberCount=space.member_count,
        articleCount=space.article_count,
        createdAt=space.created_at,
        updatedAt=space.updated_at,
        owner=UserSummary(
            id=current_user.id,
            username=current_user.email.split("@")[0],
            displayName=current_user.display_name,
            avatarUrl=None
        ),
        isMember=True,
        memberRole="owner"
    )


@router.get("", response_model=SpaceListResponse)
async def list_spaces(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    tags: list[str] = Query(default=[]),
    q: str | None = None,
    my_spaces: bool = False,
    skip: int = 0,
    limit: int = Query(20, le=100),
):
    """List spaces"""
    if my_spaces and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for my_spaces"
        )

    spaces, total = await SpaceService.list_spaces(
        db=db,
        skip=skip,
        limit=limit,
        tags=tags if tags else None,
        search=q,
        user_id=current_user.id if current_user else None,
        my_spaces=my_spaces
    )

    # Check membership for each space if user is authenticated
    space_summaries = []
    for space in spaces:
        is_member = None
        member_role = None

        if current_user:
            role = await SpaceService.get_member_role(db, space.id, current_user.id)
            if role:
                is_member = True
                member_role = role

        space_summaries.append(SpaceSummary(
            id=space.id,
            name=space.name,
            slug=space.slug,
            description=space.description,
            tags=space.tags,
            visibility=space.visibility,
            memberCount=space.member_count,
            articleCount=space.article_count,
            createdAt=space.created_at,
            owner=UserSummary(
                id=space.owner.id,
                username=space.owner.email.split("@")[0],
                displayName=space.owner.display_name,
                avatarUrl=None
            ),
            isMember=is_member,
            memberRole=member_role
        ))

    return SpaceListResponse(
        spaces=space_summaries,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{slug}", response_model=Space)
async def get_space(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
):
    """Get space details"""
    space = await SpaceService.get_space_by_slug(db, slug)

    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found"
        )

    # Check access
    can_access = await SpaceService.can_access_space(
        space=space,
        user_id=current_user.id if current_user else None,
        db=db
    )

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to private space"
        )

    # Check membership
    is_member = None
    member_role = None

    if current_user:
        role = await SpaceService.get_member_role(db, space.id, current_user.id)
        if role:
            is_member = True
            member_role = role

    return Space(
        id=space.id,
        name=space.name,
        slug=space.slug,
        description=space.description,
        tags=space.tags,
        visibility=space.visibility,
        memberCount=space.member_count,
        articleCount=space.article_count,
        createdAt=space.created_at,
        updatedAt=space.updated_at,
        owner=UserSummary(
            id=space.owner.id,
            username=space.owner.email.split("@")[0],
            displayName=space.owner.display_name,
            avatarUrl=None
        ),
        isMember=is_member,
        memberRole=member_role
    )


@router.patch("/{id}", response_model=Space)
async def update_space(
    id: UUID,
    data: SpaceUpdate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user_required)],
):
    """Update space"""
    # Check if user is owner
    space = await db.get(SpaceModel, id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found"
        )

    if space.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can update space"
        )

    updated_space = await SpaceService.update_space(db, id, data)

    return Space(
        id=updated_space.id,
        name=updated_space.name,
        slug=updated_space.slug,
        description=updated_space.description,
        tags=updated_space.tags,
        visibility=updated_space.visibility,
        memberCount=updated_space.member_count,
        articleCount=updated_space.article_count,
        createdAt=updated_space.created_at,
        updatedAt=updated_space.updated_at,
        owner=UserSummary(
            id=current_user.id,
            username=current_user.email.split("@")[0],
            displayName=current_user.display_name,
            avatarUrl=None
        ),
        isMember=True,
        memberRole="owner"
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_space(
    id: UUID,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user_required)],
):
    """Delete space"""
    # Check if user is owner
    space = await db.get(SpaceModel, id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found"
        )

    if space.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can delete space"
        )

    success = await SpaceService.delete_space(db, id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete space"
        )


@router.post("/{id}/join")
async def join_space(
    id: UUID,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user_required)],
):
    """Join a space"""
    # Check if space exists
    space = await db.get(SpaceModel, id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found"
        )

    result = await SpaceService.join_space(db, id, current_user.id)

    if result.get("already_member"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Already a member with role: {result['role']}"
        )

    return {
        "success": True,
        "role": result["role"],
        "joinedAt": None  # Could get from DB if needed
    }


@router.post("/{id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_space(
    id: UUID,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user_required)],
):
    """Leave a space"""
    success = await SpaceService.leave_space(db, id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot leave space - either not a member or you are the owner"
        )


@router.get("/{id}/members", response_model=MemberListResponse)
async def get_space_members(
    id: UUID,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    role: str | None = None,
    skip: int = 0,
    limit: int = Query(20, le=100),
):
    """Get space members"""
    # Check if space exists and user can access
    space = await db.get(SpaceModel, id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found"
        )

    can_access = await SpaceService.can_access_space(
        space=space,
        user_id=current_user.id if current_user else None,
        db=db
    )

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to private space"
        )

    # TODO: Implement member listing in SpaceService
    # For now, return empty response
    return MemberListResponse(
        members=[],
        total=0,
        skip=skip,
        limit=limit
    )


@router.patch("/{id}/members/{user_id}")
async def update_member_role(
    id: UUID,
    user_id: UUID,
    role_data: dict,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user_required)],
):
    """Update member role"""
    # Check if current user is owner or moderator
    current_role = await SpaceService.get_member_role(db, id, current_user.id)

    if current_role not in ["owner", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or moderator can update member roles"
        )

    new_role = role_data.get("role")
    if new_role not in ["moderator", "member"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    success = await SpaceService.update_member_role(db, id, user_id, new_role)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update member role"
        )

    return {"role": new_role}


@router.post("/{id}/articles")
async def share_article_to_space(
    id: UUID,
    article_data: dict,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user_required)],
):
    """Share article to space"""
    article_id = article_data.get("articleId")
    if not article_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="articleId is required"
        )

    space_article = await SpaceService.share_article(
        db=db,
        space_id=id,
        article_id=UUID(article_id),
        user_id=current_user.id
    )

    if not space_article:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot share article - either not a member, article doesn't exist, is not published, or already shared"
        )

    # TODO: Return proper SpaceArticle response
    return {"success": True}


@router.get("/{id}/articles", response_model=SpaceArticleListResponse)
async def get_space_articles(
    id: UUID,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    pinned_first: bool = False,
    skip: int = 0,
    limit: int = Query(20, le=100),
):
    """Get articles in space"""
    # Check if space exists and user can access
    space = await db.get(SpaceModel, id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found"
        )

    can_access = await SpaceService.can_access_space(
        space=space,
        user_id=current_user.id if current_user else None,
        db=db
    )

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to private space"
        )

    # TODO: Implement article listing in SpaceService
    # For now, return empty response
    return SpaceArticleListResponse(
        articles=[],
        total=0,
        skip=skip,
        limit=limit
    )


@router.patch("/{id}/articles/{article_id}")
async def update_space_article(
    id: UUID,
    article_id: UUID,
    pin_data: dict,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user_required)],
):
    """Pin/unpin article"""
    # Check if current user is owner or moderator
    current_role = await SpaceService.get_member_role(db, id, current_user.id)

    if current_role not in ["owner", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or moderator can pin articles"
        )

    # TODO: Implement pinning in SpaceService
    return {"pinned": pin_data.get("pinned")}


@router.delete("/{id}/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_article_from_space(
    id: UUID,
    article_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user_required)],
):
    """Remove article from space"""
    # TODO: Check permissions and implement removal
    pass