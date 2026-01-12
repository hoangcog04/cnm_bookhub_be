import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cnm_bookhub_be.db.base import Base

if TYPE_CHECKING:
    from cnm_bookhub_be.db.models.order_items import OrderItem
    from cnm_bookhub_be.db.models.users import User


class OrderStatus(StrEnum):
    REQUIRE_PAYMENT = "require_payment"  # wait for checkout
    WAITING_FOR_CONFIRMATION = "waiting_for_confirmation"  # waiting for confirmation
    DELIVERY_IN_PROGRESS = "delivery_in_progress"  # delivery in progress
    CANCELLED = "cancelled"  # cancelled by user or admin
    COMPLETED = "completed"  # after delivery


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    address_at_purchase: Mapped[str] = mapped_column(Text, nullable=False)
    payment_intent_id: Mapped[str] = mapped_column(String(length=255), nullable=True)
    total_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order"
    )
