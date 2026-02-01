import asyncio
import os

from manifest_core.cli.progress import RichProgress
from manifest_core.modules.passive import PassiveEnum
from manifest_core.modules.brute import BruteforceEngine
from manifest_core.modules.permutations import PermutationEngine

from manifest_core.dns.resolver import DNSResolver
from manifest_core.dns.massdns import MassDNSResolver
from manifest_core.dns.wildcard import WildcardDetector
from manifest_core.dns.dedupe import Deduplicator

from manifest_core.modules.takeover import TakeoverScanner

from manifest_core.utils.common import ensure_dir
from manifest_core.utils.logger import get_logger

from manifest_core.output.json_writer import JSONWriter
from manifest_core.output.txt_writer import TXTWriter
from manifest_core.output.html_report import HTMLReport


class ManifestRunner:

    def __init__(self, args):
        self.args = args
        self.domain = args.domain
        self.logger = get_logger()

        ensure_dir(args.output)

    async def run(self):
        with RichProgress() as ui:

            #──────────────────────────────────────────────
            # 1. PASSIVE ENUMERATION
            #──────────────────────────────────────────────
            ui.add_task("passive", f"[white]Passive enumeration for {self.domain}[/white]")

            passive = PassiveEnum(self.domain)
            passive_results = await passive.run()

            ui.complete("passive", f"[green]Passive: {len(passive_results)} found")


            #──────────────────────────────────────────────
            # 2. BRUTE FORCE
            #──────────────────────────────────────────────
            brute_results = []
            if self.args.brute or self.args.all:
                ui.add_task("brute", "[white]Bruteforce enumeration[/white]")
                brute = BruteforceEngine(self.domain, self.args.wordlist)
                brute_results = brute.generate()
                ui.complete("brute", f"[green]Brute: {len(brute_results)} candidates")


            #──────────────────────────────────────────────
            # 3. PERMUTATION ENGINE
            #──────────────────────────────────────────────
            perms_results = []
            if self.args.perms or self.args.all:
                ui.add_task("perms", "[white]Generating permutations[/white]")
                perms = PermutationEngine()
                perms_results = perms.generate(passive_results)
                ui.complete("perms", f"[green]Perms: {len(perms_results)} generated")


            #──────────────────────────────────────────────
            # 4. DNS RESOLUTION (MassDNS → fallback)
            #──────────────────────────────────────────────
            ui.add_task("dns", "[white]Resolving DNS[/white]")

            all_candidates = list(set(passive_results + brute_results + list(perms_results)))

            massdns = MassDNSResolver()
            if massdns.is_available():
                resolved = await massdns.resolve_bulk(all_candidates)
            else:
                resolver = DNSResolver(
                    concurrency=self.args.threads,
                    timeout=self.args.timeout
                )
                resolved = await resolver.resolve_bulk(all_candidates)

            ui.complete("dns", f"[green]DNS: {len(resolved)} live subdomains")


            #──────────────────────────────────────────────
            # 5. WILDCARD DETECTION + FILTER
            #──────────────────────────────────────────────
            ui.add_task("wildcard", "[white]Detecting wildcard[/white]")

            resolver = DNSResolver()
            wildcard = WildcardDetector(resolver)

            is_wc, wc_ips = await wildcard.detect(self.domain)

            if is_wc:
                resolved = wildcard.filter_wildcard(resolved, wc_ips)

            ui.complete("wildcard", f"[yellow]Wildcard filtering done")


            #──────────────────────────────────────────────
            # 6. TAKEOVER DETECTION
            #──────────────────────────────────────────────
            ui.add_task("takeover", "[white]Checking for takeovers[/white]")

            takeover = TakeoverScanner()
            takeovers = [
                r for r in resolved
                if r.get("cname") and takeover.detect(r["cname"])
            ]

            ui.complete("takeover", f"[red]{len(takeovers)} takeover candidates")


            #──────────────────────────────────────────────
            # 7. DEDUPLICATION
            #──────────────────────────────────────────────
            resolved = Deduplicator.dedupe(resolved)


            #──────────────────────────────────────────────
            # 8. FINAL RESULT DICT
            #──────────────────────────────────────────────
            results = {
                "domain": self.domain,
                "subdomains": resolved,
                "takeovers": takeovers,
            }


            #──────────────────────────────────────────────
            # 9. OUTPUT (JSON / TXT / HTML)
            #──────────────────────────────────────────────
            output_dir = self.args.output
            domain = self.domain

            # JSON
            if self.args.json:
                JSONWriter.write(
                    os.path.join(output_dir, f"{domain}.json"),
                    results
                )

            # TXT list
            if self.args.txt:
                TXTWriter.write(
                    os.path.join(output_dir, f"{domain}.txt"),
                    results["subdomains"]
                )

            # HTML Dashboard
            if self.args.html:
                HTMLReport.write(
                    os.path.join(output_dir, f"{domain}.html"),
                    domain,
                    results["subdomains"],
                    results["takeovers"]
                )

            return results
