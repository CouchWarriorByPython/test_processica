from typing import Annotated

from arq import ArqRedis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_db
from src.repositories.address_repository import AddressRepository
from src.services.address_service import AddressService

_arq_pool: ArqRedis | None = None


async def get_arq_pool() -> ArqRedis | None:
    return _arq_pool


def set_arq_pool(pool: ArqRedis | None) -> None:
    global _arq_pool
    _arq_pool = pool


async def get_address_service(
    session: Annotated[AsyncSession, Depends(get_db)],
    arq: Annotated[ArqRedis | None, Depends(get_arq_pool)],
) -> AddressService:
    return AddressService(AddressRepository(session), arq)
