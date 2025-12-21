# app/infrastructure/db/migrate.py
import pathlib
import asyncpg
import logging
import re

logger = logging.getLogger(__name__)

MIGRATIONS_PATH = pathlib.Path(__file__).parent / "migrations"
MIGRATION_RE = re.compile(r"^(\d+)_.*\.sql$")

# Naming convention for migration files
# <version>_<description>.sql
def load_migrations():
    migrations = []

    for path in MIGRATIONS_PATH.glob("*.sql"):
        match = MIGRATION_RE.match(path.name)
        if not match:
            raise RuntimeError(
                f"Invalid migration filename: {path.name}. "
                "Expected format: <version>_<description>.sql"
            )

        version = int(match.group(1))
        migrations.append((version, path))

    migrations.sort(key=lambda x: x[0])
    return migrations

async def run_migrations(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)

        rows = await conn.fetch("SELECT version FROM schema_migrations")
        applied = {row["version"] for row in rows}

        for version, path in load_migrations():
            if version in applied:
                continue

            logger.info("Applying migration %s", path.name)
            sql = path.read_text()

            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute(
                    "INSERT INTO schema_migrations (version) VALUES ($1)",
                    version,
                )
