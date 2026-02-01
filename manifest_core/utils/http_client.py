import aiohttp
import asyncio

class HTTPClient:
    """Shared async HTTP client used by fingerprint + spider"""

    def __init__(self, user_agent="Manifest/1.0", timeout=5, max_conn=200):
        self.headers = {"User-Agent": user_agent}
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.connector = aiohttp.TCPConnector(limit=max_conn)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=self.timeout,
            headers=self.headers
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def get(self, url):
        """GET request with safe fallback"""
        try:
            async with self.session.get(url, allow_redirects=True) as resp:
                return {
                    "url": str(resp.url),
                    "status": resp.status,
                    "text": await resp.text(errors="ignore"),
                    "headers": dict(resp.headers)
                }
        except asyncio.TimeoutError:
            return {"error": "timeout"}
        except Exception as e:
            return {"error": str(e)}
