import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends
from httpx_oauth.clients.github import GitHubOAuth2
from httpx_oauth.clients.google import GoogleOAuth2
from pydantic import SecretStr

from cnm_bookhub_be.db.dao.order_dao import OrderDAO
from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.orders import Order
from cnm_bookhub_be.db.models.users import (
    User,  # type: ignore
    UserCreate,  # type: ignore
    UserProfileUpdate,  # type: ignore
    UserRead,  # type: ignore
    UserUpdate,  # type: ignore
    UserListResponse, # type: ignore
    UserReadWithWard, # type: ignore
    api_users,  # type: ignore
    auth_jwt,  # type: ignore
    current_active_user,  # type: ignore
)
from cnm_bookhub_be.db.dao.user_dao import UserDAO
from cnm_bookhub_be.services.oauth_service import (
    github_oauth_client,
    google_oauth_client,
)
from cnm_bookhub_be.settings import settings
from cnm_bookhub_be.web.api.orders.schema import OrderHistoryDTO
from cnm_bookhub_be.web.api.users.custom_oauth import get_custom_oauth_router
from cnm_bookhub_be.web.api.users.admin_routes import admin_users_router

router = APIRouter()

# Include admin routes
router.include_router(admin_users_router)

router.include_router(
    api_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    api_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    api_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    api_users.get_auth_router(auth_jwt), prefix="/auth/jwt", tags=["auth"]
)
router.include_router(
    get_custom_oauth_router(
        google_oauth_client,
        auth_jwt,
        settings.users_secret,
        associate_by_email=True,
        is_verified_by_default=True,
    ),
    prefix="/auth/google",
    tags=["auth"],
)

router.include_router(
    get_custom_oauth_router(
        github_oauth_client,
        auth_jwt,
        settings.users_secret,
        associate_by_email=True,
        is_verified_by_default=True,
    ),
    prefix="/auth/github",
    tags=["auth"],
)


@router.get(
    "/users/me/history_order", response_model=list[OrderHistoryDTO], tags=["users"]
)
async def get_my_order_history(
    user: User = Depends(current_active_user),  # type: ignore
    order_dao: OrderDAO = Depends(),
) -> list[Order]:
    """Get current user's order history with order items and book details."""
    return await order_dao.get_history_order(user.id)


@router.get(
    "/users/me/history_order_by_status",
    response_model=list[OrderHistoryDTO],
    tags=["users"],
)
async def get_my_order_history_by_status(
    status: str,
    user: User = Depends(current_active_user),  # type: ignore
    order_dao: OrderDAO = Depends(),
) -> list[Order]:
    """
    Get current user's order history filtered by status.

    Valid status values:
    - pending (Chờ xử lý)
    - processing (Đã xử lý)
    - shipped (Đang vận chuyển)
    - completed (Thành công)
    - cancelled (Đã hủy)
    """
    return await order_dao.get_orders_by_user_and_status(user.id, status)


@router.patch("/users/me/profile", response_model=UserRead, tags=["users"])
async def update_my_profile(
    profile_data: UserProfileUpdate,
    user: User = Depends(current_active_user),  # type: ignore
    session: "AsyncSession" = Depends(get_db_session),  # type: ignore
) -> User:
    """Update current user's profile information.

    Only allows updating profile fields (full_name, phone_number, avatar_url,
    ward_code, address_detail). For password/email changes, use dedicated endpoints.
    """
    from sqlalchemy.ext.asyncio import AsyncSession

    # Update only fields that are provided (not None)
    update_data = profile_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@router.get("/users/all", response_model=UserListResponse, tags=["users"])
async def get_all_users(
    limit: int = 10,
    offset: int = 1,
    user_name: Optional[str] = None,
    user_dao: UserDAO = Depends(),
    current_user: User = Depends(current_active_user),
) -> UserListResponse:
    """List all users (Admin only)."""
    if not current_user.is_superuser:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    users, total_pages = await user_dao.get_all_users(limit, offset, user_name)
    return UserListResponse(items=users, totalPage=total_pages)


@router.get("/users/admin/{id}", response_model=UserReadWithWard, tags=["users"])
async def get_user_detail(
    id: uuid.UUID,
    user_dao: UserDAO = Depends(),
    current_user: User = Depends(current_active_user),
) -> User:
    """Get user details (Admin only)."""
    if not current_user.is_superuser:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = await user_dao.get_user_by_id(id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/users/{id}", status_code=204, tags=["users"])
async def delete_user(
    id: uuid.UUID,
    user_dao: UserDAO = Depends(),
    current_user: User = Depends(current_active_user),
):
    """Delete user (Admin only)."""
    if not current_user.is_superuser:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if current_user.id == id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    success = await user_dao.delete_user(id)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    
    from fastapi import Response
    return Response(status_code=204)


router.include_router(
    api_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
