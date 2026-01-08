from typing import Any
from unittest.mock import AsyncMock

import pytest

from src.schemas.address import AddressCreate
from tests.constants import AddressData


@pytest.fixture
def sample_address_data() -> dict[str, Any]:
    return {
        "name": AddressData.NAME_DEFAULT,
        "company_name": AddressData.COMPANY_DEFAULT,
        "phone": AddressData.PHONE_DEFAULT,
        "address_line1": AddressData.ADDRESS_LINE1_DEFAULT,
        "address_line2": AddressData.ADDRESS_LINE2_DEFAULT,
        "city_locality": AddressData.CITY_DEFAULT,
        "state_province": AddressData.STATE_DEFAULT,
        "postal_code": AddressData.POSTAL_CODE_DEFAULT,
        "country_code": AddressData.COUNTRY_CODE_US,
    }


@pytest.fixture
def sample_address_create(sample_address_data: dict[str, Any]) -> AddressCreate:
    return AddressCreate(**sample_address_data)


@pytest.fixture
def invalid_address_data() -> dict[str, Any]:
    return {
        "name": AddressData.NAME_DEFAULT,
        "address_line1": AddressData.ADDRESS_LINE1_DEFAULT,
        "city_locality": AddressData.CITY_DEFAULT,
        "state_province": AddressData.STATE_DEFAULT,
        "postal_code": AddressData.POSTAL_CODE_INVALID,
        "country_code": AddressData.COUNTRY_CODE_US,
    }


@pytest.fixture
def mock_arq() -> AsyncMock:
    mock = AsyncMock()
    mock.enqueue_job = AsyncMock(return_value=None)
    return mock
