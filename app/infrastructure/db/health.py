import asyncpg


async def check_db(pool: asyncpg.Pool) -> bool:
    async with pool.acquire() as conn:
        await conn.execute("SELECT 1")
    return True
