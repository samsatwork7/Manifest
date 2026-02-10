import asyncio
import socket
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from manifest_core.modules.filters import SmartFilter
from manifest_core.modules.passive import PassiveEnum

# Optional imports
try:
    from manifest_core.modules.brute import BruteforceEngine
    HAS_BRUTE = True
except ImportError:
    HAS_BRUTE = False
    BruteforceEngine = None

try:
    from manifest_core.modules.permutations import PermutationEngine
    HAS_PERMS = True
except ImportError:
    HAS_PERMS = False
    PermutationEngine = None

try:
    from manifest_core.modules.takeover import TakeoverDetector
    HAS_TAKEOVER = True
except ImportError:
    HAS_TAKEOVER = False
    TakeoverDetector = None

# Output imports
try:
    from manifest_core.output.html_report import HTMLReport
    HAS_HTML = True
except ImportError:
    HAS_HTML = False

try:
    from manifest_core.output.json_writer import JSONWriter
    HAS_JSON = True
except ImportError:
    HAS_JSON = False

try:
    from manifest_core.output.txt_writer import TXTWriter
    HAS_TXT = True
except ImportError:
    HAS_TXT = False


class ManifestRunner:
    def __init__(self, args):
        self.args = args
        self.console = Console()
    
    async def resolve_dns_batch(self, subdomains, max_workers=50, timeout=2.0, max_resolve=0):
        """Resolve IP addresses for subdomains with configurable limits"""
        resolved = {}
        
        def dns_lookup(subdomain):
            """Perform DNS lookup for a single subdomain"""
            ipv4_addresses = []
            ipv6_addresses = []
            
            try:
                # Set timeout
                socket.setdefaulttimeout(timeout)
                
                # Get all address info (IPv4 and IPv6)
                addr_info = socket.getaddrinfo(subdomain, None)
                
                for family, _, _, _, sockaddr in addr_info:
                    ip = sockaddr[0]
                    if family == socket.AF_INET:  # IPv4
                        ipv4_addresses.append(ip)
                    elif family == socket.AF_INET6:  # IPv6
                        if not ip.startswith('fe80:'):  # Skip link-local
                            ipv6_addresses.append(ip)
                
                # Also try direct IPv4 resolution as fallback
                if not ipv4_addresses:
                    try:
                        ipv4 = socket.gethostbyname_ex(subdomain)[2]
                        ipv4_addresses.extend(ipv4)
                    except:
                        pass
                        
            except (socket.gaierror, socket.timeout):
                pass  # Could not resolve
            except Exception:
                pass  # Other errors
            
            # Deduplicate and return
            ipv4_addresses = list(set(ipv4_addresses))
            ipv6_addresses = list(set(ipv6_addresses))
            
            return subdomain, ipv4_addresses, ipv6_addresses
        
        # Determine how many to resolve
        if max_resolve > 0:
            subs_to_resolve = subdomains[:max_resolve]
        else:
            subs_to_resolve = subdomains  # All
        
        if not subs_to_resolve:
            return resolved
        
        total_to_resolve = len(subs_to_resolve)
        self.console.print(f"[cyan][*][/cyan] Resolving DNS for {total_to_resolve} subdomains...")
        
        # Use ThreadPoolExecutor for parallel DNS resolution
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, dns_lookup, sub)
                for sub in subs_to_resolve
            ]
            
            # Show progress
            import sys
            resolved_count = 0
            for i, task in enumerate(asyncio.as_completed(tasks), 1):
                subdomain, ipv4, ipv6 = await task
                resolved[subdomain] = {'ipv4': ipv4, 'ipv6': ipv6}
                
                if ipv4 or ipv6:
                    resolved_count += 1
                
                # Update progress every 100 subdomains or 5%
                if i % 100 == 0 or i == total_to_resolve or i % max(1, total_to_resolve//20) == 0:
                    percent = (i / total_to_resolve) * 100
                    sys.stdout.write(f"\r[cyan][*][/cyan] Progress: {i}/{total_to_resolve} ({percent:.1f}%) - Resolved: {resolved_count}")
                    sys.stdout.flush()
            
            if total_to_resolve > 0:
                print()  # New line after progress
        
        self.console.print(f"[green][✓][/green] Successfully resolved {resolved_count}/{total_to_resolve} subdomains")
        
        return resolved

    async def run(self):
        results = {}
        
        # Track total time
        start_time = time.time()

        # ─────────────────────────────────────────────
        # 1. PASSIVE ENUMERATION
        # ─────────────────────────────────────────────
        self.console.print("[yellow][*][/yellow] Collecting subdomains...")
        passive_engine = PassiveEnum(self.args.domain)
        passive_subs = await passive_engine.run()
        results["passive_count"] = len(passive_subs)

        all_subdomains = list(set(passive_subs))
        results["original_count"] = len(all_subdomains)

        # ─────────────────────────────────────────────
        # 2. BRUTEFORCE ENUMERATION
        # ─────────────────────────────────────────────
        brute_subs = []
        if (self.args.brute or self.args.all) and HAS_BRUTE:
            self.console.print("[yellow][*][/yellow] Bruteforce enumeration...")
            brute_engine = BruteforceEngine(self.args.domain, wordlist=self.args.wordlist)
            brute_subs = await brute_engine.run(threads=self.args.threads)

            all_subdomains = list(set(all_subdomains + brute_subs))
            results["brute_count"] = len(brute_subs)

        elif (self.args.brute or self.args.all) and not HAS_BRUTE:
            self.console.print("[yellow][!][/yellow] Bruteforce module not available")
            results["brute_count"] = 0

        # ─────────────────────────────────────────────
        # 3. PERMUTATIONS
        # ─────────────────────────────────────────────
        if (self.args.perms or self.args.all) and HAS_PERMS:
            self.console.print("[yellow][*][/yellow] Generating permutations...")
            perm_engine = PermutationEngine()
            source_subs = passive_subs
            if brute_subs:
                source_subs = source_subs + brute_subs

            perm_subs = perm_engine.generate(source_subs)

            all_subdomains = list(set(all_subdomains + perm_subs))
            results["perm_count"] = len(perm_subs)

        elif (self.args.perms or self.args.all) and not HAS_PERMS:
            self.console.print("[yellow][!][/yellow] Permutations module not available")
            results["perm_count"] = 0

        # ────────────────────────────────────────────
        # 4. SMART FILTERING
        # ─────────────────────────────────────────────
        if hasattr(self.args, "filter_level") and self.args.filter_level != "none":
            self.console.print("[cyan][*][/cyan] Applying smart filtering...")

            filter_engine = SmartFilter(self.args.domain)
            original = len(all_subdomains)

            filtered = filter_engine.filter_subdomains(all_subdomains, self.args.filter_level)

            removed = original - len(filtered)
            self.console.print(f"[green][+][/green] Filtered out {removed} noisy subdomains")
            self.console.print(f"[green][+][/green] Kept {len(filtered)} high-quality targets")

            all_subdomains = filtered
            results["filtered_count"] = len(filtered)
            results["removed_count"] = removed

        # ─────────────────────────────────────────────
        # 5. DNS RESOLUTION (Conditional)
        # ─────────────────────────────────────────────
        resolved_ips = {}

        # --resolved-only requires DNS resolution to be meaningful
        if getattr(self.args, "resolved_only", False) and not getattr(self.args, "resolve_dns", False):
            self.console.print("[yellow][!][/yellow] --resolved-only requires DNS resolution; enabling --resolve-dns automatically")
            self.args.resolve_dns = True

        if getattr(self.args, "resolve_dns", False) and all_subdomains:
            # Get resolution parameters
            timeout = getattr(self.args, "dns_timeout", 2.0)
            max_resolve = getattr(self.args, "max_resolve", 0)  # 0 = all
            
            resolved_ips = await self.resolve_dns_batch(
                all_subdomains,
                max_workers=50,
                timeout=timeout,
                max_resolve=max_resolve
            )
            results["resolved_ips"] = resolved_ips
            results["resolved_count"] = sum(1 for ips in resolved_ips.values() if ips['ipv4'] or ips['ipv6'])

        # ─────────────────────────────────────────────
        # 6. TAKEOVER DETECTION
        # ─────────────────────────────────────────────
        if HAS_TAKEOVER:
            self.console.print("[yellow][*][/yellow] Checking for subdomain takeovers...")

            takeover_engine = TakeoverDetector(self.args.domain)

            if all_subdomains:
                sample_size = min(100, len(all_subdomains))
                sample = all_subdomains[:sample_size]

                self.console.print(
                    f"[cyan][*][/cyan] Optimized takeover scan on {sample_size} subdomains"
                )

                takeovers = await takeover_engine.run(sample)
                results["takeovers"] = takeovers

                if takeovers:
                    self.console.print(
                        f"[red][!][/red] Found {len(takeovers)} potential takeover vulnerabilities"
                    )
                else:
                    self.console.print("[green][✓][/green] No takeover vulnerabilities found")
            else:
                results["takeovers"] = []
        else:
            results["takeovers"] = []
            self.console.print("[yellow][!][/yellow] Takeover detection module not available")

        # ─────────────────────────────────────────────
        # 7. FINAL RESULT AGGREGATION
        # ─────────────────────────────────────────────
        results["subdomains"] = all_subdomains
        results["total_found"] = len(all_subdomains)
        results["domain"] = self.args.domain
        
        # Add duration
        total_time = time.time() - start_time
        results["duration"] = total_time

        # ─────────────────────────────────────────────
        # 8. OUTPUT REPORTS (HTML, JSON, TXT)
        # ─────────────────────────────────────────────
        output_dir = getattr(self.args, "output", None)
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            self.console.print(f"[cyan][*][/cyan] Output directory: {output_dir}")
        
        # Get timestamp for all reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_domain = self.args.domain.replace(".", "_")
        
        # Determine which subdomains to include in reports
        if getattr(self.args, "resolved_only", False):
            report_subdomains = [
                sub for sub in all_subdomains
                if sub in resolved_ips and (resolved_ips[sub]['ipv4'] or resolved_ips[sub]['ipv6'])
            ]
            self.console.print(
                f"[cyan][*][/cyan] Resolved-only mode enabled: {len(report_subdomains)}/{len(all_subdomains)} subdomains"
            )
        else:
            report_subdomains = all_subdomains

        # HTML Report
        if getattr(self.args, "html", False) and HAS_HTML:
            try:
                self.console.print("[yellow][*][/yellow] Generating HTML report...")
                
                # Build subdomain list for HTML with resolved IPs
                html_subdomains = []
                for sub in report_subdomains:
                    ip_data = resolved_ips.get(sub, {'ipv4': [], 'ipv6': []})
                    
                    # Mark if resolved
                    resolved = bool(ip_data.get('ipv4') or ip_data.get('ipv6'))

                    html_subdomains.append({
                        "subdomain": sub,
                        "interesting": any(
                            kw in sub.lower()
                            for kw in ["admin", "api", "vpn", "dashboard", "secure", "portal", "console"]
                        ),
                        "resolved": resolved,
                        "ipv4": ip_data.get('ipv4', []),
                        "ipv6": ip_data.get('ipv6', [])
                    })
                
                # Build takeover data for HTML
                html_takeovers = []
                if "takeovers" in results and results["takeovers"]:
                    for takeover in results["takeovers"]:
                        if isinstance(takeover, dict):
                            html_takeovers.append(takeover)
                        else:
                            html_takeovers.append({
                                "subdomain": str(takeover),
                                "service": "Unknown",
                                "cname": "N/A"
                            })
                
                # Generate filename and path
                if output_dir:
                    html_path = os.path.join(output_dir, f"manifest_{safe_domain}_{timestamp}.html")
                else:
                    html_path = f"manifest_{safe_domain}_{timestamp}.html"
                
                # Write HTML report
                HTMLReport.write(html_path, self.args.domain, html_subdomains, html_takeovers)
                
                self.console.print(f"[green][✓][/green] HTML report saved: [cyan]{html_path}[/cyan]")
                
            except Exception as e:
                self.console.print(f"[red][!][/red] Failed to generate HTML report: {e}")
                import traceback
                self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
        elif getattr(self.args, "html", False) and not HAS_HTML:
            self.console.print("[yellow][!][/yellow] HTML report module not available")
        
        # JSON Report
        if getattr(self.args, "json", False) and HAS_JSON:
            try:
                self.console.print("[yellow][*][/yellow] Generating JSON report...")
                
                # Prepare data for JSON
                json_data = {
                    'metadata': {
                        'tool': 'Manifest v2.0',
                        'domain': self.args.domain,
                        'scan_date': datetime.now().isoformat(),
                        'duration': total_time,
                        'options': vars(self.args)
                    },
                    'statistics': {
                        'total_subdomains': len(all_subdomains),
                        'live_subdomains': results.get('resolved_count', 0),
                        'takeover_candidates': len(results.get('takeovers', [])),
                        'passive_count': results.get('passive_count', 0),
                        'brute_count': results.get('brute_count', 0),
                        'perm_count': results.get('perm_count', 0),
                        'filtered_count': results.get('filtered_count', len(all_subdomains))
                    },
                    'subdomains': report_subdomains,
                    'resolved_ips': resolved_ips,
                    'takeovers': results.get('takeovers', [])
                }
                
                # Generate filename and path
                if output_dir:
                    json_path = os.path.join(output_dir, f"manifest_{safe_domain}_{timestamp}.json")
                else:
                    json_path = f"manifest_{safe_domain}_{timestamp}.json"
                
                # Write JSON report
                JSONWriter.write_enhanced(json_path, json_data)
                
                self.console.print(f"[green][✓][/green] JSON report saved: [cyan]{json_path}[/cyan]")
                
            except Exception as e:
                self.console.print(f"[red][!][/red] Failed to generate JSON report: {e}")
                import traceback
                self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
        elif getattr(self.args, "json", False) and not HAS_JSON:
            self.console.print("[yellow][!][/yellow] JSON report module not available")
        
        # TXT Report
        if getattr(self.args, "txt", False) and HAS_TXT:
            try:
                self.console.print("[yellow][*][/yellow] Generating TXT report...")
                
                # Generate filename and path
                if output_dir:
                    txt_path = os.path.join(output_dir, f"manifest_{safe_domain}_{timestamp}.txt")
                else:
                    txt_path = f"manifest_{safe_domain}_{timestamp}.txt"
                
                # Prepare data for TXT
                txt_data = []
                for sub in report_subdomains:
                    ip_data = resolved_ips.get(sub, {})
                    ipv4 = ip_data.get('ipv4', [])
                    ipv6 = ip_data.get('ipv6', [])
                    
                    if ipv4 or ipv6:
                        ips = ', '.join(ipv4 + ipv6)
                        txt_data.append({'subdomain': sub, 'ips': ips})
                    else:
                        txt_data.append({'subdomain': sub, 'ips': ''})
                
                # Write TXT report
                TXTWriter.write(txt_path, txt_data)
                
                self.console.print(f"[green][✓][/green] TXT report saved: [cyan]{txt_path}[/cyan]")
                
            except Exception as e:
                self.console.print(f"[red][!][/red] Failed to generate TXT report: {e}")
                import traceback
                self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
        elif getattr(self.args, "txt", False) and not HAS_TXT:
            self.console.print("[yellow][!][/yellow] TXT report module not available")

        # ─────────────────────────────────────────────
        # 9. RETURN FINAL RESULTS
        # ─────────────────────────────────────────────
        return results
