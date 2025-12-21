
import secrets


def generate_activation_code() -> str:
    """
    Generates a cryptographically secure 4-digit activation code.
    """
    return f"{secrets.randbelow(10000):04d}"