import asyncio
import socket
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

        # ─────────────────────────────────────────────
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

        # ─────────────────────────────────────────────
        # 8. HTML REPORT GENERATION
        # ─────────────────────────────────────────────
        if getattr(self.args, "html", False):
            try:
                self.console.print("[yellow][*][/yellow] Generating HTML report...")
                
                # Determine which subdomains to include in report
                if getattr(self.args, "resolved_only", False) and resolved_ips:
                    # Only include subdomains that resolved
                    subs_for_report = [sub for sub in all_subdomains 
                                     if sub in resolved_ips and (resolved_ips[sub]['ipv4'] or resolved_ips[sub]['ipv6'])]
                    self.console.print(f"[cyan][*][/cyan] Showing {len(subs_for_report)} resolved subdomains in report")
                else:
                    # Show ALL subdomains in HTML report
                    subs_for_report = all_subdomains
                    self.console.print(f"[cyan][*][/cyan] Including all {len(all_subdomains)} subdomains in HTML report")
                
                # Build subdomain list for HTML with resolved IPs
                html_subdomains = []
                for sub in subs_for_report:
                    ip_data = resolved_ips.get(sub, {'ipv4': [], 'ipv6': []})
                    
                    # Mark interesting subdomains
                    interesting_keywords = ["admin", "api", "vpn", "dashboard", "secure", "portal", "console"]
                    interesting = any(kw in sub.lower() for kw in interesting_keywords)
                    
                    # Mark if resolved
                    resolved = bool(ip_data.get('ipv4') or ip_data.get('ipv6'))
                    
                    html_subdomains.append({
                        "subdomain": sub,
                        "interesting": interesting,
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
                
                # Directory handling
                import os
                from datetime import datetime
                
                output_dir = self.args.output if getattr(self.args, "output", None) else "."
                
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_domain = self.args.domain.replace(".", "_")
                filename = f"manifest_{safe_domain}_{timestamp}.html"
                filepath = os.path.join(output_dir, filename)
                
                # Write HTML report
                from manifest_core.output.html_report import HTMLReport
                HTMLReport.write(filepath, self.args.domain, html_subdomains, html_takeovers)
                
                self.console.print(f"[green][✓][/green] HTML report saved: [cyan]{filepath}[/cyan]")
                
                # Optional JSON export
                if getattr(self.args, "json", False):
                    from manifest_core.output.json_writer import JSONWriter
                    json_path = filepath.replace(".html", ".json")
                    JSONWriter.write(json_path, results)
                    self.console.print(f"[green][✓][/green] JSON report saved: [cyan]{json_path}[/cyan]")
                
            except ImportError as e:
                self.console.print(f"[red][!][/red] HTML report module error: {e}")
            except Exception as e:
                self.console.print(f"[red][!][/red] Failed to generate HTML report: {e}")
                import traceback
                self.console.print(f"[dim]{traceback.format_exc()}[/dim]")

        # ─────────────────────────────────────────────
        # 9. PREPARE FINAL RESULTS
        # ─────────────────────────────────────────────
        # Summary display is now handled in main.py
        # Return results to main function for display
        return results
