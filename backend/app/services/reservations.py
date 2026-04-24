from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List

async def calculate_monthly_revenue(property_id: str, month: int, year: int, db_session=None) -> Decimal:
    """
    Calculates revenue for a specific month.
    """

    start_date = datetime(year, month, 1)
    if month < 12:
        end_date = datetime(year, month + 1, 1)
    else:
        end_date = datetime(year + 1, 1, 1)
        
    print(f"DEBUG: Querying revenue for {property_id} from {start_date} to {end_date}")

    # SQL Simulation (This would be executed against the actual DB)
    query = """
        SELECT SUM(total_amount) as total
        FROM reservations
        WHERE property_id = $1
        AND tenant_id = $2
        AND check_in_date >= $3
        AND check_in_date < $4
    """
    
    # In production this query executes against a database session.
    # result = await db.fetch_val(query, property_id, tenant_id, start_date, end_date)
    # return result or Decimal('0')
    
    return Decimal('0') # Placeholder for now until DB connection is finalized

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        import os
        from sqlalchemy.ext.asyncio import create_async_engine
        url = os.environ["DATABASE_URL"].replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )
        _engine = create_async_engine(url, pool_pre_ping=True)
    return _engine


async def calculate_total_revenue(property_id: str, tenant_id: str) -> Dict[str, Any]:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession

    engine = _get_engine()
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text(
                """
                SELECT SUM(total_amount) AS total_revenue,
                       COUNT(*)          AS reservation_count
                FROM reservations
                WHERE property_id = :property_id AND tenant_id = :tenant_id
                """
            ),
            {"property_id": property_id, "tenant_id": tenant_id},
        )
        row = result.fetchone()

    total = Decimal(str(row.total_revenue)) if row and row.total_revenue is not None else Decimal("0")
    count = int(row.reservation_count) if row and row.reservation_count is not None else 0
    return {
        "property_id": property_id,
        "tenant_id": tenant_id,
        "total": f"{total:.2f}",
        "currency": "USD",
        "count": count,
    }
