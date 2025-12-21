from asgi_lifespan import LifespanManager
import pytest
from unittest.mock import AsyncMock, patch

from app.infrastructure.db import migrate
from app.main import create_app
from app.core.lifespan import close_db_pool, init_db_pool
from tests.mock.db.fakepool import FakePool


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


@pytest.mark.asyncio
async def test_lifespan_without_db_pool_does_not_run_migrations(monkeypatch):
    app = create_app()

    # Simule un échec de création du pool
    async def fake_init_db_pool(app):
        app.state.db_pool = None

    monkeypatch.setattr(
        "app.core.lifespan.init_db_pool",
        fake_init_db_pool,
    )

    # Spy sur run_migrations
    called = False

    async def fake_run_migrations(_pool):
        nonlocal called
        called = True

    monkeypatch.setattr(
        migrate,
        "run_migrations",
        fake_run_migrations,
    )

    async with LifespanManager(app):
        pass

    assert called is False


@pytest.mark.asyncio
async def test_lifespan_with_db_pool_runs_migrations(monkeypatch):
    app = create_app()

    fake_pool = FakePool()

    # Force la présence d’un pool
    async def fake_init_db_pool(app):
        app.state.db_pool = fake_pool

    monkeypatch.setattr(
        "app.core.lifespan.init_db_pool",
        fake_init_db_pool,
    )

    called_with = None

    async def fake_run_migrations(pool):
        nonlocal called_with
        called_with = pool

    monkeypatch.setattr(
        "app.core.lifespan.run_migrations",
        fake_run_migrations,
    )

    async with LifespanManager(app):
        pass

    assert called_with is fake_pool

