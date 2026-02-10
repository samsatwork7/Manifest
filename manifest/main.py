#!/usr/bin/env python3

import asyncio
from rich.console import Console
from manifest_core.cli.parser import build_parser
from manifest_core.cli.banner import print_banner
from manifest_core.cli.runner import ManifestRunner
from manifest_core.cli.display import (
    display_summary,
    display_filtered_results,
    display_filter_stats,
    highlight_interesting_subs
)

def main():
    parser = build_parser()
    args = parser.parse_args()
    
    console = Console()
    print_banner()
    
    # Show filter level being used
    if hasattr(args, 'filter_level') and args.filter_level != 'none':
        console.print(f"[dim]Filter level: {args.filter_level}[/dim]\n")
    
    # Run the scan safely
    runner = ManifestRunner(args)

    try:
        results = asyncio.run(runner.run())

    except KeyboardInterrupt:
        console.print("\n[red][!][/red] Keyboard interrupt received. Exiting cleanly...\n")
        return

    except Exception as e:
        console.print(f"\n[red][!][/red] Unexpected error: {e}")
        return
    
    # Display the main summary
    if results:
        display_summary(results, args)
        
        # Show filtering statistics if requested
        if hasattr(args, 'filter_stats') and args.filter_stats:
            original_count = results.get('original_count', 0)
            filtered_count = len(results.get('subdomains', []))
            if original_count > 0 and filtered_count != original_count:
                display_filter_stats(original_count, filtered_count, args.filter_level)
        
        # Show categorized results if requested
        if hasattr(args, 'categorize') and args.categorize and 'categories' in results:
            display_filtered_results(results['categories'], args.filter_level)
        
        # Highlight interesting subdomains in final output
        if 'subdomains' in results and results['subdomains']:
            console.print("\n[bold green]📋 Discovered Subdomains:[/bold green]")
            highlighted = highlight_interesting_subs(results['subdomains'])
            for sub in highlighted[:20]:  # Show first 20
                console.print(f"  {sub}")
            
            if len(results['subdomains']) > 20:
                console.print(f"  [dim]... and {len(results['subdomains']) - 20} more[/dim]")
    
    console.print("\n[bold green]✅ Recon completed successfully![/bold green]")

if __name__ == "__main__":
    main()
