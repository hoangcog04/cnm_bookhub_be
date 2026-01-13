from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cnm_bookhub_be.db.base import Base

if TYPE_CHECKING:
    from cnm_bookhub_be.db.models.wards import Ward


class Province(Base):
    """Represents a province entity."""

    __tablename__ = "provinces"

    code: Mapped[str] = mapped_column(String(length=20), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    # Relationships
    wards: Mapped[list["Ward"]] = relationship("Ward", back_populates="province")
