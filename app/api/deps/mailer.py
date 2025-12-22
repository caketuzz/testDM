from app.domain.ports.mailer import Mailer
from app.infrastructure.mailer.console_mailer import ConsoleMailer


def get_mailer() -> Mailer:
    return ConsoleMailer()
