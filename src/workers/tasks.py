import logging
from typing import Any
from uuid import UUID

from src.db.session import get_session
from src.repositories.address_repository import AddressRepository
from src.services.address_service import AddressService
from src.services.shipengine_client import ShipEngineClient

logger = logging.getLogger(__name__)


async def validate_address_task(_ctx: dict[str, Any], address_id: str) -> dict[str, str]:
    logger.info("Starting validation for address %s", address_id)

    async with get_session() as session:
        repo = AddressRepository(session)
        service = AddressService(repo)
        client = ShipEngineClient()

        address = await repo.get_by_id(UUID(address_id))
        if not address:
            error_msg = f"Address {address_id} not found"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Calling ShipEngine API for address %s", address_id)
        result = await client.validate_address(address)

        await service.save_validation_result(
            address_id=address.id,
            status=result.status,
            matched_address=result.matched_address,
            messages=result.messages,
        )

        logger.info(
            "Validation completed for address %s with status %s", address_id, result.status.value
        )
        return {"status": result.status.value, "address_id": address_id}
