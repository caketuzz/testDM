from contextlib import asynccontextmanager
from unittest.mock import patch
import httpx
import pytest
from app.api.deps import get_db_pool
from app.main import create_app
from asgi_lifespan import LifespanManager

from tests.mock.db.fakepool import FakePool

    
@pytest.fixture
def app():
    app = create_app()
    yield app
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_health():
    app = create_app()

    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:
            r = await client.get("/health")

    assert r.status_code == 200
    assert r.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_health_without_db(app):
    app.dependency_overrides[get_db_pool] = lambda: None

    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:
            r = await client.get("/health")

    assert r.status_code == 200
    assert r.json()["database"] == "ko"




@pytest.mark.asyncio
async def test_health_with_db_executes_select(app):
    app.dependency_overrides[get_db_pool] = lambda: FakePool()

    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/health")

    assert r.status_code == 200
    assert r.json()["database"] == "ok"

