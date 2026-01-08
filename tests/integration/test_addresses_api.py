from typing import Any

import pytest
from httpx import AsyncClient

from tests.constants import (
    AddressData,
    HealthStatus,
    StatusCodes,
    TestIds,
    ValidationStatusValues,
)


class TestAddressesAPI:
    @pytest.fixture
    def valid_address_payload(self) -> dict[str, Any]:
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

    async def test_create_address_returns_201(
        self,
        client: AsyncClient,
        valid_address_payload: dict[str, Any],
    ) -> None:
        response = await client.post(
            "/api/v1/addresses",
            json=valid_address_payload,
        )

        assert response.status_code == StatusCodes.CREATED
        data = response.json()
        assert data["name"] == AddressData.NAME_DEFAULT
        assert data["address_line1"] == AddressData.ADDRESS_LINE1_DEFAULT
        assert data["validation_status"] == ValidationStatusValues.PENDING
        assert "id" in data

    async def test_create_address_with_invalid_country_returns_422(
        self,
        client: AsyncClient,
        valid_address_payload: dict[str, Any],
    ) -> None:
        valid_address_payload["country_code"] = "INVALID"

        response = await client.post(
            "/api/v1/addresses",
            json=valid_address_payload,
        )

        assert response.status_code == StatusCodes.UNPROCESSABLE

    async def test_list_addresses_returns_empty_list(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/addresses")

        assert response.status_code == StatusCodes.OK
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_addresses_returns_created_addresses(
        self,
        client: AsyncClient,
        valid_address_payload: dict[str, Any],
    ) -> None:
        await client.post("/api/v1/addresses", json=valid_address_payload)

        response = await client.get("/api/v1/addresses")

        assert response.status_code == StatusCodes.OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

    async def test_get_address_returns_address(
        self,
        client: AsyncClient,
        valid_address_payload: dict[str, Any],
    ) -> None:
        create_response = await client.post(
            "/api/v1/addresses",
            json=valid_address_payload,
        )
        address_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/addresses/{address_id}")

        assert response.status_code == StatusCodes.OK
        data = response.json()
        assert data["id"] == address_id

    async def test_get_nonexistent_address_returns_404(self, client: AsyncClient) -> None:
        response = await client.get(f"/api/v1/addresses/{TestIds.FAKE_UUID}")

        assert response.status_code == StatusCodes.NOT_FOUND

    async def test_update_address_updates_fields(
        self,
        client: AsyncClient,
        valid_address_payload: dict[str, Any],
    ) -> None:
        create_response = await client.post(
            "/api/v1/addresses",
            json=valid_address_payload,
        )
        address_id = create_response.json()["id"]

        update_payload = {"city_locality": AddressData.CITY_UPDATED}
        response = await client.put(
            f"/api/v1/addresses/{address_id}",
            json=update_payload,
        )

        assert response.status_code == StatusCodes.OK
        data = response.json()
        assert data["city_locality"] == AddressData.CITY_UPDATED
        assert data["validation_status"] == ValidationStatusValues.PENDING

    async def test_delete_address_returns_204(
        self,
        client: AsyncClient,
        valid_address_payload: dict[str, Any],
    ) -> None:
        create_response = await client.post(
            "/api/v1/addresses",
            json=valid_address_payload,
        )
        address_id = create_response.json()["id"]

        response = await client.delete(f"/api/v1/addresses/{address_id}")

        assert response.status_code == StatusCodes.NO_CONTENT

        get_response = await client.get(f"/api/v1/addresses/{address_id}")
        assert get_response.status_code == StatusCodes.NOT_FOUND

    async def test_validate_address_returns_message(
        self,
        client: AsyncClient,
        valid_address_payload: dict[str, Any],
    ) -> None:
        create_response = await client.post(
            "/api/v1/addresses",
            json=valid_address_payload,
        )
        address_id = create_response.json()["id"]

        response = await client.post(f"/api/v1/addresses/{address_id}/validate")

        assert response.status_code == StatusCodes.OK
        assert "message" in response.json()


class TestHealthEndpoints:
    async def test_health_returns_ok(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/health")

        assert response.status_code == StatusCodes.OK
        assert response.json()["status"] == HealthStatus.OK

    async def test_health_ready_returns_ok(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/health/ready")

        assert response.status_code == StatusCodes.OK
        data = response.json()
        assert data["status"] == HealthStatus.OK
