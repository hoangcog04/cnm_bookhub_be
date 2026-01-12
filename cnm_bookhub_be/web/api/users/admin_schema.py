"""User management schemas for admin."""

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserAdminDTO(BaseModel):
    """User DTO for admin panel - list view."""

    id: uuid.UUID
    full_name: str | None = None
    email: str
    phone_number: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @property
    def role(self) -> str:
        """Compute role based on is_superuser."""
        return "ADMIN" if self.is_superuser else "USER"


class UserAdminDetailDTO(BaseModel):
    """User DTO for admin panel - detail view."""

    id: uuid.UUID
    full_name: str | None = None
    email: str
    phone_number: str | None = None
    avatar_url: str | None = None
    address_detail: str | None = None
    ward_code: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @property
    def role(self) -> str:
        """Compute role based on is_superuser."""
        return "ADMIN" if self.is_superuser else "USER"


class UserAdminUpdateDTO(BaseModel):
    """User DTO for admin to update user."""

    full_name: str | None = None
    phone_number: str | None = None
    role: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None


class UserAdminListResponse(BaseModel):
    """Paginated user list response for admin."""

    items: list[UserAdminDTO]
    totalPage: int
