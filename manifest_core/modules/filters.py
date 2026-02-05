import re
from urllib.parse import urlparse

class SmartFilter:
    """
    Intelligent filtering system to remove noise and prioritize interesting targets
    """
    
    # Patterns for common uninteresting subdomains
    NOISE_PATTERNS = [
        r'autodiscover\..*',
        r'autoconfig\..*',
        r'.*\.pkg\..*',
        r'.*\.cdn\..*',
        r'.*\.edge\..*',
        r'.*\.akamai\..*',
        r'.*\.cloudfront\..*',
        r'.*\.akamaiedge\..*',
        r'.*\.safedns\..*',
        r'.*\.domaincontrol\..*',
        r'.*\.whoisguard\..*',
        r'ns[0-9]+\..*',
        r'mail\..*',
        r'smtp\..*',
        r'pop\..*',
        r'imap\..*',
        r'ftp\..*',
        r'cpanel\..*',
        r'webmail\..*',
        r'whm\..*',
        r'webdisk\..*',
        r'.*\.compute\..*',
        r'.*\.internal\..*',
        r'.*\.local\..*',
        r'.*\.prod\..*\.internal',
        r'.*\.staging\..*\.internal',
        r'\.prod\.',
        r'\.stg\.',
        r'\.dev\.',
        r'\.uat\.',
        r'\.test\.',
        r'localhost.*',
        r'^localhost$',
        r'^broadcasthost$',
        r'^ip6\-.*',
        r'^fe80\:.*',
        r'^::1$',
        r'^0\.0\.0\.0$',
        r'.*\.arpa$',
        r'.*\.in-addr\.arpa$'
    ]
    
    # Keywords that make subdomains INTERESTING
    INTERESTING_KEYWORDS = [
        'api', 'admin', 'dashboard', 'portal', 'backup', 'dev', 'staging', 'test',
        'secure', 'vpn', 'jenkins', 'git', 'confluence', 'jira', 'wiki', 'sharepoint',
        'exchange', 'owa', 'aws', 'azure', 'gcp', 'cloud', 'console', 'manager',
        'control', 'monitor', 'log', 'analytics', 'grafana', 'kibana', 'prometheus',
        'elastic', 'splunk', 'sonar', 'nexus', 'artifactory', 'registry', 'docker',
        'kubernetes', 'k8s', 'openshift', 'swarm', 'mesos', 'rancher', 'traefik',
        'nginx', 'apache', 'iis', 'tomcat', 'jboss', 'weblogic', 'websphere',
        'wordpress', 'joomla', 'drupal', 'magento', 'shopify', 'woocommerce',
        'database', 'sql', 'mysql', 'postgres', 'mongodb', 'redis', 'elasticsearch',
        'cassandra', 'oracle', 'db', 'data', 'storage', 'bucket', 's3', 'blob',
        'file', 'share', 'nas', 'san', 'backup', 'archive', 'restore', 'recovery'
    ]
    
    # High priority keywords (critical targets)
    HIGH_PRIORITY_KEYWORDS = [
        'admin', 'dashboard', 'api', 'vpn', 'jenkins', 'git', 'confluence', 'jira',
        'exchange', 'owa', 'aws', 'azure', 'console', 'grafana', 'kibana'
    ]
    
    def __init__(self, domain):
        self.domain = domain
        self.noise_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.NOISE_PATTERNS]
        self.interesting_regex = [re.compile(rf'\b{kw}\b', re.IGNORECASE) for kw in self.INTERESTING_KEYWORDS]
        self.high_priority_regex = [re.compile(rf'\b{kw}\b', re.IGNORECASE) for kw in self.HIGH_PRIORITY_KEYWORDS]
    
    def filter_subdomains(self, subdomains, filter_level='normal'):
        """
        Filter subdomains based on selected level
        Levels: 'none', 'light', 'normal', 'aggressive', 'intelligent'
        """
        if filter_level == 'none':
            return subdomains
        
        filtered = []
        
        for sub in subdomains:
            if not isinstance(sub, str):
                continue
            
            sub_lower = sub.lower()
            
            # Skip if matches noise patterns
            is_noise = False
            for pattern in self.noise_regex:
                if pattern.match(sub_lower):
                    is_noise = True
                    break
            
            if is_noise:
                continue
            
            # Apply filtering based on level
            if filter_level == 'light':
                filtered.append(sub)
            elif filter_level == 'normal':
                if self._is_normal_filter_pass(sub_lower):
                    filtered.append(sub)
            elif filter_level == 'aggressive':
                if self._is_aggressive_filter_pass(sub_lower):
                    filtered.append(sub)
            elif filter_level == 'intelligent':
                filtered.append({
                    'subdomain': sub,
                    'priority': self._calculate_priority(sub_lower),
                    'interesting': self._is_interesting(sub_lower)
                })
        
        if filter_level == 'intelligent':
            # Sort by priority
            filtered.sort(key=lambda x: x['priority'], reverse=True)
            return [item['subdomain'] for item in filtered]
        
        return filtered
    
    def _is_normal_filter_pass(self, subdomain):
        """Normal filtering: remove obvious noise"""
        # Skip very long subdomains (likely garbage)
        if len(subdomain) > 100:
            return False
        
        # Skip if has consecutive special chars
        if re.search(r'[\.\-_]{3,}', subdomain):
            return False
        
        # Skip if looks like an IP address
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', subdomain.split('.')[0]):
            return False
        
        return True
    
    def _is_aggressive_filter_pass(self, subdomain):
        """Aggressive filtering: only keep potentially interesting targets"""
        # Must pass normal filter first
        if not self._is_normal_filter_pass(subdomain):
            return False
        
        # Check if contains interesting keywords
        for pattern in self.interesting_regex:
            if pattern.search(subdomain):
                return True
        
        # Check if it's a short, meaningful name
        base = subdomain.split('.')[0]
        if len(base) <= 8 and base.isalpha() and len(base) >= 3:
            return True
        
        return False
    
    def _is_interesting(self, subdomain):
        """Check if subdomain contains interesting keywords"""
        for pattern in self.interesting_regex:
            if pattern.search(subdomain):
                return True
        return False
    
    def _calculate_priority(self, subdomain):
        """Calculate priority score for intelligent sorting"""
        score = 0
        
        # High priority keywords
        for pattern in self.high_priority_regex:
            if pattern.search(subdomain):
                score += 10
        
        # Interesting keywords
        for pattern in self.interesting_regex:
            if pattern.search(subdomain):
                score += 5
        
        # Length factor (shorter = higher priority)
        base_len = len(subdomain.split('.')[0])
        if base_len <= 5:
            score += 3
        elif base_len <= 10:
            score += 1
        
        # Number factor (subdomains with numbers are often test/staging)
        if re.search(r'\d', subdomain):
            score -= 2
        
        return score
    
    def categorize_subdomains(self, subdomains):
        """Categorize subdomains by type"""
        categories = {
            'api_endpoints': [],
            'admin_panels': [],
            'infrastructure': [],
            'development': [],
            'mail_servers': [],
            'cdn_assets': [],
            'other': []
        }
        
        for sub in subdomains:
            sub_lower = sub.lower()
            
            # API endpoints
            if any(kw in sub_lower for kw in ['api', 'rest', 'graphql', 'soap', 'json', 'xml']):
                categories['api_endpoints'].append(sub)
            
            # Admin panels
            elif any(kw in sub_lower for kw in ['admin', 'dashboard', 'panel', 'control', 'manager']):
                categories['admin_panels'].append(sub)
            
            # Infrastructure
            elif any(kw in sub_lower for kw in ['vpn', 'ssh', 'ftp', 'sftp', 'vnc', 'rdp', 'jenkins', 
                                              'gitlab', 'github', 'bitbucket', 'jira', 'confluence']):
                categories['infrastructure'].append(sub)
            
            # Development
            elif any(kw in sub_lower for kw in ['dev', 'staging', 'test', 'stage', 'qa', 'uat', 'beta']):
                categories['development'].append(sub)
            
            # Mail servers
            elif any(kw in sub_lower for kw in ['mail', 'smtp', 'imap', 'pop', 'exchange', 'owa']):
                categories['mail_servers'].append(sub)
            
            # CDN/Assets
            elif any(kw in sub_lower for kw in ['cdn', 'static', 'assets', 'media', 'img', 'images', 'js', 'css']):
                categories['cdn_assets'].append(sub)
            
            else:
                categories['other'].append(sub)
        
        return categories
