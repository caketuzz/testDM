from typing import Optional, Protocol
from app.domain.models.user import User


class UserRepository(Protocol):
    async def get_by_email(self, email: str) -> Optional[User]:
        ...

    async def create(self, user: User) -> User:
        ...

    async def save(self, user: User) -> None:
        ...
