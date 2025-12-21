from datetime import datetime
from app.domain.exceptions import (
    ActivationCodeLocked,
    UserAlreadyExists,
    ActivationCodeExpired,
    ActivationCodeInvalid,
    UserAlreadyActive,
)
from app.domain.models.activation_code import ActivationCode
from app.domain.models.user import User
from app.domain.ports.activation_code_repository import ActivationCodeRepository
from app.domain.ports.user_repository import UserRepository
from app.domain.ports.mailer import Mailer
from app.domain.services.security import codes_match


class RegistrationService:
    def __init__(
        self,
        user_repo: UserRepository,
        activation_code_repo: ActivationCodeRepository,
        mailer: Mailer,
    ):
        self.user_repo = user_repo
        self.activation_code_repo = activation_code_repo
        self.mailer = mailer

    async def register(self, user: User, activation_code: ActivationCode) -> None:
        existing = await self.user_repo.get_by_email(user.email)
        if existing:
            raise UserAlreadyExists()

        await self.user_repo.create(user)
        await self.mailer.send_activation_code(user.email, activation_code.code_hash)

    async def activate(
        self,
        user: User,
        activation_code: ActivationCode,
        provided_code: str,
        now: datetime,
    ) -> None:
        if user.is_active:
            raise UserAlreadyActive()

        if not activation_code.can_attempt():
            raise ActivationCodeLocked()

        if activation_code.is_expired(now):
            raise ActivationCodeExpired()

        if not codes_match(activation_code.code_hash, provided_code):
            await self.activation_code_repo.increment_attempts(activation_code.id)
            raise ActivationCodeInvalid()

        # --- SUCCESS PATH ---
        user.activate(now)
        await self.user_repo.save(user)
        await self.activation_code_repo.mark_used(activation_code.id, now)

