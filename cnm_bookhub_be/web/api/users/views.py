from fastapi import APIRouter, Depends
from pydantic import SecretStr
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.github import GitHubOAuth2
from cnm_bookhub_be.settings import settings
from cnm_bookhub_be.services.oauth_service import google_oauth_client, github_oauth_client
from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.users import (
    UserCreate,  # type: ignore
    UserRead,  # type: ignore
    UserUpdate,  # type: ignore
    UserProfileUpdate,  # type: ignore
    api_users,  # type: ignore
    auth_jwt,  # type: ignore
    current_active_user,  # type: ignore
    User,  # type: ignore
)

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
