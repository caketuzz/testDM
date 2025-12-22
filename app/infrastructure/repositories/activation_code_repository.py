from typing import Optional
from datetime import datetime
import asyncpg

from app.domain.models.activation_code import ActivationCode
from app.domain.ports.activation_code_repository import ActivationCodeRepository


class PostgresActivationCodeRepository(ActivationCodeRepository):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_for_user(self, user_id: int) -> Optional[ActivationCode]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    id,
                    user_id,
                    code_hash,
                    expires_at,
                    used_at,
                    created_at,
                    attempts
                FROM activation_codes
                WHERE user_id = $1
                """,
                user_id,
            )

        if not row:
            return None

        return ActivationCode(
            id=row["id"],
            user_id=row["user_id"],
            code_hash=row["code_hash"],
            expires_at=row["expires_at"],
            used_at=row["used_at"],
            created_at=row["created_at"],
            attempts=row["attempts"],
        )

    async def create(self, code: ActivationCode) -> ActivationCode:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO activation_codes (
                    user_id,
                    code_hash,
                    expires_at,
                    attempts
                )
                VALUES ($1, $2, $3, 0)
                RETURNING id, created_at
                """,
                code.user_id,
                code.code_hash,
                code.expires_at,
            )

        code.id = row["id"]
        code.created_at = row["created_at"]
        return code

    async def mark_used(self, code_id: int, at: datetime) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE activation_codes
                SET used_at = $1
                WHERE id = $2
                """,
                at,
                code_id,
            )
    
    async def increment_attempts(self, code_id: int) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE activation_codes
                SET attempts = attempts + 1
                WHERE id = $1
                """,
                code_id,
            )
