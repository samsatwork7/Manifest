#!/usr/bin/env python3

import asyncio
from .main import main
from manifest_core.cli.parser import build_parser
from manifest_core.cli.banner import print_banner
from manifest_core.cli.runner import ManifestRunner

def main():
    parser = build_parser()
    args = parser.parse_args()

    print_banner()

    runner = ManifestRunner(args)
    results = asyncio.run(runner.run())

    print("\n[bold green]✔ Recon completed![/bold green]")

if __name__ == "__main__":
    main()
