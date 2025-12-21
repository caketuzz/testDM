from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: int
    email: str
    password_hash: str
    is_active: bool
    created_at: datetime
    activated_at: Optional[datetime] = None

    def activate(self, at: datetime) -> None:
        if self.is_active:
            raise ValueError("User already active")

        self.is_active = True
        self.activated_at = at
