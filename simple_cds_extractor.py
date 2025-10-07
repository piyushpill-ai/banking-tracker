#!/usr/bin/env python3
"""
Simple extractor to get bank API data sources from CDS product comparator demo
Uses requests only to avoid Selenium issues
"""

import requests
import json
import re
import time
from urllib.parse import urljoin, urlparse

class SimpleCDSExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.data_sources = []
        
    def extract_from_demo_page(self):
        """Extract data sources from the CDS demo page"""
        print("🔍 Fetching CDS product comparator demo page...")
        
        try:
            demo_url = "https://consumerdatastandardsaustralia.github.io/product-comparator-demo/"
            response = self.session.get(demo_url, timeout=30)
            response.raise_for_status()
            
            print(f"✅ Fetched demo page ({len(response.text)} characters)")
            
            # Extract from HTML source
            self.extract_from_html(response.text)
            
            # Look for JSON files that might contain data sources
            self.find_data_files(response.text, demo_url)
            
        except Exception as e:
            print(f"❌ Error fetching demo page: {e}")
            
        return self.data_sources
    
    def extract_from_html(self, html_content):
        """Extract API endpoints from HTML content"""
        print("📝 Analyzing HTML content...")
        
        # Look for various patterns that might contain API endpoints
        patterns = [
            # API endpoints in various forms
            r'https?://[^\s<>"\']+api[^\s<>"\']*products[^\s<>"\']*',
            r'https?://[^\s<>"\']+cds-au[^\s<>"\']*products[^\s<>"\']*',
            r'https?://[^\s<>"\']+banking[^\s<>"\']*products[^\s<>"\']*',
            
            # Base URLs that we can construct endpoints from
            r'https?://api\.[^\s<>"\']+',
            r'https?://[^\s<>"\']*\.api\.[^\s<>"\']+',
            r'https?://public\.[^\s<>"\']+',
            r'https?://open\.[^\s<>"\']+',
            r'https?://digital\.[^\s<>"\']+',
            
            # Specific bank domains
            r'https?://[^\s<>"\']*commbank[^\s<>"\']*',
            r'https?://[^\s<>"\']*westpac[^\s<>"\']*',
            r'https?://[^\s<>"\']*anz[^\s<>"\']*',
            r'https?://[^\s<>"\']*nab[^\s<>"\']*',
        ]
        
        found_urls = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                # Clean up the match
                url = match.strip('",\'();')
                if self.is_potential_api_url(url):
                    found_urls.add(url)
        
        print(f"🔗 Found {len(found_urls)} potential API URLs")
        
        # Process found URLs
        for url in found_urls:
            endpoint = self.process_url(url)
            if endpoint:
                bank_name = self.extract_bank_name(url)
                self.data_sources.append({
                    'bank_name': bank_name,
                    'endpoint': endpoint,
                    'original_url': url,
                    'source': 'html_extraction'
                })
                print(f"  🏦 {bank_name}: {endpoint}")
    
    def find_data_files(self, html_content, base_url):
        """Look for data files that might contain bank information"""
        print("📂 Looking for data files...")
        
        # Look for JavaScript files that might contain data
        js_patterns = [
            r'src=["\']([^"\']*\.js)["\']',
            r'href=["\']([^"\']*\.js)["\']',
        ]
        
        json_patterns = [
            r'["\']([^"\']*\.json)["\']',
            r'fetch\(["\']([^"\']*\.json)["\']',
        ]
        
        all_patterns = js_patterns + json_patterns
        
        for pattern in all_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                file_url = urljoin(base_url, match)
                print(f"📄 Found potential data file: {file_url}")
                self.fetch_and_analyze_file(file_url)
    
    def fetch_and_analyze_file(self, file_url):
        """Fetch and analyze a data file for API endpoints"""
        try:
            response = self.session.get(file_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Look for API endpoints in the file content
                if 'api' in content.lower() and ('products' in content.lower() or 'banking' in content.lower()):
                    print(f"  📋 Analyzing {file_url}...")
                    self.extract_from_file_content(content, file_url)
                    
        except Exception as e:
            print(f"  ⚠️ Could not fetch {file_url}: {e}")
    
    def extract_from_file_content(self, content, source_url):
        """Extract API endpoints from file content"""
        # Try to parse as JSON first
        try:
            data = json.loads(content)
            self.extract_from_json(data, source_url)
        except:
            # If not JSON, treat as text
            self.extract_from_text(content, source_url)
    
    def extract_from_json(self, data, source_url):
        """Extract endpoints from JSON data"""
        def search_json(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and self.is_potential_api_url(value):
                        endpoint = self.process_url(value)
                        if endpoint:
                            bank_name = self.extract_bank_name(value) or key
                            self.data_sources.append({
                                'bank_name': bank_name,
                                'endpoint': endpoint,
                                'source': f'json_data:{source_url}',
                                'json_path': f"{path}.{key}" if path else key
                            })
                            print(f"  🎯 JSON: {bank_name} -> {endpoint}")
                    else:
                        search_json(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    search_json(item, f"{path}[{i}]" if path else f"[{i}]")
        
        search_json(data)
    
    def extract_from_text(self, content, source_url):
        """Extract endpoints from text content"""
        # Use same patterns as HTML extraction
        patterns = [
            r'https?://[^\s<>"\']+api[^\s<>"\']*products[^\s<>"\']*',
            r'https?://[^\s<>"\']+cds-au[^\s<>"\']*products[^\s<>"\']*',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                url = match.strip('",\'();')
                endpoint = self.process_url(url)
                if endpoint:
                    bank_name = self.extract_bank_name(url)
                    self.data_sources.append({
                        'bank_name': bank_name,
                        'endpoint': endpoint,
                        'source': f'text_data:{source_url}'
                    })
                    print(f"  📝 Text: {bank_name} -> {endpoint}")
    
    def is_potential_api_url(self, url):
        """Check if URL could be a bank API endpoint"""
        if not url or len(url) < 10:
            return False
            
        if not url.startswith(('http://', 'https://')):
            return False
            
        url_lower = url.lower()
        
        # Must contain API-related terms
        api_terms = ['api', 'cds-au', 'banking', 'public', 'open', 'digital']
        if not any(term in url_lower for term in api_terms):
            return False
            
        # Exclude common non-API URLs
        exclude_terms = ['javascript', 'css', 'image', 'font', 'analytics', 'google', 'facebook']
        if any(term in url_lower for term in exclude_terms):
            return False
            
        return True
    
    def process_url(self, url):
        """Process URL to create a proper API endpoint"""
        if not url:
            return None
            
        # If it already looks like a products endpoint, use it
        if 'products' in url.lower():
            return url
            
        # Try to construct a products endpoint
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Try common endpoint patterns
        endpoint_patterns = [
            f"{base_url}/cds-au/v1/banking/products",
            f"{base_url}/api/cds-au/v1/banking/products",
            f"{base_url}/public/cds-au/v1/banking/products",
            f"{base_url}/open/cds-au/v1/banking/products",
        ]
        
        # Return the first pattern
        return endpoint_patterns[0]
    
    def extract_bank_name(self, url):
        """Extract bank name from URL"""
        if not url:
            return "Unknown Bank"
            
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Bank name mappings
        bank_mappings = {
            'commbank': 'Commonwealth Bank',
            'cba': 'Commonwealth Bank',
            'westpac': 'Westpac',
            'anz': 'ANZ',
            'nab': 'NAB',
            'bendigo': 'Bendigo Bank',
            'boq': 'Bank of Queensland',
            'suncorp': 'Suncorp Bank',
            'adelaide': 'Adelaide Bank',
            'ing': 'ING Australia',
            'macquarie': 'Macquarie Bank',
            '86400': 'UBank',
            'ubank': 'UBank',
            'heritage': 'Heritage Bank',
            'imb': 'IMB Bank',
            'greater': 'Greater Bank',
            'newcastle': 'Newcastle Permanent',
            'teachers': 'Teachers Mutual Bank',
        }
        
        for key, name in bank_mappings.items():
            if key in domain:
                return name
                
        # Extract from domain
        domain_parts = domain.split('.')
        if len(domain_parts) > 1:
            return domain_parts[0].replace('-', ' ').title() + ' Bank'
            
        return "Unknown Bank"
    
    def save_results(self):
        """Save extracted data sources"""
        if not self.data_sources:
            print("❌ No data sources found")
            return
            
        # Remove duplicates
        unique_sources = []
        seen_endpoints = set()
        
        for source in self.data_sources:
            endpoint = source.get('endpoint', '')
            if endpoint and endpoint not in seen_endpoints:
                unique_sources.append(source)
                seen_endpoints.add(endpoint)
        
        timestamp = int(time.time())
        
        # Save as JSON
        json_file = f"extracted_bank_apis_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(unique_sources, f, indent=2)
        
        # Save as Python code for easy integration
        py_file = f"extracted_bank_list_{timestamp}.py"
        with open(py_file, 'w') as f:
            f.write("# Bank API endpoints extracted from CDS product comparator demo\n")
            f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("EXTRACTED_BANKS = [\n")
            
            for i, source in enumerate(unique_sources):
                bank_name = source.get('bank_name', f'Bank{i+1}')
                endpoint = source.get('endpoint', '')
                brand_id = f"extracted-{i+1:03d}"
                
                f.write(f'    ("{bank_name}", "{brand_id}", "{endpoint}"),\n')
            
            f.write("]\n\n")
            f.write("# Additional metadata\n")
            f.write("EXTRACTION_METADATA = {\n")
            f.write(f"    'total_banks': {len(unique_sources)},\n")
            f.write(f"    'extraction_date': '{time.strftime('%Y-%m-%d %H:%M:%S')}',\n")
            f.write("    'sources': [\n")
            
            sources_summary = {}
            for source in unique_sources:
                source_type = source.get('source', 'unknown')
                sources_summary[source_type] = sources_summary.get(source_type, 0) + 1
            
            for source_type, count in sources_summary.items():
                f.write(f"        ('{source_type}', {count}),\n")
            
            f.write("    ]\n")
            f.write("}\n")
        
        print(f"\n💾 Results saved:")
        print(f"   📄 JSON: {json_file}")
        print(f"   🐍 Python: {py_file}")
        print(f"\n📊 Summary:")
        print(f"   🏦 Total unique banks: {len(unique_sources)}")
        
        # Show first few results
        print(f"\n🎯 Sample results:")
        for source in unique_sources[:5]:
            bank_name = source.get('bank_name', 'Unknown')
            endpoint = source.get('endpoint', '')
            print(f"   {bank_name}: {endpoint}")
        
        if len(unique_sources) > 5:
            print(f"   ... and {len(unique_sources) - 5} more")
            
        return unique_sources

def main():
    """Main execution"""
    print("🚀 CDS Bank API Extractor")
    print("=" * 50)
    
    extractor = SimpleCDSExtractor()
    
    try:
        # Extract from demo page
        data_sources = extractor.extract_from_demo_page()
        
        # Save results
        if data_sources:
            unique_sources = extractor.save_results()
            print(f"\n✅ Successfully extracted {len(unique_sources)} bank API endpoints!")
        else:
            print("\n❌ No bank API endpoints found")
            print("💡 The demo page structure might have changed or uses dynamic loading")
            
    except Exception as e:
        print(f"❌ Error during extraction: {e}")

if __name__ == "__main__":
    main()


