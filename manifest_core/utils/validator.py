import re

class DomainValidator:
    """Validates domain formats"""

    DOMAIN_REGEX = re.compile(
        r"^(?!\-)(?:[a-zA-Z0-9\-]{0,62}[a-zA-Z0-9]\.)+[a-zA-Z]{2,}$"
    )

    @staticmethod
    def is_valid(domain: str) -> bool:
        return bool(DomainValidator.DOMAIN_REGEX.match(domain))
