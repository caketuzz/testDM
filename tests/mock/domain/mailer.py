
from app.domain.ports.mailer import Mailer



class FakeMailer(Mailer):
    def __init__(self):
        self.sent = []

    async def send_activation_code(self, email: str, code: str) -> None:
        self.sent.append((email, code))
