

from app.domain.ports.activation_code_repository import ActivationCodeRepository


class FakeActivationCodeRepo(ActivationCodeRepository):
    def __init__(self, code=None):
        self.code = code

    async def get_for_user(self, user_id):
        return self.code

    async def mark_used(self, code_id, now):
        pass

    async def increment_attempts(self, code_id):
        pass