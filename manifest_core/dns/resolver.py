import asyncio
import dns.asyncresolver
import dns.exception

from manifest_core.utils.limiter import RateLimiter


class DNSResolver:
    """
    Async DNS Resolver (IPv4 + IPv6)
    Used when MassDNS is NOT available.
    """

    def __init__(self, concurrency=500, timeout=3, retries=2, rate_limit=0):
        self.timeout = timeout
        self.retries = retries
        self.semaphore = asyncio.Semaphore(concurrency)
        self.rate_limiter = RateLimiter(rate_limit)

        # Separate resolvers for A + AAAA
        self.resolver_v4 = dns.asyncresolver.Resolver()
        self.resolver_v4.timeout = timeout
        self.resolver_v4.lifetime = timeout

        self.resolver_v6 = dns.asyncresolver.Resolver()
        self.resolver_v6.timeout = timeout
        self.resolver_v6.lifetime = timeout

    async def _resolve_once(self, domain, record_type):
        """Single record resolution"""
        try:
            res = await asyncio.wait_for(
                (self.resolver_v4 if record_type == "A" else self.resolver_v6).resolve(domain, record_type),
                timeout=self.timeout
            )
            return [r.to_text() for r in res]
        except:
            return []

    async def resolve(self, domain):
        """Resolve A + AAAA records with retries"""
        async with self.semaphore:
            await self.rate_limiter.wait()

            a_records, aaaa_records = [], []

            for _ in range(self.retries):
                a_records = await self._resolve_once(domain, "A")
                if a_records:
                    break

            for _ in range(self.retries):
                aaaa_records = await self._resolve_once(domain, "AAAA")
                if aaaa_records:
                    break

            if not a_records and not aaaa_records:
                return None

            return {
                "subdomain": domain,
                "ipv4": a_records,
                "ipv6": aaaa_records
            }

    async def resolve_bulk(self, domains):
        """Bulk resolver"""
        tasks = [self.resolve(d) for d in domains]
        results = await asyncio.gather(*tasks)

        return [r for r in results if r]
