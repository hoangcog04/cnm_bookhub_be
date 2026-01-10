import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cnm_bookhub_be.db.base import Base

if TYPE_CHECKING:
    from cnm_bookhub_be.db.models.books import Book
    from cnm_bookhub_be.db.models.orders import Order


class OrderItem(Base):
    """Represents an order item entity."""

    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("books.id"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_purchase: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    book: Mapped["Book"] = relationship("Book", back_populates="order_items")
