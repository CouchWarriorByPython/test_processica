import uuid
from unittest.mock import AsyncMock

import pytest

from src.core.enums import ValidationStatus
from src.core.exceptions import AddressNotFoundError
from src.schemas.address import AddressCreate, AddressUpdate
from src.services.address_service import AddressService
from tests.constants import AddressData, TaskNames
from tests.factories.address_factory import create_test_address


class TestAddressService:
    @pytest.fixture
    def mock_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_arq(self) -> AsyncMock:
        mock = AsyncMock()
        mock.enqueue_job = AsyncMock()
        return mock

    @pytest.fixture
    def service(self, mock_repo: AsyncMock, mock_arq: AsyncMock) -> AddressService:
        return AddressService(mock_repo, mock_arq)

    async def test_create_address_creates_with_pending_status(
        self,
        service: AddressService,
        mock_repo: AsyncMock,
        mock_arq: AsyncMock,
    ) -> None:
        data = AddressCreate(
            name=AddressData.NAME_DEFAULT,
            address_line1=AddressData.ADDRESS_LINE1_DEFAULT,
            city_locality=AddressData.CITY_DEFAULT,
            state_province=AddressData.STATE_DEFAULT,
            postal_code=AddressData.POSTAL_CODE_DEFAULT,
            country_code=AddressData.COUNTRY_CODE_US,
        )
        mock_address = create_test_address()
        mock_repo.create.return_value = mock_address
        mock_repo.get_by_id_with_results.return_value = mock_address

        result = await service.create(data)

        assert result == mock_address
        mock_repo.create.assert_called_once()
        mock_arq.enqueue_job.assert_called_once_with(
            TaskNames.VALIDATE_ADDRESS,
            str(mock_address.id),
        )

    async def test_get_by_id_returns_address(
        self,
        service: AddressService,
        mock_repo: AsyncMock,
    ) -> None:
        address_id = uuid.uuid4()
        mock_address = create_test_address(id=address_id)
        mock_repo.get_by_id_with_results.return_value = mock_address

        result = await service.get_by_id(address_id)

        assert result == mock_address
        mock_repo.get_by_id_with_results.assert_called_once_with(address_id)

    async def test_get_by_id_raises_not_found(
        self,
        service: AddressService,
        mock_repo: AsyncMock,
    ) -> None:
        address_id = uuid.uuid4()
        mock_repo.get_by_id_with_results.return_value = None

        with pytest.raises(AddressNotFoundError) as exc_info:
            await service.get_by_id(address_id)

        assert exc_info.value.entity_id == address_id

    async def test_update_resets_validation_status(
        self,
        service: AddressService,
        mock_repo: AsyncMock,
        mock_arq: AsyncMock,
    ) -> None:
        address_id = uuid.uuid4()
        mock_address = create_test_address(
            id=address_id,
            validation_status=ValidationStatus.VERIFIED,
        )
        mock_repo.get_by_id.return_value = mock_address
        mock_repo.update.return_value = mock_address

        update_data = AddressUpdate(city_locality=AddressData.CITY_UPDATED)
        await service.update(address_id, update_data)

        assert mock_address.validation_status == ValidationStatus.PENDING
        assert mock_address.validated_at is None
        mock_arq.enqueue_job.assert_called_once()

    async def test_delete_removes_address(
        self,
        service: AddressService,
        mock_repo: AsyncMock,
    ) -> None:
        address_id = uuid.uuid4()
        mock_address = create_test_address(id=address_id)
        mock_repo.get_by_id.return_value = mock_address

        await service.delete(address_id)

        mock_repo.delete.assert_called_once_with(mock_address)

    async def test_delete_raises_not_found(
        self,
        service: AddressService,
        mock_repo: AsyncMock,
    ) -> None:
        address_id = uuid.uuid4()
        mock_repo.get_by_id.return_value = None

        with pytest.raises(AddressNotFoundError):
            await service.delete(address_id)
