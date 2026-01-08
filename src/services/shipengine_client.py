import asyncio
from dataclasses import dataclass
from typing import Any

from src.core.enums import ValidationStatus
from src.db.models.address import Address


@dataclass
class ValidationResponse:
    status: ValidationStatus
    matched_address: dict[str, Any] | None = None
    messages: list[dict[str, Any]] | None = None


class ShipEngineClient:
    async def validate_address(self, address: Address) -> ValidationResponse:
        await asyncio.sleep(0.5)

        errors = self._validate_fields(address)

        if errors:
            return ValidationResponse(
                status=ValidationStatus.ERROR,
                messages=errors,
            )

        warnings: list[dict[str, Any]] = []
        if address.address_line1 and "PO BOX" in address.address_line1.upper():
            warnings.append(
                {
                    "code": "po_box_detected",
                    "type": "warning",
                    "message": "Address appears to be a PO Box",
                }
            )

        status = ValidationStatus.WARNING if warnings else ValidationStatus.VERIFIED
        return ValidationResponse(
            status=status,
            matched_address={
                "name": address.name,
                "company_name": address.company_name,
                "phone": address.phone,
                "address_line1": self._normalize_street(address.address_line1),
                "address_line2": address.address_line2,
                "address_line3": address.address_line3,
                "city_locality": address.city_locality.upper(),
                "state_province": address.state_province.upper(),
                "postal_code": self._normalize_postal_code(
                    address.postal_code, address.country_code
                ),
                "country_code": address.country_code.upper(),
            },
            messages=warnings or None,
        )

    def _validate_fields(self, address: Address) -> list[dict[str, Any]]:
        errors: list[dict[str, Any]] = []

        if not address.address_line1:
            errors.append(
                {
                    "code": "address_line1_required",
                    "type": "error",
                    "message": "Address line 1 is required",
                }
            )

        if not address.city_locality:
            errors.append(
                {
                    "code": "city_required",
                    "type": "error",
                    "message": "City is required",
                }
            )

        if not address.postal_code or len(address.postal_code) < 3:
            errors.append(
                {
                    "code": "invalid_postal_code",
                    "type": "error",
                    "message": "Invalid or missing postal code",
                }
            )

        if not address.country_code or len(address.country_code) != 2:
            errors.append(
                {
                    "code": "invalid_country_code",
                    "type": "error",
                    "message": "Country code must be 2 characters (ISO 3166-1 alpha-2)",
                }
            )

        return errors

    def _normalize_street(self, street: str) -> str:
        replacements = {
            " street": " ST",
            " avenue": " AVE",
            " boulevard": " BLVD",
            " road": " RD",
            " drive": " DR",
            " lane": " LN",
            " court": " CT",
        }
        result = street.upper()
        for old, new in replacements.items():
            result = result.replace(old.upper(), new)
        return result

    def _normalize_postal_code(self, postal_code: str, country_code: str) -> str:
        cleaned = postal_code.strip().upper()
        if country_code.upper() == "US" and len(cleaned) == 5:
            return cleaned

        return cleaned
