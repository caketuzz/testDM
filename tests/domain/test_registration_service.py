
import pytest
from datetime import datetime, timedelta

from app.domain.models.user import User
from app.domain.models.activation_code import ActivationCode
from app.domain.services.registration_service import RegistrationService
from app.domain.exceptions import (
    ActivationCodeLocked,
    UserAlreadyExists,
    ActivationCodeExpired,
    ActivationCodeInvalid,
    UserAlreadyActive,
)
from tests.mock.domain.activation_code_repo import FakeActivationCodeRepo
from tests.mock.domain.mailer import FakeMailer
from tests.mock.domain.user_repository import FakeUserRepository


@pytest.fixture
def service():
    repo = FakeUserRepository()
    activation_code_repo = FakeActivationCodeRepo()
    mailer = FakeMailer()
    return RegistrationService(repo, activation_code_repo, mailer), repo, activation_code_repo, mailer


@pytest.fixture
def user():
    return User(
        id=1,
        email="test@example.com",
        password_hash="hashed",
        is_active=False,
        created_at=datetime.utcnow(),
    )


def activation_code(user, now, ttl=60, code="1234"):
    return ActivationCode(
        id=1,
        user_id=user.id,
        code_hash=code,
        created_at=now,
        expires_at=now + timedelta(minutes=ttl),
        used_at=None
    )

@pytest.mark.asyncio
async def test_register_sends_activation_code(service, user):
    svc, repo, activation_code_repo, mailer = service
    now = datetime.utcnow()
    code = activation_code(user, now)

    await svc.register(user, code)

    assert repo.users[user.email] == user
    assert (user.email, code.code_hash) in mailer.sent

@pytest.mark.asyncio
async def test_register_existing_user_raises(service, user):
    svc, repo, _, _ = service
    repo.users[user.email] = user

    with pytest.raises(UserAlreadyExists):
        await svc.register(user, activation_code(user, datetime.utcnow()))

@pytest.mark.asyncio
async def test_activate_user_ok(service, user):
    svc, repo, activation_code_repo, _ = service
    now = datetime.utcnow()
    repo.users[user.email] = user
    code = activation_code(user, now)

    await svc.activate(user, code, "1234", now)

    assert user.is_active is True
    assert user.activated_at == now

@pytest.mark.asyncio
async def test_activate_expired_code_raises(service, user):
    svc, repo, activation_code_repo, _ = service
    now = datetime.utcnow()
    repo.users[user.email] = user
    code = activation_code(user, now - timedelta(minutes=120), ttl=60)

    with pytest.raises(ActivationCodeExpired):
        await svc.activate(user, code, "1234", now)

@pytest.mark.asyncio
async def test_activate_invalid_code_raises(service, user):
    svc, repo, _, _ = service
    now = datetime.utcnow()
    repo.users[user.email] = user
    code = activation_code(user, now)

    with pytest.raises(ActivationCodeInvalid):
        await svc.activate(user, code, "9999", now)

@pytest.mark.asyncio
async def test_activate_already_active_user_raises(service, user):
    svc, repo, _, _ = service
    now = datetime.utcnow()
    user.is_active = True
    repo.users[user.email] = user
    code = activation_code(user, now)

    with pytest.raises(UserAlreadyActive):
        await svc.activate(user, code, "1234", now)

@pytest.mark.asyncio
async def test_activate_no_attempt_left(service, user):
    svc, repo, _, _ = service
    now = datetime.utcnow()
    repo.users[user.email] = user
    code = activation_code(user, now)
    code.attempts = 5

    with pytest.raises(ActivationCodeLocked):
        await svc.activate(user, code, "1234", now)

