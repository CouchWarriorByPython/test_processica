import pytest

from src.core.enums import ValidationStatus
from src.services.shipengine_client import ShipEngineClient
from tests.constants import AddressData, ValidationMessages
from tests.factories.address_factory import create_test_address


class TestShipEngineClient:
    @pytest.fixture
    def client(self) -> ShipEngineClient:
        return ShipEngineClient()

    async def test_validate_valid_address_returns_verified(self, client: ShipEngineClient) -> None:
        address = create_test_address()

        result = await client.validate_address(address)

        assert result.status == ValidationStatus.VERIFIED
        assert result.matched_address is not None
        assert result.messages is None

    async def test_validate_address_normalizes_fields(self, client: ShipEngineClient) -> None:
        address = create_test_address()

        result = await client.validate_address(address)

        assert result.matched_address is not None
        assert result.matched_address["city_locality"] == AddressData.CITY_DEFAULT.upper()
        assert result.matched_address["state_province"] == AddressData.STATE_DEFAULT.upper()
        assert result.matched_address["country_code"] == AddressData.COUNTRY_CODE_US.upper()

    async def test_validate_invalid_postal_code_returns_error(
        self, client: ShipEngineClient
    ) -> None:
        address = create_test_address(postal_code=AddressData.POSTAL_CODE_INVALID)

        result = await client.validate_address(address)

        assert result.status == ValidationStatus.ERROR
        assert result.messages is not None
        assert any(ValidationMessages.INVALID_POSTAL_CODE in m["message"] for m in result.messages)

    async def test_validate_po_box_returns_warning(self, client: ShipEngineClient) -> None:
        address = create_test_address(address_line1=AddressData.ADDRESS_LINE1_PO_BOX)

        result = await client.validate_address(address)

        assert result.status == ValidationStatus.WARNING
        assert result.messages is not None
        assert any(ValidationMessages.PO_BOX_WARNING in m["message"] for m in result.messages)

    async def test_validate_missing_address_line1_returns_error(
        self, client: ShipEngineClient
    ) -> None:
        address = create_test_address(address_line1="")

        result = await client.validate_address(address)

        assert result.status == ValidationStatus.ERROR
        assert result.messages is not None
