from datetime import datetime
from app.domain.exceptions import (
    UserAlreadyExists,
    ActivationCodeExpired,
    ActivationCodeInvalid,
    UserAlreadyActive,
)
from app.domain.models.activation_code import ActivationCode
from app.domain.models.user import User
from app.domain.ports.user_repository import UserRepository
from app.domain.ports.mailer import Mailer


class RegistrationService:
    def __init__(self, user_repo: UserRepository, mailer: Mailer):
        self.user_repo = user_repo
        self.mailer = mailer

    async def register(self, user: User, activation_code: ActivationCode) -> None:
        existing = await self.user_repo.get_by_email(user.email)
        if existing:
            raise UserAlreadyExists()

        await self.user_repo.create(user)
        await self.mailer.send_activation_code(user.email, activation_code.code)

    async def activate(
        self,
        user: User,
        activation_code: ActivationCode,
        provided_code: str,
        now: datetime,
    ) -> None:
        if user.is_active:
            raise UserAlreadyActive()

        if activation_code.is_expired(now):
            raise ActivationCodeExpired()

        if activation_code.code != provided_code:
            raise ActivationCodeInvalid()

        user.activate(now)
        await self.user_repo.save(user)
