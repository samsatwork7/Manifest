import json
from datetime import datetime

class JSONWriter:
    
    @staticmethod
    def write_enhanced(filepath, data):
        """
        Write enhanced JSON report with metadata and statistics
        """
        enhanced_data = {
            'metadata': {
                'tool': 'Manifest v2.0',
                'domain': data.get('domain', ''),
                'scan_date': datetime.now().isoformat(),
                'duration': data.get('duration', 0),
                'options': data.get('options', {})
            },
            'statistics': {
                'total_subdomains': len(data.get('subdomains', [])),
                'live_subdomains': len(data.get('live', [])),
                'wildcard_filtered': data.get('wildcard_filtered', 0),
                'takeover_candidates': len(data.get('takeovers', [])),
                'unique_ips': len(set(
                    ip for sub in data.get('live_details', []) 
                    for ip in sub.get('ipv4', []) + sub.get('ipv6', [])
                )) if data.get('live_details') else 0
            },
            'subdomains': {
                'all': data.get('subdomains', []),
                'live': data.get('live', []),
                'detailed': data.get('live_details', []),
                'by_source': data.get('sources', {})
            },
            'takeovers': data.get('takeovers', []),
            'wildcards': data.get('wildcards', []),
            'dns_records': data.get('dns_records', {}),
            'permutations': data.get('permutations', [])
        }
        
        with open(filepath, 'w') as f:
            json.dump(enhanced_data, f, indent=2, default=str)
        
        return filepath
    
    @staticmethod
    def write_simple(filepath, subdomains):
        """
        Write simple list of subdomains
        """
        with open(filepath, 'w') as f:
            json.dump(subdomains, f, indent=2)
    
    @staticmethod
    def write_for_other_tools(filepath, data, format_type='amass'):
        """
        Write output compatible with other tools
        Formats: 'amass', 'subfinder', 'assetfinder', 'plain'
        """
        if format_type == 'amass':
            # Amass JSON format
            output = []
            for sub in data.get('subdomains', []):
                output.append({
                    'name': sub,
                    'domain': data.get('domain', ''),
                    'timestamp': datetime.now().isoformat()
                })
        elif format_type == 'subfinder':
            # Subfinder format (simple JSON array)
            output = data.get('subdomains', [])
        elif format_type == 'assetfinder':
            # Assetfinder format (plain text, one per line)
            with open(filepath, 'w') as f:
                for sub in data.get('subdomains', []):
                    f.write(sub + '\n')
            return filepath
        else:  # plain
            output = data.get('subdomains', [])
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        
        return filepath
