import asyncio
import time

class RateLimiter:
    """Async rate limiter for DNS and HTTP"""

    def __init__(self, rate_limit=0):
        self.rate_limit = rate_limit
        self.last_ts = 0

    async def wait(self):
        if self.rate_limit == 0:
            return

        now = time.time()
        diff = now - self.last_ts
        wait = max(0, 1 / self.rate_limit - diff)
        if wait > 0:
            await asyncio.sleep(wait)

        self.last_ts = time.time()
