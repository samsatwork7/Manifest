class Deduplicator:
    """Merges and deduplicates DNS results"""

    @staticmethod
    def dedupe(results):
        final = {}
        for r in results:
            sd = r["subdomain"]
            if sd not in final:
                final[sd] = {"subdomain": sd, "ipv4": set(), "ipv6": set()}

            final[sd]["ipv4"].update(r.get("ipv4", []))
            final[sd]["ipv6"].update(r.get("ipv6", []))

        # Convert sets → lists
        return [
            {
                "subdomain": sd,
                "ipv4": list(v["ipv4"]),
                "ipv6": list(v["ipv6"])
            }
            for sd, v in final.items()
        ]
