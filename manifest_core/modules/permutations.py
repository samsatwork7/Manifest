class PermutationEngine:
    """
    Simple but powerful permutation engine
    """

    COMMON = ["dev", "staging", "test", "stage", "pre", "old", "new", "v1", "v2"]

    def generate(self, subdomains):
        final = set()

        for sd in subdomains:
            base = sd.split(".")[0]

            for p in self.COMMON:
                final.add(f"{base}-{p}")
                final.add(f"{p}-{base}")
                final.add(f"{base}{p}")
                final.add(f"{p}{base}")

        return final
