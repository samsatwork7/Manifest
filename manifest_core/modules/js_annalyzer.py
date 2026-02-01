import re
import math

SECRET_REGEX = [
    r"AIza[0-9A-Za-z\-_]{35}",  # Google API
    r"AKIA[0-9A-Z]{16}",        # AWS
    r"EAACEdEose0cBA[0-9A-Za-z]+", # Facebook
    r"sk_live_[0-9A-Za-z]+",    # Stripe live key
    r"sk_test_[0-9A-Za-z]+",    # Stripe test key
    r"ghp_[0-9A-Za-z]{36}",     # GitHub token
    r"shpat_[0-9A-Za-z]{32}",   # Shopify
]

class JSAnalyzer:

    def _entropy(self, s):
        """Shannon entropy"""
        prob = [float(s.count(c)) / len(s) for c in set(s)]
        return -sum([p * math.log(p, 2) for p in prob])

    def extract_secrets(self, text):
        found = set()

        # 1) Regex matches
        for rgx in SECRET_REGEX:
            for m in re.findall(rgx, text):
                found.add(m)

        # 2) High-entropy detection
        for token in re.findall(r"[0-9A-Za-z_\-=]{20,}", text):
            if self._entropy(token) > 4.0:
                found.add(token)

        return list(found)
