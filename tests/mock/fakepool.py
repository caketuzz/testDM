class FakeConn:
    async def execute(self, query: str):
        return None

class FakeAcquireCtx:
    async def __aenter__(self):
        return FakeConn()
    async def __aexit__(self, exc_type, exc, tb):
        return False

class FakePool:
    def __init__(self):
        self.closed = False
        
    def acquire(self):
        return FakeAcquireCtx()
    
    async def close(self):
        self.closed = True