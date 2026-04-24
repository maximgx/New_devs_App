import os
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        url = os.environ["DATABASE_URL"].replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )
        _engine = create_async_engine(url, pool_pre_ping=True)
    return _engine


def _resolve_tenant_id(current_user) -> str:
    if isinstance(current_user, dict):
        tid = current_user.get("tenant_id")
    else:
        tid = getattr(current_user, "tenant_id", None)
    if not tid:
        raise HTTPException(status_code=403, detail="No tenant context")
    return tid


@router.get("/properties")
async def list_properties(
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    tenant_id = _resolve_tenant_id(current_user)

    async with AsyncSession(_get_engine()) as session:
        result = await session.execute(
            text(
                """
                SELECT id, name, timezone
                FROM properties
                WHERE tenant_id = :tenant_id
                ORDER BY id
                """
            ),
            {"tenant_id": tenant_id},
        )
        rows = result.fetchall()

    return [{"id": r.id, "name": r.name, "timezone": r.timezone} for r in rows]
