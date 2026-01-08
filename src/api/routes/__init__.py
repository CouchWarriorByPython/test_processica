from fastapi import APIRouter

from src.api.routes import addresses, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["Addresses"])
