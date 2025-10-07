#!/usr/bin/env python3
"""
Extract all bank API data sources from Consumer Data Standards Australia product comparator demo
This will give us a comprehensive list of all available bank APIs for our Luke Prior replica
"""

import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

class CDSDataSourceExtractor:
    def __init__(self):
        self.setup_driver()
        self.data_sources = []
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def extract_data_sources_from_demo(self):
        """Extract all data sources from the CDS product comparator demo"""
        print("🔍 Extracting data sources from CDS product comparator demo...")
        
        try:
            # Load the demo page
            demo_url = "https://consumerdatastandardsaustralia.github.io/product-comparator-demo/"
            self.driver.get(demo_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
            # Look for data sources section
            print("📋 Looking for Data Sources section...")
            
            # Try to find elements that contain data source information
            # The demo page might store this in JavaScript variables or in the DOM
            
            # Check for JavaScript variables containing data sources
            script_elements = self.driver.find_elements(By.TAG_NAME, "script")
            
            for script in script_elements:
                script_content = script.get_attribute("innerHTML")
                if script_content and "dataSources" in script_content:
                    print("📜 Found dataSources in JavaScript!")
                    self.extract_from_javascript(script_content)
                    
                if script_content and "endpoints" in script_content.lower():
                    print("📜 Found endpoints in JavaScript!")
                    self.extract_endpoints_from_javascript(script_content)
                    
                if script_content and "api" in script_content.lower() and "products" in script_content.lower():
                    print("📜 Found API products references!")
                    self.extract_api_references(script_content)
            
            # Also check the DOM for data source listings
            self.extract_from_dom()
            
            # Check network requests made by the page
            self.analyze_network_requests()
            
        except Exception as e:
            print(f"❌ Error extracting data sources: {e}")
            
        return self.data_sources
    
    def extract_from_javascript(self, script_content):
        """Extract data sources from JavaScript content"""
        try:
            # Look for various patterns that might contain API endpoints
            patterns = [
                r'"([^"]*api[^"]*products[^"]*)"',  # API endpoints with "products"
                r"'([^']*api[^']*products[^']*)'",   # Single quoted API endpoints
                r'baseUrl:\s*["\']([^"\']+)["\']',   # baseUrl definitions
                r'endpoint:\s*["\']([^"\']+)["\']',  # endpoint definitions
                r'url:\s*["\']([^"\']+)["\']',       # url definitions
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                for match in matches:
                    if self.is_valid_api_endpoint(match):
                        print(f"✅ Found API endpoint: {match}")
                        self.data_sources.append({
                            'endpoint': match,
                            'source': 'javascript_extraction'
                        })
                        
        except Exception as e:
            print(f"⚠️ Error parsing JavaScript: {e}")
    
    def extract_endpoints_from_javascript(self, script_content):
        """Extract specific endpoint configurations"""
        try:
            # Look for bank configurations
            bank_patterns = [
                r'(\w+):\s*{\s*[^}]*endpoint[^}]*}',  # Bank objects with endpoints
                r'["\'](\w+)["\']:\s*["\']([^"\']*api[^"\']*)["\']',  # Key-value pairs
            ]
            
            for pattern in bank_patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple) and len(match) == 2:
                        bank_name, endpoint = match
                        if self.is_valid_api_endpoint(endpoint):
                            print(f"🏦 Found {bank_name}: {endpoint}")
                            self.data_sources.append({
                                'bank_name': bank_name,
                                'endpoint': endpoint,
                                'source': 'bank_configuration'
                            })
                            
        except Exception as e:
            print(f"⚠️ Error parsing bank endpoints: {e}")
    
    def extract_api_references(self, script_content):
        """Extract API references and construct endpoints"""
        try:
            # Look for domain references that could be API bases
            domain_patterns = [
                r'https?://([^/]+\.(?:com\.au|com|net\.au|org\.au))[^"\'\s]*',
                r'["\']([^"\']*\.(?:com\.au|com))["\']',
            ]
            
            for pattern in domain_patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                for match in matches:
                    if self.looks_like_bank_domain(match):
                        # Try to construct API endpoint
                        api_endpoint = self.construct_api_endpoint(match)
                        if api_endpoint:
                            print(f"🔗 Constructed endpoint: {api_endpoint}")
                            self.data_sources.append({
                                'endpoint': api_endpoint,
                                'domain': match,
                                'source': 'domain_construction'
                            })
                            
        except Exception as e:
            print(f"⚠️ Error extracting API references: {e}")
    
    def extract_from_dom(self):
        """Extract data sources from DOM elements"""
        try:
            # Look for lists, tables, or other elements that might contain data sources
            elements_to_check = [
                "//div[contains(text(), 'Data Source')]",
                "//li[contains(text(), 'api')]",
                "//td[contains(text(), 'api')]",
                "//span[contains(text(), 'endpoint')]",
                "//pre[contains(text(), 'api')]",
            ]
            
            for xpath in elements_to_check:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        text = element.get_attribute("textContent") or element.text
                        if text:
                            self.extract_urls_from_text(text)
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error extracting from DOM: {e}")
    
    def analyze_network_requests(self):
        """Analyze network requests to find API calls"""
        try:
            # Get browser logs to see network requests
            logs = self.driver.get_log('performance')
            
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    url = message['message']['params']['response']['url']
                    if 'api' in url.lower() and 'products' in url.lower():
                        print(f"🌐 Found network request: {url}")
                        self.data_sources.append({
                            'endpoint': url,
                            'source': 'network_analysis'
                        })
                        
        except Exception as e:
            print(f"⚠️ Error analyzing network requests: {e}")
    
    def is_valid_api_endpoint(self, url):
        """Check if URL looks like a valid API endpoint"""
        if not url or len(url) < 10:
            return False
            
        # Must contain these keywords
        required_keywords = ['api', 'products']
        if not all(keyword in url.lower() for keyword in required_keywords):
            return False
            
        # Must be HTTP(S)
        if not url.startswith(('http://', 'https://')):
            return False
            
        # Should contain banking-related terms
        banking_terms = ['banking', 'cds-au', 'cdr']
        if not any(term in url.lower() for term in banking_terms):
            return False
            
        return True
    
    def looks_like_bank_domain(self, domain):
        """Check if domain looks like it belongs to a bank"""
        if not domain:
            return False
            
        banking_keywords = [
            'bank', 'banking', 'financial', 'credit', 'loan', 'mortgage',
            'anz', 'nab', 'westpac', 'commbank', 'cba', 'suncorp',
            'bendigo', 'adelaide', 'heritage', 'boq', 'ing', 'macquarie'
        ]
        
        domain_lower = domain.lower()
        return any(keyword in domain_lower for keyword in banking_keywords)
    
    def construct_api_endpoint(self, domain):
        """Construct API endpoint from domain"""
        if not domain.startswith(('http://', 'https://')):
            domain = f"https://{domain}"
            
        # Try common API patterns
        patterns = [
            f"{domain}/cds-au/v1/banking/products",
            f"{domain}/api/cds-au/v1/banking/products",
            f"{domain}/public/cds-au/v1/banking/products",
            f"{domain}/open/cds-au/v1/banking/products",
        ]
        
        # Return the first pattern for now
        return patterns[0] if patterns else None
    
    def extract_urls_from_text(self, text):
        """Extract URLs from text content"""
        url_pattern = r'https?://[^\s<>"\']+api[^\s<>"\']*products[^\s<>"\']*'
        matches = re.findall(url_pattern, text, re.IGNORECASE)
        
        for match in matches:
            if self.is_valid_api_endpoint(match):
                print(f"📝 Extracted from text: {match}")
                self.data_sources.append({
                    'endpoint': match,
                    'source': 'text_extraction'
                })
    
    def save_data_sources(self):
        """Save extracted data sources to files"""
        timestamp = int(time.time())
        
        # Remove duplicates
        unique_sources = []
        seen_endpoints = set()
        
        for source in self.data_sources:
            endpoint = source.get('endpoint', '')
            if endpoint and endpoint not in seen_endpoints:
                unique_sources.append(source)
                seen_endpoints.add(endpoint)
        
        # Save as JSON
        json_file = f"cds_data_sources_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(unique_sources, f, indent=2)
        
        # Save as Python list for easy import
        py_file = f"cds_bank_list_{timestamp}.py"
        with open(py_file, 'w') as f:
            f.write("# Extracted bank API endpoints from CDS product comparator demo\n")
            f.write("# Generated automatically\n\n")
            f.write("BANK_API_ENDPOINTS = [\n")
            
            for i, source in enumerate(unique_sources):
                endpoint = source.get('endpoint', '')
                bank_name = source.get('bank_name', f'Bank{i+1}')
                brand_id = f"extracted-{i+1}"
                
                f.write(f'    ("{bank_name}", "{brand_id}", "{endpoint}"),\n')
            
            f.write("]\n")
        
        print(f"💾 Saved {len(unique_sources)} unique data sources to:")
        print(f"   📄 {json_file}")
        print(f"   🐍 {py_file}")
        
        return unique_sources
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    """Main execution function"""
    extractor = CDSDataSourceExtractor()
    
    try:
        # Extract data sources
        data_sources = extractor.extract_data_sources_from_demo()
        
        print(f"\n📊 Summary:")
        print(f"   Found {len(data_sources)} potential data sources")
        
        if data_sources:
            # Save results
            unique_sources = extractor.save_data_sources()
            
            print(f"\n🎯 Unique API endpoints found:")
            for source in unique_sources[:10]:  # Show first 10
                endpoint = source.get('endpoint', '')
                bank_name = source.get('bank_name', 'Unknown')
                print(f"   🏦 {bank_name}: {endpoint}")
            
            if len(unique_sources) > 10:
                print(f"   ... and {len(unique_sources) - 10} more")
        else:
            print("❌ No data sources found. The demo page structure might have changed.")
            print("💡 Try manually inspecting the page source or network requests.")
            
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        
    finally:
        extractor.cleanup()

if __name__ == "__main__":
    main()


