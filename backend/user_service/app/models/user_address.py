
from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class UserAddress(Base):
    __tablename__ = "user_addresses"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    user_profile_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_profiles.id"),
        nullable=False,
        index=True,
    )

    address_line1: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    address_line2: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    city: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    state: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    postal_code: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    country: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
