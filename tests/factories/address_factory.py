import uuid
from datetime import UTC, datetime
from typing import Any

from polyfactory.factories.pydantic_factory import ModelFactory

from src.core.enums import ValidationStatus
from src.db.models.address import Address
from src.schemas.address import AddressCreate
from tests.constants import AddressData


class AddressCreateFactory(ModelFactory):
    __model__ = AddressCreate

    name = AddressData.NAME_DEFAULT
    company_name = AddressData.COMPANY_DEFAULT
    phone = AddressData.PHONE_DEFAULT
    address_line1 = AddressData.ADDRESS_LINE1_DEFAULT
    city_locality = AddressData.CITY_DEFAULT
    state_province = AddressData.STATE_DEFAULT
    postal_code = AddressData.POSTAL_CODE_DEFAULT
    country_code = AddressData.COUNTRY_CODE_US


def create_test_address(
    *,
    id: uuid.UUID | None = None,
    validation_status: ValidationStatus = ValidationStatus.PENDING,
    **kwargs: Any,
) -> Address:
    defaults: dict[str, Any] = {
        "id": id or uuid.uuid4(),
        "name": AddressData.NAME_DEFAULT,
        "company_name": AddressData.COMPANY_DEFAULT,
        "phone": AddressData.PHONE_DEFAULT,
        "address_line1": AddressData.ADDRESS_LINE1_DEFAULT,
        "address_line2": AddressData.ADDRESS_LINE2_DEFAULT,
        "address_line3": None,
        "city_locality": AddressData.CITY_DEFAULT,
        "state_province": AddressData.STATE_DEFAULT,
        "postal_code": AddressData.POSTAL_CODE_DEFAULT,
        "country_code": AddressData.COUNTRY_CODE_US,
        "validation_status": validation_status,
        "validated_at": None,
        "created_at": datetime.now(UTC),
        "updated_at": None,
    }
    defaults.update(kwargs)

    address = Address()
    for key, value in defaults.items():
        setattr(address, key, value)

    return address
