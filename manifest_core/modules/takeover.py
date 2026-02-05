import asyncio
import re

class TakeoverDetector:
    """
    Detect potential subdomain takeovers
    """

    # Common CNAME patterns that indicate vulnerable services
    VULNERABLE_CNAMES = {
        # GitHub Pages
        r'\.github\.io$': 'GitHub Pages',
        r'\.github\.com$': 'GitHub',
        r'\.githubusercontent\.com$': 'GitHub',

        # AWS/S3
        r'\.s3\.amazonaws\.com$': 'AWS S3 Bucket',
        r'\.s3-website[.-]': 'AWS S3 Website',
        r'\.amazonaws\.com$': 'AWS Service',

        # Azure
        r'\.azurewebsites\.net$': 'Azure App Service',
        r'\.cloudapp\.azure\.com$': 'Azure Cloud Service',
        r'\.azurestaticapps\.net$': 'Azure Static Apps',

        # Heroku
        r'\.herokuapp\.com$': 'Heroku App',
        r'\.herokudns\.com$': 'Heroku DNS',

        # Google Cloud
        r'\.appspot\.com$': 'Google App Engine',
        r'\.cloudfunctions\.net$': 'Google Cloud Functions',

        # Cloudflare
        r'\.pages\.dev$': 'Cloudflare Pages',
        r'\.workers\.dev$': 'Cloudflare Workers',

        # Vercel / Netlify
        r'\.vercel\.app$': 'Vercel',
        r'\.now\.sh$': 'Vercel (Legacy)',
        r'\.netlify\.app$': 'Netlify',

        # WordPress
        r'\.wordpress\.com$': 'WordPress.com',
        r'\.wpengine\.com$': 'WP Engine',

        # Others
        r'\.readthedocs\.io$': 'ReadTheDocs',
        r'\.firebaseapp\.com$': 'Firebase',
        r'\.surge\.sh$': 'Surge.sh',
        r'\.pantheonsite\.io$': 'Pantheon',
        r'\.acquia-sites\.com$': 'Acquia',
        r'\.fly\.dev$': 'Fly.io',
        r'\.render\.com$': 'Render',
    }

    def __init__(self, domain):
        self.domain = domain
        self.vulnerabilities = []

    async def check_cname(self, subdomain, cname):
        """Check if a CNAME indicates potential takeover"""
        for pattern, service in self.VULNERABLE_CNAMES.items():
            if re.search(pattern, cname, re.IGNORECASE):
                return {
                    'subdomain': subdomain,
                    'cname': cname,
                    'service': service,
                    'vulnerable': True,
                    'pattern': pattern
                }
        return None

    async def check_subdomain(self, subdomain):
        """Check a single subdomain for takeover vulnerability"""
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.timeout = 2
            resolver.lifetime = 2

            # Check CNAME records
            try:
                answers = resolver.resolve(subdomain, 'CNAME')
                for rdata in answers:
                    cname = str(rdata.target).rstrip('.')
                    result = await self.check_cname(subdomain, cname)
                    if result:
                        self.vulnerabilities.append(result)
                        return result
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
                pass

        except Exception:
            pass  # ignore DNS errors

        return None

    async def run(self, subdomains, max_concurrent=20):
        """
        Check multiple subdomains for takeover vulnerabilities
        Optimized with progress bar for large batches
        """
        from rich.progress import Progress, SpinnerColumn, TextColumn

        self.vulnerabilities = []

        if not subdomains:
            return []

        # ──────────────────────────────
        # With progress bar (large list)
        # ──────────────────────────────
        if len(subdomains) > 20:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:

                task = progress.add_task(
                    f"Checking {len(subdomains)} subdomains...",
                    total=len(subdomains)
                )

                semaphore = asyncio.Semaphore(max_concurrent)

                async def check_with_semaphore(subdomain):
                    async with semaphore:
                        result = await self.check_subdomain(subdomain)
                        progress.update(task, advance=1)
                        return result

                tasks = [check_with_semaphore(sub) for sub in subdomains]
                results = await asyncio.gather(*tasks, return_exceptions=True)

        else:
            # ──────────────────────────────
            # No progress bar (small list)
            # ──────────────────────────────
            semaphore = asyncio.Semaphore(max_concurrent)

            async def check_with_semaphore(subdomain):
                async with semaphore:
                    return await self.check_subdomain(subdomain)

            tasks = [check_with_semaphore(sub) for sub in subdomains]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter valid results
        valid_results = [
            r for r in results
            if r is not None and not isinstance(r, Exception)
        ]

        return self.vulnerabilities

    def get_report(self):
        """Generate a takeover vulnerability report"""
        if not self.vulnerabilities:
            return "No takeover vulnerabilities detected."

        report = ["⚠️  Potential Subdomain Takeover Vulnerabilities:", ""]

        for vuln in self.vulnerabilities:
            report.append(f"🔴 {vuln['subdomain']}")
            report.append(f"   Service: {vuln['service']}")
            report.append(f"   CNAME: {vuln['cname']}")
            report.append("")

        return "\n".join(report)
