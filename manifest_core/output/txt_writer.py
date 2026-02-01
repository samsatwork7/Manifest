class TXTWriter:

    @staticmethod
    def write(filepath, subdomains):
        with open(filepath, "w") as f:
            for s in subdomains:
                f.write(s["subdomain"] + "\n")
