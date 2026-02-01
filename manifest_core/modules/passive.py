import aiohttp
import asyncio
import json
import re

class PassiveEnum:
    """
    Free passive enumeration (no API keys required).
    """

    def __init__(self, domain, user_agent="Manifest/1.0"):
        self.domain = domain
        self.headers = {"User-Agent": user_agent}

    async def _fetch_json(self, session, url):
        try:
            async with session.get(url, headers=self.headers, timeout=10) as r:
                return await r.json(content_type=None)
        except:
            return None

    async def _fetch_text(self, session, url):
        try:
            async with session.get(url, headers=self.headers, timeout=10) as r:
                return await r.text()
        except:
            return ""

    # ─────────────────────────────────────────────
    # FREE DATA SOURCES
    # ─────────────────────────────────────────────

    async def crtsh(self, session):
        """crt.sh certificate transparency"""
        url = f"https://crt.sh/?q={self.domain}&output=json"
        data = await self._fetch_json(session, url)
        if not data:
            return []
        return list({entry["name_value"] for entry in data})

    async def hackertarget(self, session):
        """HackerTarget free subdomain enum"""
        url = f"https://api.hackertarget.com/hostsearch/?q={self.domain}"
        text = await self._fetch_text(session, url)
        return [line.split(",")[0] for line in text.splitlines() if line]

    async def otx(self, session):
        """AlienVault OTX passive DNS (public endpoint)"""
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{self.domain}/passive_dns"
        data = await self._fetch_json(session, url)
        if not data:
            return []
        return [d["hostname"] for d in data.get("passive_dns", []) if "hostname" in d]

    async def threatcrowd(self, session):
        url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={self.domain}"
        data = await self._fetch_json(session, url)
        if not data:
            return []
        return data.get("subdomains", [])

    async def bufferover(self, session):
        url = f"https://dns.bufferover.run/dns?q=.{self.domain}"
        data = await self._fetch_json(session, url)
        if not data:
            return []

        records = data.get("FDNS_A", []) + data.get("RDNS", [])
        subs = []
        for r in records:
            parts = r.split(",")
            if len(parts) == 2:
                subs.append(parts[1])

        return subs

    async def urlscan(self, session):
        url = f"https://urlscan.io/api/v1/search/?q=domain:{self.domain}"
        data = await self._fetch_json(session, url)
        if not data:
            return []

        return [
            item.get("page", {}).get("domain")
            for item in data.get("results", [])
            if item.get("page")
        ]

    async def archive_org(self, session):
        url = f"http://web.archive.org/cdx/search/cdx?url=*.{self.domain}/*&output=json&fl=original"
        json_data = await self._fetch_json(session, url)
        if not json_data:
            return []

        subs = []
        for row in json_data[1:]:
            url = row[0]
            m = re.match(r"https?://([^/]+)/", url)
            if m:
                subs.append(m.group(1))

        return subs

    # ─────────────────────────────────────────────
    # RUN ALL SOURCES
    # ─────────────────────────────────────────────

    async def run(self):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.crtsh(session),
                self.hackertarget(session),
                self.otx(session),
                self.threatcrowd(session),
                self.bufferover(session),
                self.urlscan(session),
                self.archive_org(session),
            ]

            results = await asyncio.gather(*tasks)

        # Flatten + normalize
        final = set()
        for group in results:
            for sub in group:
                if sub and sub.endswith(self.domain):
                    sub = sub.strip().lower().replace("*.", "")
                    final.add(sub)

        return sorted(final)
