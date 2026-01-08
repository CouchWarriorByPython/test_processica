from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_db

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def ready(db: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
