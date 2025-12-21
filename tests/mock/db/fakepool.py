# tests/mock/fakepool.py

class FakeTransaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class FakeConn:
    def __init__(self):
        self.executed = []
        self.migrations = set()

    async def execute(self, sql: str, *args):
        self.executed.append(sql.strip())
        if sql.strip().startswith("INSERT INTO schema_migrations"):
            self.migrations.add(args[0])

    async def fetch(self, sql: str):
        if sql.strip().startswith("SELECT version FROM schema_migrations"):
            return [{"version": v} for v in self.migrations]
        return []

    # ⚠️ PAS async
    def transaction(self):
        return FakeTransaction()


class FakeAcquireCtx:
    def __init__(self, conn: FakeConn):
        self.conn = conn

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        pass


class FakePool:
    def __init__(self):
        self.conn = FakeConn()
        self.closed = False

    # ⚠️ PAS async
    def acquire(self):
        return FakeAcquireCtx(self.conn)

    async def close(self):
        self.closed = True
