# manifest_core/modules/brute.py
import asyncio
import aiohttp
from typing import List

class BruteforceEngine:
    """Simple bruteforce subdomain discovery"""
    
    def __init__(self, domain, wordlist=None):
        self.domain = domain
        self.wordlist = wordlist or self._default_wordlist()
        
    def _default_wordlist(self):
        """Default common subdomain wordlist"""
        return [
            'www', 'mail', 'ftp', 'admin', 'test', 'dev', 'staging',
            'api', 'secure', 'portal', 'web', 'app', 'mobile', 'blog',
            'shop', 'store', 'support', 'help', 'docs', 'wiki',
            'download', 'upload', 'files', 'cdn', 'static', 'assets',
            'media', 'img', 'images', 'video', 'audio', 'news', 'forum',
            'community', 'chat', 'status', 'monitor', 'analytics',
            'dashboard', 'control', 'manager', 'panel', 'login', 'auth',
            'sso', 'oauth', 'api-gateway', 'graphql', 'rest', 'soap',
            'vpn', 'ssh', 'rdp', 'jenkins', 'git', 'gitlab', 'github',
            'jira', 'confluence', 'bitbucket', 'docker', 'registry',
            'k8s', 'kubernetes', 'openshift', 'swarm', 'rancher',
            'prometheus', 'grafana', 'kibana', 'elastic', 'splunk'
        ]
    
    async def _check_subdomain(self, session, sub: str) -> bool:
        """Check if a subdomain resolves"""
        url = f"http://{sub}.{self.domain}"
        try:
            async with session.get(url, timeout=2, allow_redirects=False) as r:
                return r.status < 500  # Any non-server-error response
        except:
            try:
                # Try DNS resolution
                import socket
                socket.gethostbyname(f"{sub}.{self.domain}")
                return True
            except:
                return False
    
    async def run(self, threads=100) -> List[str]:
        """Run bruteforce discovery"""
        if not self.wordlist:
            return []
        
        found = []
        
        # Create subdomain list
        subdomains = [f"{word}.{self.domain}" for word in self.wordlist]
        
        # Limit to reasonable size
        if len(subdomains) > 500:
            subdomains = subdomains[:500]
        
        async with aiohttp.ClientSession() as session:
            # Run with concurrency limit
            semaphore = asyncio.Semaphore(min(threads, 50))
            
            async def check_with_semaphore(sub: str):
                async with semaphore:
                    if await self._check_subdomain(session, sub.split('.')[0]):
                        return sub
                return None
            
            tasks = [check_with_semaphore(sub) for sub in subdomains]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect valid results
            for result in results:
                if result and not isinstance(result, Exception):
                    found.append(result)
        
        return found
