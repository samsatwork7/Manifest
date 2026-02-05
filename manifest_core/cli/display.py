from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def display_summary(results, args=None):
    """Display beautiful summary of results with DNS resolution stats"""
    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="cyan", width=25)
    table.add_column("Value", style="green")

    table.add_row("Target Domain", results.get("domain", "N/A"))
    table.add_row("Total Found", str(results.get("total_found", 0)))
    
    # Show resolved count if DNS was performed
    if "resolved_count" in results:
        total = results.get("total_found", 0)
        resolved = results["resolved_count"]
        if total > 0:
            resolved_pct = (resolved / total) * 100
            table.add_row("DNS Resolved", f"{resolved}/{total} ({resolved_pct:.1f}%)")
        else:
            table.add_row("DNS Resolved", f"{resolved}/{total}")
    
    table.add_row("After Filtering", str(len(results.get("subdomains", []))))

    if "passive_count" in results:
        table.add_row("Passive Sources", str(results["passive_count"]))

    if "brute_count" in results:
        table.add_row("Bruteforce", str(results["brute_count"]))

    if "perm_count" in results:
        table.add_row("Permutations", str(results["perm_count"]))

    if "takeovers" in results:
        table.add_row("Takeover Risks", str(len(results["takeovers"])))
    
    # Show DNS resolution mode if args provided
    if args and hasattr(args, 'resolve_dns') and args.resolve_dns:
        mode = "Resolved-only" if getattr(args, 'resolved_only', False) else "All subdomains"
        max_resolve = getattr(args, 'max_resolve', 0)
        if max_resolve > 0:
            mode += f" (max: {max_resolve})"
        table.add_row("DNS Mode", mode)

    console.print(
        Panel(table, title="[bold]📊 Scan Summary[/bold]", border_style="green")
    )

def display_filtered_results(categories, filter_level):
    """Display categorized subdomains in a nice format"""
    
    if not categories or filter_level == 'none':
        return
    
    console.print("\n[bold cyan]📊 Categorized Results[/bold cyan]")
    console.print("[dim]Subdomains grouped by type for easier analysis[/dim]\n")
    
    # Create a summary table
    summary_table = Table(show_header=True, header_style="bold magenta")
    summary_table.add_column("Category", style="cyan", width=20)
    summary_table.add_column("Count", justify="right")
    summary_table.add_column("Examples", style="dim")
    
    interesting_categories = [
        ('api_endpoints', '🔌 API Endpoints'),
        ('admin_panels', '🔐 Admin Panels'),
        ('infrastructure', '🖥️ Infrastructure'),
        ('development', '⚡ Development'),
        ('mail_servers', '📧 Mail Servers')
    ]
    
    for cat_key, cat_name in interesting_categories:
        if cat_key in categories and categories[cat_key]:
            subs = categories[cat_key]
            example = subs[0] if len(subs) > 0 else "None"
            if len(subs) > 1:
                example += f" (+{len(subs)-1} more)"
            
            summary_table.add_row(cat_name, str(len(subs)), example)
    
    console.print(summary_table)
    
    # Show detailed view for important categories in verbose mode
    if console.is_terminal and console.width > 80:
        console.print("\n[bold yellow]🔍 High-Value Targets:[/bold yellow]")
        
        for cat_key, cat_name in [('api_endpoints', 'API Endpoints'), 
                                  ('admin_panels', 'Admin Panels')]:
            if cat_key in categories and categories[cat_key]:
                panel_content = "\n".join([f"• {sub}" for sub in categories[cat_key][:10]])
                if len(categories[cat_key]) > 10:
                    panel_content += f"\n[dim]... and {len(categories[cat_key]) - 10} more[/dim]"
                
                console.print(Panel(
                    panel_content,
                    title=f"[bold]{cat_name}[/bold]",
                    border_style="yellow"
                ))

def display_filter_stats(original_count, filtered_count, filter_level):
    """Display filtering statistics"""
    
    if filter_level == 'none':
        return
    
    removed = original_count - filtered_count
    reduction_pct = (removed / original_count * 100) if original_count > 0 else 0
    
    console.print(f"\n[bold green]✅ Filtering Complete[/bold green]")
    
    stats_table = Table(show_header=False, box=None)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")
    
    stats_table.add_row("Filter Level", filter_level.title())
    stats_table.add_row("Original Subdomains", str(original_count))
    stats_table.add_row("After Filtering", str(filtered_count))
    stats_table.add_row("Noise Removed", f"{removed} ({reduction_pct:.1f}%)")
    
    console.print(Panel(stats_table, title="📈 Filter Statistics", border_style="green"))
    
    # Show recommendation based on reduction
    if reduction_pct > 50:
        console.print("[dim]💡 Tip: High noise reduction. Consider using 'light' filter if you need more results.[/dim]")
    elif reduction_pct < 10:
        console.print("[dim]💡 Tip: Low noise. Try 'aggressive' filter to focus only on high-value targets.[/dim]")

def highlight_interesting_subs(subdomains):
    """Highlight interesting subdomains in the output"""
    
    interesting_keywords = [
        ('admin', '🔐'),
        ('api', '🔌'),
        ('vpn', '🛡️'),
        ('jenkins', '⚙️'),
        ('git', '📦'),
        ('aws', '☁️'),
        ('azure', '☁️'),
        ('dashboard', '📊'),
        ('console', '💻')
    ]
    
    highlighted = []
    for sub in subdomains:
        sub_lower = sub.lower()
        emoji = ""
        
        for keyword, icon in interesting_keywords:
            if keyword in sub_lower:
                emoji = icon
                break
        
        if emoji:
            highlighted.append(f"[yellow]{emoji} {sub}[/yellow]")
        else:
            highlighted.append(sub)
    
    return highlighted

# Export all functions
__all__ = [
    'display_summary',
    'display_filtered_results', 
    'display_filter_stats',
    'highlight_interesting_subs'
]
