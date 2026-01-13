from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cnm_bookhub_be.db.base import Base

if TYPE_CHECKING:
    from cnm_bookhub_be.db.models.provinces import Province
    from cnm_bookhub_be.db.models.users import User


class Ward(Base):
    """Represents a ward entity."""

    __tablename__ = "wards"

    code: Mapped[str] = mapped_column(String(length=20), primary_key=True)
    province_code: Mapped[str] = mapped_column(
        String(length=20),
        ForeignKey("provinces.code"),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    # Relationships
    province: Mapped["Province"] = relationship("Province", back_populates="wards")
    users: Mapped[list["User"]] = relationship("User", back_populates="ward")

