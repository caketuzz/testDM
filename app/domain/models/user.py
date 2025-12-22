from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.utils.security import hash_password


@dataclass
class User:
    id: int
    email: str
    password_hash: str
    is_active: bool
    created_at: datetime
    activated_at: Optional[datetime] = None

    @classmethod
    def create(cls, email: str, password: str, now: Optional[datetime] = None) -> "User":
        now = now or datetime.now(timezone.utc)
        return cls( 
            id=None,
            email=email,
            password_hash=hash_password(password),
            is_active=False,
            created_at=now,
            activated_at=None,
        )

    def activate(self, at: datetime) -> None:
        if self.is_active:
            raise ValueError("User already active")

        self.is_active = True
        self.activated_at = at
