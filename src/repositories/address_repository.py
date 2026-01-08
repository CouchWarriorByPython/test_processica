from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.enums import ValidationStatus
from src.db.models.address import Address, ValidationResult
from src.repositories.base import BaseRepository


class AddressRepository(BaseRepository[Address]):
    model = Address

    async def get_by_id_with_results(self, address_id: UUID) -> Address | None:
        stmt = (
            select(Address)
            .where(Address.id == address_id)
            .options(selectinload(Address.validation_results))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_with_results(self, limit: int = 100, offset: int = 0) -> list[Address]:
        stmt = (
            select(Address)
            .options(selectinload(Address.validation_results))
            .order_by(Address.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, status: ValidationStatus, limit: int = 100) -> list[Address]:
        stmt = (
            select(Address)
            .where(Address.validation_status == status)
            .order_by(Address.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add_validation_result(self, validation: ValidationResult) -> ValidationResult:
        self._session.add(validation)
        await self._session.flush()
        return validation
