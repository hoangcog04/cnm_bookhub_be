"""Admin user management routes."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from cnm_bookhub_be.db.dao.user_dao import UserDAO
from cnm_bookhub_be.db.models.users import User, current_active_user
from cnm_bookhub_be.web.api.users.admin_schema import (
    UserAdminDTO,
    UserAdminDetailDTO,
    UserAdminListResponse,
    UserAdminUpdateDTO,
)

admin_users_router = APIRouter(prefix="/admin/users", tags=["admin-users"])


async def check_admin_permission(user: User = Depends(current_active_user)) -> User:
    """Check if user is admin/superuser."""
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required.",
        )
    return user


@admin_users_router.get("/", response_model=UserAdminListResponse)
async def list_users(
    limit: int = 10,
    offset: int = 1,
    search: Optional[str] = None,
    user_dao: UserDAO = Depends(),
    _: User = Depends(check_admin_permission),
) -> UserAdminListResponse:
    """
    List all users with pagination and search.
    
    Query Parameters:
    - limit: Number of users per page (default: 10)
    - offset: Page number, 1-based (default: 1)
    - search: Search by full_name or email
    """
    users, total_pages = await user_dao.get_all_users(
        limit=limit,
        offset=offset,
        user_name=search,
    )
    return UserAdminListResponse(items=users, totalPage=total_pages)


@admin_users_router.get("/{user_id}", response_model=UserAdminDetailDTO)
async def get_user_detail(
    user_id: uuid.UUID,
    user_dao: UserDAO = Depends(),
    _: User = Depends(check_admin_permission),
) -> User:
    """Get detailed information about a specific user."""
    user = await user_dao.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@admin_users_router.put("/{user_id}", response_model=UserAdminDetailDTO)
async def update_user(
    user_id: uuid.UUID,
    update_data: UserAdminUpdateDTO,
    user_dao: UserDAO = Depends(),
    admin_user: User = Depends(check_admin_permission),
) -> User:
    """
    Update user information.
    
    Admin can update:
    - full_name: User's full name
    - phone_number: User's phone number
    - role: User's role/status
    - is_active: Active status
    - is_superuser: Admin status
    """
    if user_id == admin_user.id and not update_data.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove your own admin status",
        )

    update_dict = update_data.model_dump(exclude_unset=True)
    user = await user_dao.update_user(user_id, **update_dict)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@admin_users_router.patch("/{user_id}/toggle-active", response_model=UserAdminDetailDTO)
async def toggle_user_active(
    user_id: uuid.UUID,
    user_dao: UserDAO = Depends(),
    admin_user: User = Depends(check_admin_permission),
) -> User:
    """Toggle user active/inactive status."""
    user = await user_dao.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself",
        )

    user = await user_dao.update_user(user_id, is_active=not user.is_active)
    return user


@admin_users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    user_dao: UserDAO = Depends(),
    admin_user: User = Depends(check_admin_permission),
) -> None:
    """Delete a user and all associated data."""
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )

    success = await user_dao.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
