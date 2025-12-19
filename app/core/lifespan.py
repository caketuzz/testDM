from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncpg
import logging

from app.core.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = None

    try:
        pool = await asyncpg.create_pool(settings.database_url)
        app.state.db_pool = pool
        logger.info("Database connection pool initialized")
    except Exception as exc:
        logger.error("Database connection failed at startup", exc_info=exc)

    yield

    if app.state.db_pool:
        await app.state.db_pool.close()
