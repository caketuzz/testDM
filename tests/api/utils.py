
from app.utils.security import hash_password, verify_password
import pytest


def test_verify_password_invalid_algo():
    fake_hash = "md5$1000$salt$hash"

    assert verify_password(fake_hash, "secret") is False


def test_verify_password_wrong_password():
    password_hash = hash_password("correct-password")

    assert verify_password(password_hash, "wrong-password") is False


def test_verify_password_ok():
    password_hash = hash_password("secret")

    assert verify_password(password_hash, "secret") is True

def test_verify_password_malformed_hash_raises():
    with pytest.raises(ValueError):
        verify_password("invalid-hash", "secret")
