import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cnm_bookhub_be.db.base import Base

if TYPE_CHECKING:
    from cnm_bookhub_be.db.models.users import User


class SocialAccount(Base):
    """Represents a social account entity."""

    __tablename__ = "social_accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(length=50), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(length=255), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="social_accounts")

