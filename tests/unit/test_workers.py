import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.enums import ValidationStatus
from src.services.shipengine_client import ValidationResponse
from src.workers.tasks import validate_address_task
from tests.constants import ValidationStatusValues
from tests.factories.address_factory import create_test_address


class TestValidateAddressTask:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_address(self) -> MagicMock:
        return create_test_address()

    @pytest.fixture
    def mock_validation_response(self) -> ValidationResponse:
        return ValidationResponse(
            status=ValidationStatus.VERIFIED,
            matched_address={"address_line1": "123 MAIN ST"},
            messages=None,
        )

    async def test_validate_address_task_success(
        self,
        mock_session: AsyncMock,
        mock_address: MagicMock,
        mock_validation_response: ValidationResponse,
    ) -> None:
        address_id = str(mock_address.id)

        with (
            patch("src.workers.tasks.get_session") as mock_get_session,
            patch("src.workers.tasks.AddressRepository") as mock_repo_class,
            patch("src.workers.tasks.AddressService") as mock_service_class,
            patch("src.workers.tasks.ShipEngineClient") as mock_client_class,
        ):
            mock_get_session.return_value.__aenter__.return_value = mock_session

            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = mock_address
            mock_repo_class.return_value = mock_repo

            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            mock_client = AsyncMock()
            mock_client.validate_address.return_value = mock_validation_response
            mock_client_class.return_value = mock_client

            result = await validate_address_task({}, address_id)

            assert result["status"] == ValidationStatusValues.VERIFIED
            assert result["address_id"] == address_id
            mock_repo.get_by_id.assert_called_once()
            mock_client.validate_address.assert_called_once_with(mock_address)
            mock_service.save_validation_result.assert_called_once()

    async def test_validate_address_task_not_found_raises_error(
        self,
        mock_session: AsyncMock,
    ) -> None:
        address_id = str(uuid.uuid4())

        with (
            patch("src.workers.tasks.get_session") as mock_get_session,
            patch("src.workers.tasks.AddressRepository") as mock_repo_class,
        ):
            mock_get_session.return_value.__aenter__.return_value = mock_session

            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = None
            mock_repo_class.return_value = mock_repo

            with pytest.raises(ValueError, match="not found"):
                await validate_address_task({}, address_id)

    async def test_validate_address_task_with_validation_error(
        self,
        mock_session: AsyncMock,
        mock_address: MagicMock,
    ) -> None:
        address_id = str(mock_address.id)
        error_response = ValidationResponse(
            status=ValidationStatus.ERROR,
            matched_address=None,
            messages=[{"code": "invalid", "message": "Invalid address"}],
        )

        with (
            patch("src.workers.tasks.get_session") as mock_get_session,
            patch("src.workers.tasks.AddressRepository") as mock_repo_class,
            patch("src.workers.tasks.AddressService") as mock_service_class,
            patch("src.workers.tasks.ShipEngineClient") as mock_client_class,
        ):
            mock_get_session.return_value.__aenter__.return_value = mock_session

            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = mock_address
            mock_repo_class.return_value = mock_repo

            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            mock_client = AsyncMock()
            mock_client.validate_address.return_value = error_response
            mock_client_class.return_value = mock_client

            result = await validate_address_task({}, address_id)

            assert result["status"] == ValidationStatusValues.ERROR
            mock_service.save_validation_result.assert_called_once()
