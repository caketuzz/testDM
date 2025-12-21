from datetime import datetime
import pytest

from app.domain.models.activation_code import ActivationCode
from app.infrastructure.repositories.activation_code_repository import PostgresActivationCodeRepository
from tests.mock.db.db import FakeConn, FakePool


@pytest.mark.asyncio
async def test_get_activation_code_for_user():
    now = datetime.utcnow()
    row = {
        "id": 1,
        "user_id": 42,
        "code_hash": "hashed",
        "expires_at": now,
        "used_at": None,
        "created_at": now,
        "attempts": 3,
    }

    conn = FakeConn(row=row)
    pool = FakePool(conn)
    repo = PostgresActivationCodeRepository(pool)

    code = await repo.get_for_user(42)

    assert code is not None
    assert code.code_hash == "hashed"
    assert code.used_at is None
    assert code.attempts == 3

@pytest.mark.asyncio
async def test_get_activation_code_no_user():
    now = datetime.utcnow()
    row = None

    conn = FakeConn(row=row)
    pool = FakePool(conn)
    repo = PostgresActivationCodeRepository(pool)

    code = await repo.get_for_user(42)

    assert code is None

@pytest.mark.asyncio
async def test_create_activation_code_sets_id_and_created_at():
    now = datetime.utcnow()
    conn = FakeConn(row={"id": 10, "created_at": now})
    pool = FakePool(conn)
    repo = PostgresActivationCodeRepository(pool)

    code = ActivationCode(
        id=None,
        user_id=1,
        code_hash="hash",
        expires_at=now,
        used_at=None,
        created_at=None,
    )

    created = await repo.create(code)

    assert created.id == 10
    assert created.created_at == now

@pytest.mark.asyncio
async def test_mark_used_executes_update():
    conn = FakeConn()
    pool = FakePool(conn)
    repo = PostgresActivationCodeRepository(pool)

    now = datetime.utcnow()
    await repo.mark_used(code_id=5, at=now)

    sql, args = conn.executed[0]
    assert "UPDATE activation_codes" in sql
    assert args == (now, 5)


def test_register_failed_attempt_increments_attempts():
    code = code = ActivationCode(
        id=None,
        user_id=1,
        code_hash="hash",
        expires_at=datetime.now,
        used_at=None,
        created_at=None,
        attempts = 2
    )

    code.register_failed_attempt()

    assert code.attempts == 3


def test_activation_code_cannot_attempt_when_limit_reached():
    code = ActivationCode(
        id=1,
        user_id=1,
        code_hash="hash",
        expires_at=datetime.utcnow(),
        used_at=None,
        created_at=datetime.utcnow(),
        attempts=5,
    )

    assert code.can_attempt() is False

@pytest.mark.asyncio
async def test_increment_attempts_executes_update():
    conn = FakeConn()
    pool = FakePool(conn)
    repo = PostgresActivationCodeRepository(pool)

    await repo.increment_attempts(code_id=10)

    sql, args = conn.executed[0]
    assert "UPDATE activation_codes" in sql
    assert args == (10,)