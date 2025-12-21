from datetime import datetime, timedelta
from app.domain.models.activation_code import ActivationCode


def test_activation_code_is_not_used_when_used_at_is_none():
    code = ActivationCode(
        id=1,
        user_id=1,
        code_hash="hash",
        expires_at=datetime.utcnow() + timedelta(minutes=1),
        used_at=None,
        created_at=datetime.utcnow(),
    )

    assert code.is_used() is False


def test_activation_code_is_used_when_used_at_is_set():
    now = datetime.utcnow()

    code = ActivationCode(
        id=1,
        user_id=1,
        code_hash="hash",
        expires_at=now + timedelta(minutes=1),
        used_at=now,
        created_at=now,
    )

    assert code.is_used() is True
