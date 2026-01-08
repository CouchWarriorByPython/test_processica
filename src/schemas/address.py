from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.core.enums import ValidationStatus


class AddressBase(BaseModel):
    name: str | None = Field(None, max_length=255, examples=["John Doe"])
    company_name: str | None = Field(None, max_length=255, examples=["Acme Inc"])
    phone: str | None = Field(None, max_length=50, examples=["+1-555-123-4567"])
    address_line1: str = Field(..., max_length=500, examples=["123 Main St"])
    address_line2: str | None = Field(None, max_length=500, examples=["Apt 4B"])
    address_line3: str | None = Field(None, max_length=500)
    city_locality: str = Field(..., max_length=255, examples=["Austin"])
    state_province: str = Field(..., max_length=100, examples=["TX"])
    postal_code: str = Field(..., max_length=50, examples=["78701"])
    country_code: str = Field(
        ..., min_length=2, max_length=2, examples=["US"], description="ISO 3166-1 alpha-2"
    )


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    company_name: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    address_line1: str | None = Field(None, max_length=500)
    address_line2: str | None = Field(None, max_length=500)
    address_line3: str | None = Field(None, max_length=500)
    city_locality: str | None = Field(None, max_length=255)
    state_province: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=50)
    country_code: str | None = Field(None, min_length=2, max_length=2)


class ValidationResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: ValidationStatus
    matched_address: dict[str, Any] | None = None
    messages: list[dict[str, Any]] | None = None
    created_at: datetime


class AddressResponse(AddressBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    validation_status: ValidationStatus
    validated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    validation_results: list[ValidationResultResponse] = Field(default_factory=list)


class AddressListResponse(BaseModel):
    items: list[AddressResponse]
    total: int
    limit: int
    offset: int
