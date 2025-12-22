


from asgi_lifespan import LifespanManager
from fastapi import Depends
from httpx import ASGITransport, AsyncClient
import pytest

from app.api.deps.auth import get_authenticated_user
from app.api.deps.mailer import get_mailer
from app.api.deps.repository import get_activation_code_repository, get_user_repository
from app.domain.models.activation_code import ActivationCode
from app.main import create_app
from app.utils.security import hash_password
from tests.mock.domain.activation_code_repo import FakeActivationCodeRepo
from tests.mock.domain.user_repository import FakeUser, FakeUserRepository
from tests.mock.domain.mailer import FakeMailer


@pytest.fixture
async def app():
    app = create_app()

    @app.get("/protected")
    async def protected(user=Depends(get_authenticated_user)):
        return {"email": user.email}
    
    async with LifespanManager(app):
        yield app

    # nettoyage crucial pour éviter les fuites entre tests
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_register_ok(app):
    user_repo = FakeUserRepository()
    code_repo = FakeActivationCodeRepo()
    mailer = FakeMailer()

    app.dependency_overrides[get_user_repository] = lambda: user_repo
    app.dependency_overrides[get_activation_code_repository] = lambda: code_repo
    app.dependency_overrides[get_mailer] = lambda: mailer

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/register",
            json={"email": "test@example.com", "password": "secret12345"},
        )

    assert resp.status_code == 201
    assert len(mailer.sent) == 1



@pytest.mark.asyncio
async def test_activate_ok(app):
    user = FakeUser()
    code, plain = ActivationCode.generate(user.id)

    class FakeCodeRepo:
        async def get_for_user(self, user_id):
            return code

        async def mark_used(self, code_id, now):
            pass

        async def increment_attempts(self, code_id):
            pass

    app.dependency_overrides[get_authenticated_user] = lambda: user
    app.dependency_overrides[get_activation_code_repository] = lambda: FakeCodeRepo()
    app.dependency_overrides[get_user_repository] = lambda: FakeUserRepository()

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
            resp = await client.post(
                "/activate",
                json={"code": plain},
            )

    assert resp.status_code == 200
    assert user.is_active is True

@pytest.mark.asyncio
async def test_activate_invalid_code_returns_neutral(app):
    user = FakeUser()
    code, _ = ActivationCode.generate(user.id)

    class FakeCodeRepo:
        async def get_for_user(self, user_id):
            return code

        async def mark_used(self, code_id, now):
            pass

        async def increment_attempts(self, code_id):
            pass

    app.dependency_overrides[get_authenticated_user] = lambda: user
    app.dependency_overrides[get_activation_code_repository] = lambda: FakeCodeRepo()
    app.dependency_overrides[get_user_repository] = lambda: None

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
            resp = await client.post(
                "/activate",
                json={"code": "9999"},
            )

    assert resp.status_code == 200
    assert user.is_active is False


@pytest.mark.asyncio
async def test_auth_user_not_found(app):
    app.dependency_overrides[get_user_repository] = lambda: FakeUserRepository()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/protected",
            auth=("unknown@example.com", "secret"),
        )

    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_auth_invalid_password(app):
    user = FakeUser(
    )
    user.email="test@example.com"
    user.password_hash=hash_password("correct")


    app.dependency_overrides[get_user_repository] = lambda: FakeUserRepository()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/protected",
            auth=("test@example.com", "wrong"),
        )

    assert resp.status_code == 401



# @pytest.mark.asyncio
# async def test_auth_ok(app):
#     user = FakeUser(
#     )
#     user.email="test@example.com"
#     user.password_hash=hash_password("correct")
#     app.dependency_overrides[get_user_repository] = lambda: FakeUserRepository()

#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test") as client:
#         resp = await client.get(
#             "/protected",
#             auth=("test@example.com", "secret"),
#         )

#     assert resp.status_code == 200
#     assert resp.json()["email"] == "test@example.com"
