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
from app.utils.security import codes_match
import logging


logger = logging.getLogger(__name__)

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

    async def register(self, user: User) -> None:
        existing = await self.user_repo.get_by_email(user.email)
        if existing:
            raise UserAlreadyExists()

        user = await self.user_repo.create(user)
        activation_code, code_plain = ActivationCode.generate(user.id)
        await self.activation_code_repo.create(activation_code)
        await self.mailer.send_activation_code(user.email, code_plain)

    async def activate(
        self,
        user: User,
        activation_code: ActivationCode,
        provided_code: str,
        now: datetime,
    ) -> None:
        print(activation_code)
        print(provided_code)
        if user.is_active:
            logger.info(f"Activation Error: {user.id} | user.isactive")
            raise UserAlreadyActive()
        
        if activation_code is None:
            logger.info(f"Activation Error: {user.id} | code is None")
            raise ActivationCodeInvalid()
        
        if not activation_code.can_attempt():
            logger.info(f"Activation Error: {user.id} | no more attempts")
            raise ActivationCodeLocked()

        if activation_code.is_expired(now):
            logger.info(f"Activation Error: {user.id} | code expired")
            raise ActivationCodeExpired()

        if not codes_match(activation_code.code_hash, provided_code):
            await self.activation_code_repo.increment_attempts(activation_code.id)
            logger.info(f"Activation Error: {user.id} | code invalid")
            raise ActivationCodeInvalid()

        # --- SUCCESS PATH ---
        user.activate(now)
        logger.info(f"User activated: {user.id}")
        await self.user_repo.save(user)
        await self.activation_code_repo.mark_used(activation_code.id, now)

