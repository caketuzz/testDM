from datetime import datetime, timezone

import pytest

from app.domain.models.user import User
from app.infrastructure.repositories.user_repository import PostgresUserRepository
from tests.mock.db.db import FakeConn, FakePool


@pytest.mark.asyncio
async def test_get_by_email_returns_user():
    row = {
        "id": 1,
        "email": "test@example.com",
        "password_hash": "hash",
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc),
        "activated_at": None,
    }

    conn = FakeConn(row=row)
    pool = FakePool(conn)
    repo = PostgresUserRepository(pool)

    user = await repo.get_by_email("test@example.com")

    assert user is not None
    assert user.email == "test@example.com"
    assert user.is_active is False

@pytest.mark.asyncio
async def test_get_by_email_returns_None():
    row = None

    conn = FakeConn(row=row)
    pool = FakePool(conn)
    repo = PostgresUserRepository(pool)

    user = await repo.get_by_email("test@example.com")

    assert user is None

@pytest.mark.asyncio
async def test_create_user_sets_id_from_db():
    conn = FakeConn(row={"id": 42})
    pool = FakePool(conn)
    repo = PostgresUserRepository(pool)

    user = User(
        id=None,
        email="test@example.com",
        password_hash="hash",
        is_active=False,
        created_at=datetime.now(timezone.utc),
        activated_at=None,
    )

    created = await repo.create(user)

    # invariant clé
    assert created.id == 42


@pytest.mark.asyncio
async def test_save_updates_status_and_activated_at():
    conn = FakeConn()
    pool = FakePool(conn)
    repo = PostgresUserRepository(pool)

    user = User(
        id=1,
        email="test@example.com",
        password_hash="hash",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        activated_at=datetime.now(timezone.utc),
    )

    await repo.save(user)

    assert len(conn.executed) == 1
    sql, args = conn.executed[0]
    assert "UPDATE users" in sql
    assert args[0] == "ACTIVE"
