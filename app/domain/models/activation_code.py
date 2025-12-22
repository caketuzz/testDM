from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from app.utils.security import hash_code


MAX_ACTIVATION_CODE_ATTEMPTS = 5

@dataclass
class ActivationCode:
    id: Optional[int]
    user_id: int
    code_hash: str
    expires_at: datetime
    used_at: Optional[datetime]
    created_at: datetime
    attempts: int = 0

    @classmethod
    def generate(
        cls,
        user_id: int,
        now: Optional[datetime] = None,
        ttl_minutes: int = 60,
    ) -> Tuple["ActivationCode", str]:
        """
        Returns (ActivationCode, code_plaintext).
        - plaintext is only used for the purpose of email sending
        """
        now = now or datetime.now(timezone.utc)
        code_plain = f"{__import__('secrets').randbelow(10000):04d}"
        return (
            cls(
                id=None,
                user_id=user_id,
                code_hash=hash_code(code_plain),
                expires_at=now + timedelta(minutes=ttl_minutes),
                used_at=None,
                created_at=now,
                attempts=0,
            ),
            code_plain,
        )

    def is_expired(self, now: datetime) -> bool:
        return now >= self.expires_at

    def is_used(self) -> bool:
        return self.used_at is not None
    
    def can_attempt(self) -> bool:
        return self.attempts < MAX_ACTIVATION_CODE_ATTEMPTS
    
    def register_failed_attempt(self) -> None:
        self.attempts += 1

