from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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

    def is_expired(self, now: datetime) -> bool:
        return now >= self.expires_at

    def is_used(self) -> bool:
        return self.used_at is not None
    
    def can_attempt(self) -> bool:
        return self.attempts < MAX_ACTIVATION_CODE_ATTEMPTS
    
    def register_failed_attempt(self) -> None:
        self.attempts += 1

