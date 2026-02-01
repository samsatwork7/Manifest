import asyncio
import json
import tempfile
import os

from manifest_core.utils.common import which
from manifest_core.utils.logger import get_logger

class MassDNSResolver:
    """
    Auto-detects MassDNS binary.
    If present → uses MassDNS for ultra-fast IPv4/IPv6 resolution.
    """

    def __init__(self, rate_limit=0, resolvers_file=None):
        self.massdns_path = which("massdns")
        self.rate_limit = rate_limit
        self.resolvers_file = resolvers_file or "resolvers.txt"
        self.logger = get_logger("MassDNS")

    def is_available(self):
        return self.massdns_path is not None

    async def resolve_bulk(self, domains):
        """Run MassDNS in batch mode"""

        if not self.is_available():
            return []

        # Write domains to temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
            for d in domains:
                f.write(d + "\n")
            wordfile = f.name

        output_file = wordfile + "_out.json"

        cmd = [
            self.massdns_path,
            "-r", self.resolvers_file,
            "-o", "J",
            "-w", output_file,
            wordfile
        ]

        self.logger.info("Running MassDNS…")

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.communicate()

        results = []
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        domain = entry["query"]["name"].rstrip(".")
                        answers = entry.get("data", [])
                        ipv4 = [a["data"] for a in answers if a["type"] == "A"]
                        ipv6 = [a["data"] for a in answers if a["type"] == "AAAA"]

                        if ipv4 or ipv6:
                            results.append({
                                "subdomain": domain,
                                "ipv4": ipv4,
                                "ipv6": ipv6
                            })

                    except:
                        pass

        # Cleanup temp files
        os.remove(wordfile)
        os.remove(output_file)

        return results
