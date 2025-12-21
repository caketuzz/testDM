from typing import Optional
from app.domain.models.user import User
from app.domain.ports.user_repository import UserRepository


class FakeUserRepository(UserRepository):
    def __init__(self):
        self.users = {}

    async def get_by_email(self, email: str) -> Optional[User]:
        return self.users.get(email)

    async def create(self, user: User) -> User:
        self.users[user.email] = user
        return user

    async def save(self, user: User) -> None:
        self.users[user.email] = user
