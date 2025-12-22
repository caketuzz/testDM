from fastapi import APIRouter, Depends
import logging
from app.api.deps.db import get_db_pool

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(pool=Depends(get_db_pool)):
    
    db_status = "ok" if pool else "ko"

    try:
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
    except Exception:
        db_status = "ko"
        # we could raise an HTTPException if the network is monitored
        # raise HTTPException(
        #     status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        #     detail="Database unavailable",
        # )

    return {
        "status": "ok",
        "database": db_status,
    }
