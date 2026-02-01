import random
import string

class WildcardDetector:
    """
    Detect wildcard DNS and filter results.
    """

    def __init__(self, resolver):
        self.resolver = resolver

    def _random_sub(self, domain):
        return f"{''.join(random.choices(string.ascii_lowercase, k=16))}.{domain}"

    async def detect(self, domain):
        """Detect wildcard by resolving random subdomains"""
        test_domains = [self._random_sub(domain) for _ in range(3)]
        responses = []

        for d in test_domains:
            res = await self.resolver.resolve(d)
            if res:
                responses.append(res)

        if not responses:
            return False, {}

        return True, {
            "ipv4": {ip for r in responses for ip in r["ipv4"]},
            "ipv6": {ip for r in responses for ip in r["ipv6"]}
        }

    def filter_wildcard(self, results, wildcard_ips):
        """Remove wildcard IP matches"""
        filtered = []
        for r in results:
            ipv4_ok = any(ip not in wildcard_ips["ipv4"] for ip in r.get("ipv4", []))
            ipv6_ok = any(ip not in wildcard_ips["ipv6"] for ip in r.get("ipv6", []))

            if ipv4_ok or ipv6_ok:
                filtered.append(r)

        return filtered
