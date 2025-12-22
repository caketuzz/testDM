import logging
from app.domain.ports.mailer import Mailer

logger = logging.getLogger(__name__)


class ConsoleMailer(Mailer):
    async def send_activation_code(self, email: str, code: str) -> None:
        logger.info(
            "[MAILER] Sending activation code to %s: %s",
            email,
            code,
        )
