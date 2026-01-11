import uuid
from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from cnm_bookhub_be.db.base import Base


class Cart(Base):
    __tablename__ = "cart"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True,
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("books.id"),
        primary_key=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
