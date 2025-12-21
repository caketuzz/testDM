from typing import  Protocol

class Mailer(Protocol):
    async def send_activation_code(self, email: str, code: str) -> None:
        ...
