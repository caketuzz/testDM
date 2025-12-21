class FakeConn:
    def __init__(self, row=None):
        self.row = row
        self.executed = []

    async def fetchrow(self, sql, *args):
        return self.row

    async def execute(self, sql, *args):
        self.executed.append((sql, args))


class FakeAcquireCtx:
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakePool:
    def __init__(self, conn):
        self.conn = conn

    def acquire(self):
        return FakeAcquireCtx(self.conn)
