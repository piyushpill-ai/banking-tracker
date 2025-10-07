#!/usr/bin/env python3
"""
Home Loan Data Scraper for Consumer Data Standards Australia Product Comparator Demo

This scraper extracts home loan product data from multiple data sources and exports to CSV.
"""

import time
import json
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class HomeLoanProduct:
    """Data structure for home loan products"""
    data_source: str
    product_name: str
    interest_rate: str
    comparison_rate: str
    loan_purpose: str  # Investment / Owner Occupier
    repayment_type: str  # Principal and Interest / Interest Only
    offset_available: str  # Y/N
    fees: Dict[str, str]  # Dictionary of fee types and amounts

class HomeLoanScraper:
    """Scraper for Consumer Data Standards Australia Product Comparator Demo"""
    
    def __init__(self, headless: bool = True):
        self.base_url = "https://consumerdatastandardsaustralia.github.io/product-comparator-demo/"
        self.driver = None
        self.headless = headless
        self.data_sources = []
        self.all_products = []
        
    def setup_driver(self):
        """Initialize the Chrome WebDriver with appropriate options"""
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def load_page(self):
        """Load the main page and wait for it to be ready"""
        try:
            logger.info(f"Loading page: {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for the page to load completely
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give additional time for JavaScript to execute
            time.sleep(5)
            logger.info("Page loaded successfully")
            
        except TimeoutException:
            logger.error("Page load timeout")
            raise
        except Exception as e:
            logger.error(f"Error loading page: {e}")
            raise
    
    def discover_data_sources(self) -> List[str]:
        """Identify all available data sources from the Data Sources section"""
        try:
            logger.info("Discovering data sources...")
            
            # Look for data sources section - we need to inspect the actual HTML structure
            # This is a placeholder - we'll need to update this based on the actual website structure
            data_source_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                                                            "[data-testid*='data-source'], .data-source, .provider")
            
            if not data_source_elements:
                # Try alternative selectors
                data_source_elements = self.driver.find_elements(By.XPATH, 
                                                               "//div[contains(text(), 'Data Source') or contains(text(), 'Provider')]")
            
            data_sources = []
            for element in data_source_elements:
                text = element.text.strip()
                if text and text not in data_sources:
                    data_sources.append(text)
            
            logger.info(f"Found {len(data_sources)} data sources: {data_sources}")
            self.data_sources = data_sources
            return data_sources
            
        except Exception as e:
            logger.error(f"Error discovering data sources: {e}")
            return []
    
    def extract_residential_mortgages(self, data_source: str) -> List[HomeLoanProduct]:
        """Extract residential mortgage products for a specific data source"""
        products = []
        
        try:
            logger.info(f"Extracting residential mortgages for: {data_source}")
            
            # This will need to be customized based on the actual website structure
            # We need to navigate to the Console Output > Products > Residential Mortgages
            
            # Look for product containers
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                                                       ".product, .mortgage-product, [data-product-type='mortgage']")
            
            for product_element in product_elements:
                try:
                    product_data = self.extract_product_data(product_element, data_source)
                    if product_data:
                        products.append(product_data)
                except Exception as e:
                    logger.warning(f"Error extracting product data: {e}")
                    continue
            
            logger.info(f"Extracted {len(products)} products from {data_source}")
            
        except Exception as e:
            logger.error(f"Error extracting residential mortgages for {data_source}: {e}")
        
        return products
    
    def extract_product_data(self, element, data_source: str) -> HomeLoanProduct:
        """Extract individual product data from a product element"""
        try:
            # Extract product name
            product_name = self.safe_extract_text(element, ".product-name, .name, h3, h4")
            
            # Extract interest rate
            interest_rate = self.safe_extract_text(element, ".interest-rate, .rate, [data-field='interest-rate']")
            
            # Extract comparison rate
            comparison_rate = self.safe_extract_text(element, ".comparison-rate, [data-field='comparison-rate']")
            
            # Extract loan purpose
            loan_purpose = self.safe_extract_text(element, ".loan-purpose, .purpose, [data-field='loan-purpose']")
            
            # Extract repayment type
            repayment_type = self.safe_extract_text(element, ".repayment-type, [data-field='repayment-type']")
            
            # Extract offset availability
            offset_available = self.extract_offset_feature(element)
            
            # Extract fees
            fees = self.extract_fees(element)
            
            return HomeLoanProduct(
                data_source=data_source,
                product_name=product_name,
                interest_rate=interest_rate,
                comparison_rate=comparison_rate,
                loan_purpose=loan_purpose,
                repayment_type=repayment_type,
                offset_available=offset_available,
                fees=fees
            )
            
        except Exception as e:
            logger.warning(f"Error extracting product data: {e}")
            return None
    
    def safe_extract_text(self, parent_element, selector: str) -> str:
        """Safely extract text from an element using CSS selector"""
        try:
            element = parent_element.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except NoSuchElementException:
            return ""
    
    def extract_offset_feature(self, element) -> str:
        """Extract whether offset account is available"""
        try:
            # Look for offset-related text or elements
            offset_elements = element.find_elements(By.XPATH, 
                                                  ".//*[contains(text(), 'offset') or contains(text(), 'Offset')]")
            
            if offset_elements:
                text = offset_elements[0].text.lower()
                if 'yes' in text or 'available' in text or 'included' in text:
                    return "Y"
                elif 'no' in text or 'not available' in text:
                    return "N"
            
            # Check for boolean indicators
            features = element.find_elements(By.CSS_SELECTOR, ".feature, .features")
            for feature in features:
                if 'offset' in feature.text.lower():
                    return "Y"
            
            return "N"
            
        except Exception:
            return "N"
    
    def extract_fees(self, element) -> Dict[str, str]:
        """Extract fee information"""
        fees = {}
        
        try:
            # Look for fee elements
            fee_elements = element.find_elements(By.CSS_SELECTOR, 
                                               ".fee, .fees, [data-field*='fee']")
            
            for fee_element in fee_elements:
                fee_text = fee_element.text.strip()
                if fee_text:
                    # Try to parse fee name and amount
                    if ':' in fee_text:
                        fee_name, fee_amount = fee_text.split(':', 1)
                        fees[fee_name.strip()] = fee_amount.strip()
                    else:
                        fees['General Fee'] = fee_text
            
            # If no fees found, check for fee tables or lists
            if not fees:
                fee_rows = element.find_elements(By.CSS_SELECTOR, 
                                               "tr, li, .fee-item")
                for row in fee_rows:
                    cells = row.find_elements(By.CSS_SELECTOR, "td, .fee-name, .fee-amount")
                    if len(cells) >= 2:
                        fees[cells[0].text.strip()] = cells[1].text.strip()
            
        except Exception as e:
            logger.warning(f"Error extracting fees: {e}")
        
        return fees
    
    def scrape_all_data(self) -> List[HomeLoanProduct]:
        """Main method to scrape all home loan data"""
        try:
            self.setup_driver()
            self.load_page()
            
            # Discover all data sources
            data_sources = self.discover_data_sources()
            
            if not data_sources:
                logger.warning("No data sources found. Will attempt to scrape available data.")
                # Try to extract data without specific data source filtering
                products = self.extract_residential_mortgages("Unknown")
                self.all_products.extend(products)
            else:
                # Scrape data for each data source
                for data_source in data_sources:
                    logger.info(f"Processing data source: {data_source}")
                    
                    # Select or filter by this data source if needed
                    # This might involve clicking on the data source or filtering
                    
                    products = self.extract_residential_mortgages(data_source)
                    self.all_products.extend(products)
                    
                    # Small delay between data sources
                    time.sleep(2)
            
            logger.info(f"Total products scraped: {len(self.all_products)}")
            return self.all_products
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_to_csv(self, filename: str = None) -> str:
        """Save scraped data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"home_loans_{timestamp}.csv"
        
        try:
            # Convert products to DataFrame
            data_rows = []
            all_fee_types = set()
            
            # First pass: collect all unique fee types
            for product in self.all_products:
                all_fee_types.update(product.fees.keys())
            
            # Second pass: create rows with all fee columns
            for product in self.all_products:
                row = {
                    'Data Source': product.data_source,
                    'Product Name': product.product_name,
                    'Interest Rate': product.interest_rate,
                    'Comparison Rate': product.comparison_rate,
                    'Loan Purpose': product.loan_purpose,
                    'Repayment Type': product.repayment_type,
                    'Offset Available': product.offset_available,
                }
                
                # Add fee columns
                for fee_type in sorted(all_fee_types):
                    row[f'Fee - {fee_type}'] = product.fees.get(fee_type, '')
                
                data_rows.append(row)
            
            # Create DataFrame and save to CSV
            df = pd.DataFrame(data_rows)
            df.to_csv(filename, index=False)
            
            logger.info(f"Data saved to {filename}")
            logger.info(f"Columns: {list(df.columns)}")
            logger.info(f"Rows: {len(df)}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            raise

def main():
    """Main function to run the scraper"""
    scraper = HomeLoanScraper(headless=False)  # Set to True for headless mode
    
    try:
        # Scrape all data
        products = scraper.scrape_all_data()
        
        if products:
            # Save to CSV
            filename = scraper.save_to_csv()
            print(f"Successfully scraped {len(products)} home loan products")
            print(f"Data saved to: {filename}")
        else:
            print("No products were scraped. Please check the website structure.")
            
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()


