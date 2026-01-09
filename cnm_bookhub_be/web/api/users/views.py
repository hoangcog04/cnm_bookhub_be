from fastapi import APIRouter, Depends
from pydantic import SecretStr
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.github import GitHubOAuth2
from cnm_bookhub_be.settings import settings
from cnm_bookhub_be.services.oauth_service import google_oauth_client, github_oauth_client
from cnm_bookhub_be.db.models.users import (
    UserCreate,  # type: ignore
    UserRead,  # type: ignore
    UserUpdate,  # type: ignore
    api_users,  # type: ignore
    auth_jwt,  # type: ignore
    current_active_user,  # type: ignore
    User,  # type: ignore
)
from cnm_bookhub_be.db.dao.order_dao import OrderDAO
from cnm_bookhub_be.db.models.orders import Order
from cnm_bookhub_be.web.api.orders.schema import OrderHistoryDTO

router = APIRouter()

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
    api_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
router.include_router(
    api_users.get_auth_router(auth_jwt), prefix="/auth/jwt", tags=["auth"]
)
router.include_router(
    api_users.get_oauth_router(
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
    api_users.get_oauth_router(
        github_oauth_client,
        auth_jwt,
        settings.users_secret,
        associate_by_email=True,
        is_verified_by_default=True,
    ),
    prefix="/auth/github",
    tags=["auth"],
)


@router.get("/users/me/history_order", response_model=list[OrderHistoryDTO], tags=["users"])
async def get_my_order_history(
    user: User = Depends(current_active_user),  # type: ignore
    order_dao: OrderDAO = Depends(),
) -> list[Order]:
    """Get current user's order history with order items and book details."""
    return await order_dao.get_history_order(user.id)


@router.get("/users/me/history_order_by_status", response_model=list[OrderHistoryDTO], tags=["users"])
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

