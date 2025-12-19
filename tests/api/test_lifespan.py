import pytest
from unittest.mock import AsyncMock, patch

from app.main import create_app
from app.core.lifespan import close_db_pool, init_db_pool
from tests.mock.fakepool import FakePool


@pytest.mark.asyncio
async def test_init_db_pool_failure():
    app = create_app()

    with patch("app.core.lifespan.asyncpg.create_pool", side_effect=Exception("DB down")):
        await init_db_pool(app)

    assert app.state.db_pool is None

@pytest.mark.asyncio
async def test_init_db_pool_success():
    app = create_app()
    fake_pool = FakePool()

    with patch(
        "app.core.lifespan.asyncpg.create_pool",
        return_value=fake_pool,
    ):
        with patch("app.core.lifespan.asyncpg.create_pool", new=AsyncMock(return_value=fake_pool)):
            await init_db_pool(app)

    assert app.state.db_pool is fake_pool

@pytest.mark.asyncio
async def test_close_db_pool_closes_pool():
    app = create_app()
    fake_pool = FakePool()
    app.state.db_pool = fake_pool
    with patch("app.core.lifespan.asyncpg.create_pool", new=AsyncMock(return_value=fake_pool)):
        await close_db_pool(app)

    assert fake_pool.closed is True