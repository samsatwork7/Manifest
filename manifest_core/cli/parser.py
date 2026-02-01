import argparse

def build_parser():
    parser = argparse.ArgumentParser(
        prog="manifest",
        description="Manifest v1.0 — Next-Gen Reconnaissance Framework",
    )

    parser.add_argument("-d", "--domain", required=True, help="Target domain")

    parser.add_argument("--passive", action="store_true", help="Run passive enumeration")
    parser.add_argument("--brute", action="store_true", help="Run brute-force enumeration")
    parser.add_argument("--perms", action="store_true", help="Run permutation enumeration")

    parser.add_argument("--all", action="store_true", help="Run complete recon")

    parser.add_argument("-w", "--wordlist", default="wordlists/medium.txt")
    parser.add_argument("--threads", default=200, type=int)
    parser.add_argument("--timeout", default=3, type=int)

    parser.add_argument("--json", action="store_true")
    parser.add_argument("--txt", action="store_true")
    parser.add_argument("--html", action="store_true")

    parser.add_argument("--output", default="output")

    return parser
