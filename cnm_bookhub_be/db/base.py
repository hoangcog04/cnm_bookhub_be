from sqlalchemy.orm import DeclarativeBase

from cnm_bookhub_be.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
