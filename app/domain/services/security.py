import hmac

 
def codes_match(expected: str, provided: str) -> bool:
    """
    Constant-time comparison to avoid timing attacks.
    """
    return hmac.compare_digest(expected, provided)
