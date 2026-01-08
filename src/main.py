import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.dependencies.services import set_arq_pool
from src.api.routes import api_router
from src.config import get_settings
from src.core.exceptions import DomainError, NotFoundError
from src.db.session import engine

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting application...")

    try:
        arq_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        set_arq_pool(arq_pool)
        logger.info("ARQ pool initialized")
    except Exception as e:
        logger.warning("Failed to connect to Redis: %s", e)
        set_arq_pool(None)

    yield

    logger.info("Shutting down...")
    await engine.dispose()


app = FastAPI(
    title="ShipEngine Address Validation Service",
    description="CRUD API for address validation with background processing",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc), "code": "NOT_FOUND"})


@app.exception_handler(DomainError)
async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc), "code": "DOMAIN_ERROR"})


app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
