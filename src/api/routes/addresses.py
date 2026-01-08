from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.services import get_address_service
from src.schemas.address import (
    AddressCreate,
    AddressListResponse,
    AddressResponse,
    AddressUpdate,
)
from src.schemas.common import MessageResponse
from src.services.address_service import AddressService

router = APIRouter()


@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    data: AddressCreate,
    service: Annotated[AddressService, Depends(get_address_service)],
) -> AddressResponse:
    address = await service.create(data)
    return AddressResponse.model_validate(address)


@router.get("", response_model=AddressListResponse)
async def list_addresses(
    service: Annotated[AddressService, Depends(get_address_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AddressListResponse:
    addresses, total = await service.get_list(limit=limit, offset=offset)
    return AddressListResponse(
        items=[AddressResponse.model_validate(a) for a in addresses],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: UUID,
    service: Annotated[AddressService, Depends(get_address_service)],
) -> AddressResponse:
    address = await service.get_by_id(address_id)
    return AddressResponse.model_validate(address)


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: UUID,
    data: AddressUpdate,
    service: Annotated[AddressService, Depends(get_address_service)],
) -> AddressResponse:
    address = await service.update(address_id, data)
    return AddressResponse.model_validate(address)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: UUID,
    service: Annotated[AddressService, Depends(get_address_service)],
) -> None:
    await service.delete(address_id)


@router.post("/{address_id}/validate", response_model=MessageResponse)
async def validate_address(
    address_id: UUID,
    service: Annotated[AddressService, Depends(get_address_service)],
) -> MessageResponse:
    await service.validate(address_id)
    return MessageResponse(message="Validation task enqueued")
