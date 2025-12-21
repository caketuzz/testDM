from typing import Optional
from datetime import datetime
import asyncpg

from app.domain.models.user import User
from app.domain.ports.user_repository import UserRepository


class PostgresUserRepository(UserRepository):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_by_email(self, email: str) -> Optional[User]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    id,
                    email,
                    password_hash,
                    status,
                    created_at,
                    activated_at
                FROM users
                WHERE email = $1
                """,
                email,
            )

        if not row:
            return None

        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            is_active=row["status"] == "ACTIVE",
            created_at=row["created_at"],
            activated_at=row["activated_at"],
        )

    async def create(self, user: User) -> User:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO users (
                    email,
                    password_hash,
                    status,
                    created_at
                )
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                user.email,
                user.password_hash,
                "ACTIVE" if user.is_active else "PENDING",
                user.created_at,
            )

        user.id = row["id"]
        return user

    async def save(self, user: User) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE users
                SET
                    status = $1,
                    activated_at = $2
                WHERE id = $3
                """,
                "ACTIVE" if user.is_active else "PENDING",
                user.activated_at,
                user.id,
            )
