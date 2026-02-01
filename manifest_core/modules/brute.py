class BruteforceEngine:
    """Generates brute-force candidates"""

    def __init__(self, domain, wordlist):
        self.domain = domain
        self.wordlist = wordlist

    def generate(self):
        with open(self.wordlist, "r") as f:
            words = [w.strip() for w in f if w.strip()]

        return [f"{w}.{self.domain}" for w in words]
