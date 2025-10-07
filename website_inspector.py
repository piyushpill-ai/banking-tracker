#!/usr/bin/env python3
"""
Website Inspector for Consumer Data Standards Australia Product Comparator Demo

This script inspects the website structure to understand how data is loaded and organized.
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebsiteInspector:
    """Inspector to analyze the Consumer Data Standards Australia website structure"""
    
    def __init__(self):
        self.base_url = "https://consumerdatastandardsaustralia.github.io/product-comparator-demo/"
        self.driver = None
        
    def setup_driver(self):
        """Initialize Chrome WebDriver"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            logger.info("Chrome WebDriver initialized")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def load_and_analyze(self):
        """Load the page and analyze its structure"""
        try:
            logger.info(f"Loading page: {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(5)  # Allow JavaScript to execute
            
            print("=== PAGE TITLE ===")
            print(self.driver.title)
            
            print("\n=== PAGE SOURCE PREVIEW ===")
            page_source = self.driver.page_source
            print(f"Page source length: {len(page_source)} characters")
            print("First 1000 characters:")
            print(page_source[:1000])
            
            # Analyze main structure
            self.analyze_main_structure()
            
            # Look for data sources
            self.analyze_data_sources()
            
            # Look for console output or API data
            self.analyze_console_output()
            
            # Check for network requests
            self.analyze_network_activity()
            
            # Save full HTML for manual inspection
            self.save_html()
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
    
    def analyze_main_structure(self):
        """Analyze the main page structure"""
        print("\n=== MAIN PAGE STRUCTURE ===")
        
        # Get all main containers
        containers = self.driver.find_elements(By.CSS_SELECTOR, "div, section, main, article")
        print(f"Found {len(containers)} container elements")
        
        # Look for specific classes or IDs
        common_selectors = [
            "#app", "#root", ".app", ".main",
            ".data-source", ".data-sources", ".providers",
            ".console", ".output", ".products", ".mortgages",
            ".loan", ".home-loan", ".residential"
        ]
        
        for selector in common_selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"Found elements for selector '{selector}': {len(elements)}")
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    print(f"  Element {i+1}: {elem.tag_name}, text preview: {elem.text[:100]}...")
    
    def analyze_data_sources(self):
        """Look for data sources section"""
        print("\n=== DATA SOURCES ANALYSIS ===")
        
        # Search for text containing "data source" or "provider"
        text_elements = self.driver.find_elements(By.XPATH, 
            "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'data source') or " +
            "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'provider') or " +
            "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'bank')]")
        
        print(f"Found {len(text_elements)} elements containing data source/provider/bank text")
        for i, elem in enumerate(text_elements[:10]):
            print(f"  {i+1}. {elem.tag_name}: {elem.text.strip()[:150]}...")
        
        # Look for buttons or interactive elements
        buttons = self.driver.find_elements(By.CSS_SELECTOR, "button, .btn, .button")
        if buttons:
            print(f"\nFound {len(buttons)} button elements:")
            for i, btn in enumerate(buttons[:10]):
                print(f"  {i+1}. {btn.text.strip()[:100]}")
    
    def analyze_console_output(self):
        """Look for console output or product data"""
        print("\n=== CONSOLE OUTPUT / PRODUCTS ANALYSIS ===")
        
        # Search for elements that might contain product data
        product_keywords = ["product", "mortgage", "loan", "rate", "interest", "residential"]
        
        for keyword in product_keywords:
            elements = self.driver.find_elements(By.XPATH, 
                f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]")
            if elements:
                print(f"\nElements containing '{keyword}': {len(elements)}")
                for i, elem in enumerate(elements[:5]):
                    print(f"  {i+1}. {elem.tag_name}: {elem.text.strip()[:100]}...")
        
        # Look for tables or structured data
        tables = self.driver.find_elements(By.CSS_SELECTOR, "table, .table, .data-table")
        if tables:
            print(f"\nFound {len(tables)} table elements")
            for i, table in enumerate(tables):
                rows = table.find_elements(By.CSS_SELECTOR, "tr, .row")
                print(f"  Table {i+1}: {len(rows)} rows")
        
        # Look for JSON or pre-formatted data
        pre_elements = self.driver.find_elements(By.CSS_SELECTOR, "pre, code, .json, .code")
        if pre_elements:
            print(f"\nFound {len(pre_elements)} pre/code elements")
            for i, pre in enumerate(pre_elements[:3]):
                print(f"  {i+1}. Content preview: {pre.text[:200]}...")
    
    def analyze_network_activity(self):
        """Check for network requests and API calls"""
        print("\n=== NETWORK ACTIVITY ANALYSIS ===")
        
        # Execute JavaScript to get network information
        try:
            # Get performance entries
            performance_data = self.driver.execute_script("""
                return performance.getEntriesByType('resource').map(entry => ({
                    name: entry.name,
                    type: entry.initiatorType,
                    duration: entry.duration
                }));
            """)
            
            print(f"Found {len(performance_data)} network requests")
            
            # Filter for API-like requests
            api_requests = [req for req in performance_data if 
                          'api' in req['name'].lower() or 
                          'json' in req['name'].lower() or
                          req['name'].endswith('.json')]
            
            if api_requests:
                print("Potential API requests:")
                for req in api_requests[:10]:
                    print(f"  - {req['name']}")
            
            # Look for XHR requests
            xhr_requests = [req for req in performance_data if req['type'] == 'xmlhttprequest']
            if xhr_requests:
                print(f"\nFound {len(xhr_requests)} XHR requests:")
                for req in xhr_requests[:5]:
                    print(f"  - {req['name']}")
                    
        except Exception as e:
            print(f"Could not analyze network activity: {e}")
    
    def save_html(self):
        """Save the full HTML for manual inspection"""
        try:
            with open('/Users/piyushpillai/Desktop/fhl ob/website_structure.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print("\n=== HTML SAVED ===")
            print("Full HTML saved to 'website_structure.html' for manual inspection")
        except Exception as e:
            print(f"Error saving HTML: {e}")
    
    def interactive_exploration(self):
        """Allow interactive exploration of the page"""
        print("\n=== INTERACTIVE EXPLORATION ===")
        print("The browser window will stay open for 60 seconds for manual inspection...")
        print("You can:")
        print("1. Open developer tools (F12)")
        print("2. Inspect elements")
        print("3. Check the Console tab for any API calls")
        print("4. Look at the Network tab to see data requests")
        
        time.sleep(60)  # Keep browser open for manual inspection

def main():
    """Main function to run the inspector"""
    inspector = WebsiteInspector()
    
    try:
        inspector.setup_driver()
        inspector.load_and_analyze()
        
        # Uncomment the next line if you want to manually inspect the page
        # inspector.interactive_exploration()
        
    except Exception as e:
        print(f"Inspection failed: {e}")

if __name__ == "__main__":
    main()


