from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncpg
import logging

from app.core.settings import settings
from app.infrastructure.db.migrate import run_migrations

logger = logging.getLogger(__name__)


async def init_db_pool(app):
    try:
        pool = await asyncpg.create_pool(settings.database_url)
        app.state.db_pool = pool
    except Exception:
        app.state.db_pool = None


async def close_db_pool(app):
    pool = getattr(app.state, "db_pool", None)
    if pool:
        await pool.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool(app)
    if app.state.db_pool:
        await run_migrations(app.state.db_pool)
    yield
    await close_db_pool(app)

