import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.enums import ValidationStatus
from src.db.models.base import Base


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str | None] = mapped_column(String(255))
    company_name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    address_line1: Mapped[str] = mapped_column(String(500))
    address_line2: Mapped[str | None] = mapped_column(String(500))
    address_line3: Mapped[str | None] = mapped_column(String(500))
    city_locality: Mapped[str] = mapped_column(String(255))
    state_province: Mapped[str] = mapped_column(String(100))
    postal_code: Mapped[str] = mapped_column(String(50))
    country_code: Mapped[str] = mapped_column(String(2))
    validation_status: Mapped[ValidationStatus] = mapped_column(
        String(20),
        default=ValidationStatus.PENDING,
    )
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )
    validation_results: Mapped[list["ValidationResult"]] = relationship(
        back_populates="address",
        cascade="all, delete-orphan",
        order_by="desc(ValidationResult.created_at)",
    )

    def __repr__(self) -> str:
        return f"<Address {self.id}: {self.address_line1}, {self.city_locality}>"


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    address_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("addresses.id", ondelete="CASCADE"),
    )
    status: Mapped[ValidationStatus] = mapped_column(String(20))
    matched_address: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    messages: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    address: Mapped["Address"] = relationship(back_populates="validation_results")

    def __repr__(self) -> str:
        return f"<ValidationResult {self.id}: {self.status}>"
