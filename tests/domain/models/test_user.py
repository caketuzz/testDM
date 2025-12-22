import pytest
from datetime import datetime, timezone

from app.domain.models.user import User


def test_user_activate_when_already_active_raises():
    user = User(
        id=1,
        email="test@example.com",
        password_hash="hashed",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        activated_at= datetime.now(timezone.utc),
    )

    with pytest.raises(ValueError, match="User already active"):
        user.activate(datetime.now(timezone.utc))
