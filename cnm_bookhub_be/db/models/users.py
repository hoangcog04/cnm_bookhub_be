# type: ignore
import uuid
from typing import TYPE_CHECKING, List, Optional
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase, SQLAlchemyBaseOAuthAccountTableUUID
from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from cnm_bookhub_be.db.models.oauth_account import OAuthAccount
from cnm_bookhub_be.db.base import Base
from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.settings import settings
from fastapi import Request
from cnm_bookhub_be.services.otp_service import OTPService
from cnm_bookhub_be.services.email_service import (
    email_service, 
    TEMPLATE_LINK_VERIFICATION_NAME,
    TEMPLATE_RESET_PASSWORD_NAME
)

from datetime import datetime
from cnm_bookhub_be.web.api.wards.schema import WardDTO
from cnm_bookhub_be.web.api.provinces.schema import ProvinceDTO
if TYPE_CHECKING:
    from cnm_bookhub_be.db.models.orders import Order
    from cnm_bookhub_be.db.models.social_accounts import SocialAccount
    from cnm_bookhub_be.db.models.wards import Ward


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Represents a user entity."""

    __tablename__ = "users"

    full_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(length=20), nullable=True)
    ward_code: Mapped[str | None] = mapped_column(
        String(length=20),
        ForeignKey("wards.code"),
        nullable=True,
    )
    address_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str | None] = mapped_column(String(length=50), nullable=True)

    # Relationships
    ward: Mapped["Ward"] = relationship("Ward", back_populates="users")
    social_accounts: Mapped[list["SocialAccount"]] = relationship(
        "SocialAccount", back_populates="user"
    )
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Represents a read command for a user."""

    full_name: str | None = None
    avatar_url: str | None = None
    phone_number: str | None = None
    ward_code: str | None = None
    address_detail: str | None = None
    role: str | None = None
    is_superuser: bool = False
    is_active: bool = True
    created_at: datetime | None = None


class UserReadWithWard(UserRead):
    """Represents a read command for a user with ward and province."""

    class WardWithProvince(WardDTO):
        province: Optional[ProvinceDTO] = None

    ward: Optional[WardWithProvince] = None


class UserListResponse(schemas.BaseModel):
    """Paginated user list response."""
    items: List[UserReadWithWard]
    totalPage: int


class UserCreate(schemas.BaseUserCreate):
    """Represents a create command for a user."""

    pass


class UserUpdate(schemas.BaseUserUpdate):
    """Represents an update command for a user profile.
    
    Only profile fields should be updated. Password and email changes
    require separate endpoints with proper verification.
    """

    full_name: str | None = None
    avatar_url: str | None = None
    phone_number: str | None = None
    ward_code: str | None = None
    address_detail: str | None = None


class UserProfileUpdate(schemas.BaseModel):
    """Schema for updating user profile only.
    
    This is used for the dedicated /users/me/profile endpoint
    and only includes safe profile fields.
    """

    full_name: str | None = None
    avatar_url: str | None = None
    phone_number: str | None = None
    ward_code: str | None = None
    address_detail: str | None = None


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Manages a user session and its tokens."""

    reset_password_token_secret = settings.users_secret
    verification_token_secret = settings.users_secret

    async def on_after_register(self, user: User, request: Request | None = None) -> None:
        print(f"User {user.id} has registered.")
        # Send OTP
        # We need a session to potentialy save the OTP. 
        # The user_db has a session.
        session = self.user_db.session
        otp_service = OTPService(session)
        print(f"Sending OTP for {user.email}")
        await otp_service.generate_otp(user.email)

        # Trigger link verification flow
        print(f"Requesting verify for {user.email}")
        # This will call on_after_request_verify with the token
        await self.request_verify(user, request)

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        print(f"Sending Verification Link for {user.email}")
        # Construct the verification URL
        # For local dev, we assume localhost:3000 (Frontend) or backend URL if just testing API
        # Let's point to the backend verify endpoint for now or a frontend route
        # Since user asked about "clicking link", usually it goes to FE. 
        # But if no FE, let's point to a backend dummy or just print it.
        # Assuming we want to verify via GET request (which fastapi-users supports)
        # OR we point to a FE page that grabs the token and POSTs to backend.
        
        # Let's generate a full URL. 
        verify_url = f"http://localhost:8000/api/auth/verify?token={token}"
        
        await email_service.send_email(
            template_name=TEMPLATE_LINK_VERIFICATION_NAME,
            to_email=user.email,
            subject="Verify your account",
            template_body={"verify_url": verify_url, "email": user.email, "username": user.email},
        ) 

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        print(f"User {user.id} has forgot their password.")
        # Construct reset password URL
        reset_url = f"http://localhost:8000/reset-password?token={token}"
        
        await email_service.send_email(
            template_name=TEMPLATE_RESET_PASSWORD_NAME,
            to_email=user.email,
            subject="Reset your password",
            template_body={"reset_url": reset_url, "email": user.email, "username": user.email},
        ) 


async def get_user_db(
    session: AsyncSession = Depends(get_db_session),
) -> SQLAlchemyUserDatabase:
    """
    Yield a SQLAlchemyUserDatabase instance.

    :param session: asynchronous SQLAlchemy session.
    :yields: instance of SQLAlchemyUserDatabase.
    """
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> UserManager:
    """
    Yield a UserManager instance.

    :param user_db: SQLAlchemy user db instance
    :yields: an instance of UserManager.
    """
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """
    Return a JWTStrategy in order to instantiate it dynamically.

    :returns: instance of JWTStrategy with provided settings.
    """
    return JWTStrategy(
        secret=settings.users_secret, lifetime_seconds=settings.users_lifetime_seconds
    )


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_jwt = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

backends = [
    auth_jwt,
]

api_users = FastAPIUsers[User, uuid.UUID](get_user_manager, backends)

current_active_user = api_users.current_user(active=True)
