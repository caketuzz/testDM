from pathlib import Path

import pytest
from app.infrastructure.db import migrate
from app.infrastructure.db.migrate import load_migrations, run_migrations
from tests.mock.fakepool import FakePool


async def test_run_migrations_is_idempotent():
    pool = FakePool()

    # 1er run
    await run_migrations(pool)
    inserts_after_first = [
        sql for sql in pool.conn.executed
        if sql.strip().startswith("INSERT INTO schema_migrations")
    ]

    # 2e run
    await run_migrations(pool)
    inserts_after_second = [
        sql for sql in pool.conn.executed
        if sql.strip().startswith("INSERT INTO schema_migrations")
    ]

    # Une seule migration appliquée
    assert len(inserts_after_first) == 1
    assert inserts_after_first == inserts_after_second


def test_load_migrations_raises_on_invalid_filename(tmp_path, monkeypatch):
    # Crée un fichier de migration invalide
    invalid_file = tmp_path / "invalid_name.sql"
    invalid_file.write_text("-- invalid migration")

    # Redirige MIGRATIONS_PATH vers ce dossier temporaire
    monkeypatch.setattr(migrate, "MIGRATIONS_PATH", tmp_path)

    with pytest.raises(RuntimeError, match="Invalid migration filename"):
        migrate.load_migrations()
