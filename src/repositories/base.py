from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.base import Base


class BaseRepository[T: Base]:
    model: type[T]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> T | None:
        return await self._session.get(self.model, entity_id)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def update(self, entity: T) -> T:
        await self._session.flush()
        return entity

    async def delete(self, entity: T) -> None:
        await self._session.delete(entity)
        await self._session.flush()

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        result = await self._session.execute(stmt)
        return result.scalar() or 0
