import httpx
from app.main import create_app


async def test_health():
    app = create_app()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")

    assert r.status_code == 200
    assert r.json()["status"] == "ok"
