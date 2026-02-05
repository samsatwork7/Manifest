import argparse

def build_parser():
    parser = argparse.ArgumentParser(
        description="Manifest v2.0 — Next-Gen Reconnaissance Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -d example.com --passive
  %(prog)s -d example.com --all --resolve-dns
  %(prog)s -d example.com --passive --html --json --txt --output reports/
        """
    )
    
    # Required argument
    parser.add_argument(
        "-d", "--domain",
        required=True,
        help="Target domain (e.g., example.com)"
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--passive",
        action="store_true",
        help="Passive enumeration only"
    )
    mode_group.add_argument(
        "--all",
        action="store_true",
        help="Full reconnaissance (passive + brute + perms)"
    )
    
    # Bruteforce options
    parser.add_argument(
        "--brute",
        action="store_true",
        help="Enable bruteforce subdomain discovery"
    )
    parser.add_argument(
        "-w", "--wordlist",
        help="Custom wordlist for bruteforce"
    )
    
    # Permutation options
    parser.add_argument(
        "--perms",
        action="store_true",
        help="Enable permutation generation"
    )
    
    # DNS resolution options
    parser.add_argument(
        '--resolve-dns',
        action='store_true',
        help='Perform DNS resolution on discovered subdomains'
    )
    parser.add_argument(
        '--resolved-only',
        action='store_true',
        help='Show only subdomains that successfully resolve to IPs'
    )
    parser.add_argument(
        '--dns-timeout',
        type=float,
        default=2.0,
        help='DNS resolution timeout in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--max-resolve',
        type=int,
        default=0,
        help='Maximum number of subdomains to resolve (0 = all, default: 0)'
    )
    
    # Performance options
    parser.add_argument(
        "--threads",
        type=int,
        default=100,
        help="Number of concurrent threads (default: 100)"
    )
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML report"
    )
    output_group.add_argument(
        "--json",
        action="store_true",
        help="Generate JSON report"
    )
    output_group.add_argument(
        "--txt",
        action="store_true",
        help="Generate TXT report (simple subdomain list)"
    )
    output_group.add_argument(
        "--output",
        help="Output directory for reports"
    )
    
    # Verbose mode
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    # Filter argument
    parser.add_argument(
        '--filter', 
        dest='filter_level',
        choices=['none', 'light', 'normal', 'aggressive', 'intelligent'],
        default='normal',
        help='''Filtering level for results:
        none: No filtering
        light: Basic noise removal
        normal: Remove common noise (default)
        aggressive: Keep only potentially interesting targets
        intelligent: Smart sorting by priority'''
    )
    
    # Categorization option
    parser.add_argument(
        '--categorize',
        action='store_true',
        help='Show categorized results (API endpoints, admin panels, etc.)'
    )
    
    # Filter stats option
    parser.add_argument(
        '--filter-stats',
        action='store_true',
        help='Show filtering statistics'
    )
    
    return parser
