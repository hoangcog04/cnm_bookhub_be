from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cnm_bookhub_be.db.base import Base

if TYPE_CHECKING:
    from cnm_bookhub_be.db.models.books import Book


class Category(Base):
    """Represents a category entity."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    # Relationships
    books: Mapped[list["Book"]] = relationship("Book", back_populates="category")

    @property
    def number_of_books(self) -> int:
        try:
            return len(self.books)
        except Exception:
            return 0
