from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from arq import ArqRedis

from src.core.enums import ValidationStatus
from src.core.exceptions import AddressNotFoundError
from src.db.models.address import Address, ValidationResult
from src.repositories.address_repository import AddressRepository
from src.schemas.address import AddressCreate, AddressUpdate


class AddressService:
    def __init__(self, repo: AddressRepository, arq: ArqRedis | None = None) -> None:
        self._repo = repo
        self._arq = arq

    async def create(self, data: AddressCreate) -> Address:
        address = Address(
            name=data.name,
            company_name=data.company_name,
            phone=data.phone,
            address_line1=data.address_line1,
            address_line2=data.address_line2,
            address_line3=data.address_line3,
            city_locality=data.city_locality,
            state_province=data.state_province,
            postal_code=data.postal_code,
            country_code=data.country_code,
            validation_status=ValidationStatus.PENDING,
        )
        address = await self._repo.create(address)

        if self._arq:
            await self._arq.enqueue_job("validate_address_task", str(address.id))

        return await self._repo.get_by_id_with_results(address.id)  # type: ignore[return-value]

    async def get_by_id(self, address_id: UUID) -> Address:
        address = await self._repo.get_by_id_with_results(address_id)
        if not address:
            raise AddressNotFoundError(address_id)
        return address

    async def get_list(self, limit: int = 20, offset: int = 0) -> tuple[list[Address], int]:
        addresses = await self._repo.get_all_with_results(limit=limit, offset=offset)
        total = await self._repo.count()
        return addresses, total

    async def update(self, address_id: UUID, data: AddressUpdate) -> Address:
        address = await self._repo.get_by_id(address_id)
        if not address:
            raise AddressNotFoundError(address_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(address, field, value)

        address.validation_status = ValidationStatus.PENDING
        address.validated_at = None
        await self._repo.update(address)

        if self._arq:
            await self._arq.enqueue_job("validate_address_task", str(address.id))

        return await self._repo.get_by_id_with_results(address.id)  # type: ignore[return-value]

    async def delete(self, address_id: UUID) -> None:
        address = await self._repo.get_by_id(address_id)
        if not address:
            raise AddressNotFoundError(address_id)
        await self._repo.delete(address)

    async def validate(self, address_id: UUID) -> Address:
        address = await self._repo.get_by_id(address_id)
        if not address:
            raise AddressNotFoundError(address_id)

        address.validation_status = ValidationStatus.PENDING
        address.validated_at = None
        await self._repo.update(address)

        if self._arq:
            await self._arq.enqueue_job("validate_address_task", str(address.id))

        return await self._repo.get_by_id_with_results(address.id)  # type: ignore[return-value]

    async def save_validation_result(
        self,
        address_id: UUID,
        status: ValidationStatus,
        matched_address: dict[str, Any] | None = None,
        messages: list[dict[str, Any]] | None = None,
    ) -> ValidationResult:
        address = await self._repo.get_by_id(address_id)
        if not address:
            raise AddressNotFoundError(address_id)

        result = ValidationResult(
            address_id=address_id,
            status=status,
            matched_address=matched_address,
            messages=messages,
        )
        result = await self._repo.add_validation_result(result)

        address.validation_status = status
        address.validated_at = datetime.now(UTC)
        await self._repo.update(address)

        return result
