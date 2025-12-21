from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ActivationCode:
    user_id: int
    code: str
    created_at: datetime
    ttl_seconds: int

    def is_expired(self, now: datetime) -> bool:
        return now > self.created_at + timedelta(seconds=self.ttl_seconds)
