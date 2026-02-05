import itertools
import re

class PermutationEngine:
    """
    Advanced permutation engine with 5x more variations
    Similar to DNSTwist but optimized for speed
    """
    
    # Expanded common prefixes/suffixes
    COMMON_PREFIXES = [
        "dev", "staging", "test", "stage", "pre", "old", "new", "v1", "v2", "v3",
        "api", "admin", "secure", "portal", "web", "app", "mobile", "beta", "alpha",
        "uat", "prod", "production", "demo", "sandbox", "backup", "archive", "legacy",
        "cdn", "static", "assets", "media", "img", "images", "video", "docs", "wiki",
        "mail", "smtp", "imap", "pop", "ftp", "sftp", "vpn", "ssh", "git", "svn",
        "jenkins", "jira", "confluence", "grafana", "kibana", "prometheus"
    ]
    
    COMMON_SUFFIXES = [
        "-dev", "-test", "-stage", "-prod", "-uat", "-demo", "-beta", "-alpha",
        "-old", "-new", "-backup", "-temp", "-archive", "-legacy", "-v1", "-v2",
        "-admin", "-api", "-web", "-app", "-mobile", "-secure", "-portal"
    ]
    
    # Common TLD alternatives
    TLD_ALTERNATIVES = {
        ".com": [".net", ".org", ".co", ".io", ".ai", ".dev", ".app", ".xyz"],
        ".net": [".com", ".org", ".io", ".co"],
        ".org": [".com", ".net", ".io"],
        ".io": [".com", ".dev", ".app"],
        ".co": [".com", ".io", ".uk"],
        ".uk": [".com", ".co.uk", ".org.uk"]
    }
    
    # Character substitution map for typos
    CHAR_SUBSTITUTIONS = {
        'a': ['@', '4'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7'],
        'b': ['8'],
        'g': ['9'],
        'l': ['1', '|'],
        'z': ['2']
    }
    
    # Common number patterns
    NUMBER_PATTERNS = ['', '1', '2', '3', '10', '11', '12', '20', '21', '22', 
                      '01', '02', '03', '001', '002', '201', '202', '2023', '2024']
    
    def __init__(self):
        self.generated = set()
    
    def generate(self, subdomains, depth=1):
        """
        Generate permutations from discovered subdomains
        depth: 1=basic, 2=advanced, 3=exhaustive
        """
        final = set()
        
        for sd in subdomains:
            parts = sd.split('.')
            if len(parts) < 2:
                continue
            
            base = parts[0]
            tld = '.' + '.'.join(parts[1:])
            
            # Add original
            final.add(sd)
            
            # 1. Prefix variations
            for prefix in self.COMMON_PREFIXES[:10*depth]:
                # Prefix with dot
                final.add(f"{prefix}.{sd}")
                # Prefix with hyphen
                final.add(f"{prefix}-{base}{tld}")
                # Prefix without separator
                final.add(f"{prefix}{base}{tld}")
            
            # 2. Suffix variations
            for suffix in self.COMMON_SUFFIXES[:5*depth]:
                final.add(f"{base}{suffix}{tld}")
            
            # 3. TLD variations
            if tld in self.TLD_ALTERNATIVES and depth >= 2:
                for alt_tld in self.TLD_ALTERNATIVES[tld]:
                    final.add(f"{base}{alt_tld}")
                    # With common prefixes
                    for prefix in self.COMMON_PREFIXES[:3]:
                        final.add(f"{prefix}.{base}{alt_tld}")
            
            # 4. Number variations
            if depth >= 2:
                for num in self.NUMBER_PATTERNS[:8*depth]:
                    # Prefix numbers
                    final.add(f"{num}{base}{tld}")
                    # Suffix numbers
                    final.add(f"{base}{num}{tld}")
                    # Hyphen numbers
                    final.add(f"{base}-{num}{tld}")
            
            # 5. Character substitution (typo-squatting)
            if depth >= 3 and len(base) <= 15:
                self._add_char_variations(final, base, tld)
            
            # 6. Hyphenation variations
            if len(base) > 4 and depth >= 2:
                self._add_hyphen_variations(final, base, tld)
            
            # 7. Duplicate/omit characters
            if depth >= 3:
                self._add_duplicate_variations(final, base, tld)
        
        return list(final)
    
    def _add_char_variations(self, final_set, base, tld):
        """Add character substitution variations"""
        # Single character substitutions
        for i, char in enumerate(base.lower()):
            if char in self.CHAR_SUBSTITUTIONS:
                for sub in self.CHAR_SUBSTITUTIONS[char]:
                    new_base = base[:i] + sub + base[i+1:]
                    final_set.add(f"{new_base}{tld}")
    
    def _add_hyphen_variations(self, final_set, base, tld):
        """Add hyphen insertion variations"""
        # Insert hyphens at natural break points
        for i in range(1, len(base)):
            if base[i].isalpha() and base[i-1].isalpha():
                # Only insert if it creates readable parts
                final_set.add(f"{base[:i]}-{base[i:]}{tld}")
    
    def _add_duplicate_variations(self, final_set, base, tld):
        """Add duplicate/omit character variations"""
        # Duplicate letters (common typos)
        for i in range(len(base)-1):
            if base[i] == base[i+1]:
                # Remove duplicate
                final_set.add(f"{base[:i] + base[i+1:]}{tld}")
            else:
                # Add duplicate
                final_set.add(f"{base[:i+1] + base[i] + base[i+1:]}{tld}")
    
    def generate_from_domain(self, domain, count=1000):
        """
        Generate permutations directly from a domain name
        Useful when no subdomains are discovered yet
        """
        base = domain.split('.')[0]
        tld = '.' + '.'.join(domain.split('.')[1:])
        
        permutations = set()
        
        # Basic permutations
        for prefix in self.COMMON_PREFIXES[:20]:
            permutations.add(f"{prefix}.{domain}")
            permutations.add(f"{prefix}-{base}{tld}")
        
        for suffix in self.COMMON_SUFFIXES[:10]:
            permutations.add(f"{base}{suffix}{tld}")
        
        for num in ['', '1', '2', '01', '02', '2024']:
            permutations.add(f"{base}{num}{tld}")
            permutations.add(f"{num}{base}{tld}")
        
        # Ensure we have exactly 'count' permutations
        result = list(permutations)
        if len(result) > count:
            return result[:count]
        
        # If we need more, add more variations
        while len(result) < count and len(self.COMMON_PREFIXES) > 0:
            for prefix in self.COMMON_PREFIXES[20:40]:
                result.append(f"{prefix}.{domain}")
                if len(result) >= count:
                    break
        
        return result[:count]
