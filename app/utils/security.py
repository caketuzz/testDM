import hmac
import os
import base64
import hashlib

# --- password hashing (PBKDF2) ---

_PWD_ITER = 200_000
_SALT_LEN = 16


def hash_password(password: str) -> str:
    salt = os.urandom(_SALT_LEN)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PWD_ITER)
    return f"pbkdf2_sha256${_PWD_ITER}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"


def verify_password(password_hash: str, password: str) -> bool:
    algo, iter_s, salt_b64, dk_b64 = password_hash.split("$", 3)
    if algo != "pbkdf2_sha256":
        return False
    iters = int(iter_s)
    salt = base64.b64decode(salt_b64)
    expected = base64.b64decode(dk_b64)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iters)
    return hmac.compare_digest(dk, expected)


# --- activation code hashing (SHA-256) ---

def hash_code(code_plain: str) -> str:
    # code = 4 digits, SHA-256 suffit (et c'est rapide)
    return hashlib.sha256(code_plain.encode("utf-8")).hexdigest()


def codes_match(code_hash: str, provided_code: str) -> bool:
    provided_hash = hash_code(provided_code)
    return hmac.compare_digest(code_hash, provided_hash)