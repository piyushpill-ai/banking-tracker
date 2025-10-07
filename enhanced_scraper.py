#!/usr/bin/env python3
"""
Enhanced Home Loan Scraper for Consumer Data Standards Australia

This scraper combines API calls with web scraping to get comprehensive home loan data
including interest rates, comparison rates, fees, and features.
"""

import json
import csv
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class HomeLoanProduct:
    """Enhanced data structure for home loan products"""
    bank_name: str
    product_id: str
    product_name: str
    product_category: str
    brand: str
    description: str
    variable_rate: str
    fixed_rate: str
    comparison_rate: str
    loan_purpose: str
    repayment_type: str
    offset_available: str
    redraw_available: str
    minimum_loan_amount: str
    maximum_loan_amount: str
    application_fee: str
    annual_fee: str
    early_exit_fee: str
    other_fees: str
    features: str
    application_url: str
    last_updated: str

class EnhancedHomeLoanScraper:
    """Enhanced scraper combining API calls with web scraping"""
    
    def __init__(self):
        self.banks = {
            'ANZ': 'https://api.anz/cds-au/v1/banking/products',
            'CommBank': 'https://api.commbank.com.au/public/cds-au/v1/banking/products',
            'NAB': 'https://openbank.api.nab.com.au/cds-au/v1/banking/products',
            'Westpac': 'https://digital-api.westpac.com.au/cds-au/v1/banking/products'
        }
        self.all_products = []
        self.session = requests.Session()
        self.driver = None
        
        # Set headers for API requests
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-AU,en;q=0.9'
        })
    
    def setup_selenium(self):
        """Setup Selenium for web scraping fallback"""
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            logger.info("Selenium WebDriver initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Selenium: {e}")
    
    def fetch_api_products(self, bank_name: str, api_url: str) -> List[Dict]:
        """Fetch products from CDS API"""
        try:
            headers = {'x-v': '3'}
            response = self.session.get(api_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('data', {}).get('products', [])
                logger.info(f"API: Retrieved {len(products)} products from {bank_name}")
                return products
            else:
                logger.warning(f"API failed for {bank_name}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"API error for {bank_name}: {e}")
            return []
    
    def scrape_web_data(self, bank_name: str) -> List[Dict]:
        """Scrape additional data from bank websites as fallback"""
        if not self.driver:
            return []
        
        try:
            # Bank-specific scraping logic
            if bank_name == 'ANZ':
                return self.scrape_anz_website()
            elif bank_name == 'CommBank':
                return self.scrape_commbank_website()
            elif bank_name == 'NAB':
                return self.scrape_nab_website()
            elif bank_name == 'Westpac':
                return self.scrape_westpac_website()
            else:
                return []
        except Exception as e:
            logger.warning(f"Web scraping failed for {bank_name}: {e}")
            return []
    
    def scrape_anz_website(self) -> List[Dict]:
        """Scrape ANZ home loan rates"""
        try:
            self.driver.get("https://www.anz.com.au/personal/home-loans/interest-rates/")
            time.sleep(3)
            
            rates_data = []
            
            # Look for rate tables
            rate_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".rate-table tr, .interest-rate, .rate-display")
            
            for element in rate_elements:
                try:
                    text = element.text.strip()
                    if '%' in text and any(keyword in text.lower() for keyword in ['variable', 'fixed', 'standard']):
                        rates_data.append({'source': 'web', 'rate_text': text})
                except:
                    continue
            
            logger.info(f"ANZ web scraping found {len(rates_data)} rate entries")
            return rates_data
            
        except Exception as e:
            logger.warning(f"ANZ web scraping error: {e}")
            return []
    
    def scrape_commbank_website(self) -> List[Dict]:
        """Scrape CommBank home loan rates"""
        try:
            self.driver.get("https://www.commbank.com.au/home-loans/interest-rates.html")
            time.sleep(3)
            
            rates_data = []
            
            # Look for rate information
            rate_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".rate, .interest-rate, .cba-rate, [data-rate]")
            
            for element in rate_elements:
                try:
                    text = element.text.strip()
                    if '%' in text:
                        rates_data.append({'source': 'web', 'rate_text': text})
                except:
                    continue
            
            logger.info(f"CommBank web scraping found {len(rates_data)} rate entries")
            return rates_data
            
        except Exception as e:
            logger.warning(f"CommBank web scraping error: {e}")
            return []
    
    def scrape_nab_website(self) -> List[Dict]:
        """Scrape NAB home loan rates"""
        try:
            self.driver.get("https://www.nab.com.au/personal/home-loans/home-loan-interest-rates")
            time.sleep(3)
            
            rates_data = []
            
            # Look for rate information
            rate_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".rate, .interest-rate, .rate-display")
            
            for element in rate_elements:
                try:
                    text = element.text.strip()
                    if '%' in text:
                        rates_data.append({'source': 'web', 'rate_text': text})
                except:
                    continue
            
            logger.info(f"NAB web scraping found {len(rates_data)} rate entries")
            return rates_data
            
        except Exception as e:
            logger.warning(f"NAB web scraping error: {e}")
            return []
    
    def scrape_westpac_website(self) -> List[Dict]:
        """Scrape Westpac home loan rates"""
        try:
            self.driver.get("https://www.westpac.com.au/personal-banking/home-loans/interest-rates/")
            time.sleep(3)
            
            rates_data = []
            
            # Look for rate information
            rate_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".rate, .interest-rate, .rate-table td")
            
            for element in rate_elements:
                try:
                    text = element.text.strip()
                    if '%' in text:
                        rates_data.append({'source': 'web', 'rate_text': text})
                except:
                    continue
            
            logger.info(f"Westpac web scraping found {len(rates_data)} rate entries")
            return rates_data
            
        except Exception as e:
            logger.warning(f"Westpac web scraping error: {e}")
            return []
    
    def extract_rates_from_text(self, text: str) -> Dict[str, str]:
        """Extract rates from text using regex"""
        rates = {}
        
        # Look for percentage rates
        rate_patterns = [
            r'(\d+\.\d+)%',  # Basic percentage
            r'(\d+\.\d{2})% p\.a\.',  # Per annum
            r'from (\d+\.\d+)%',  # From rate
            r'up to (\d+\.\d+)%'  # Up to rate
        ]
        
        for pattern in rate_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                rates['extracted_rate'] = f"{matches[0]}%"
                break
        
        return rates
    
    def merge_api_and_web_data(self, api_products: List[Dict], web_data: List[Dict], bank_name: str) -> List[HomeLoanProduct]:
        """Merge API and web-scraped data"""
        enhanced_products = []
        
        for product in api_products:
            # Skip non-residential mortgage products
            category = product.get('productCategory', '').lower()
            name = product.get('name', '').lower()
            
            if 'residential' not in category and 'mortgage' not in name and 'home loan' not in name:
                continue
            
            # Extract basic info from API
            home_loan = self.create_enhanced_product(product, web_data, bank_name)
            if home_loan:
                enhanced_products.append(home_loan)
        
        return enhanced_products
    
    def create_enhanced_product(self, product: Dict, web_data: List[Dict], bank_name: str) -> Optional[HomeLoanProduct]:
        """Create enhanced product with both API and web data"""
        try:
            # Basic API data
            product_id = product.get('productId', '')
            product_name = product.get('name', '')
            product_category = product.get('productCategory', '')
            brand = product.get('brand', bank_name)
            description = product.get('description', '')
            
            # Try to extract rates from description or use web data
            variable_rate = ""
            fixed_rate = ""
            comparison_rate = ""
            
            # Extract rates from description
            desc_rates = self.extract_rates_from_text(description)
            if desc_rates.get('extracted_rate'):
                if 'variable' in description.lower():
                    variable_rate = desc_rates['extracted_rate']
                elif 'fixed' in description.lower():
                    fixed_rate = desc_rates['extracted_rate']
            
            # Try to get rates from web data
            if not variable_rate and not fixed_rate and web_data:
                for web_item in web_data[:3]:  # Use first few web results
                    web_rates = self.extract_rates_from_text(web_item.get('rate_text', ''))
                    if web_rates.get('extracted_rate') and not variable_rate:
                        variable_rate = web_rates['extracted_rate']
                        break
            
            # Extract loan purpose and repayment type
            loan_purpose = self.extract_loan_purpose_enhanced(product)
            repayment_type = self.extract_repayment_type_enhanced(product)
            
            # Extract features
            features = self.extract_features_enhanced(product)
            offset_available = "Y" if "offset" in features.lower() else "N"
            redraw_available = "Y" if "redraw" in features.lower() else "N"
            
            # Extract fees (from description if available)
            fees = self.extract_fees_from_description(description)
            
            # Application URL
            application_url = product.get('applicationUri', '')
            
            return HomeLoanProduct(
                bank_name=bank_name,
                product_id=product_id,
                product_name=product_name,
                product_category=product_category,
                brand=brand,
                description=description[:500] + "..." if len(description) > 500 else description,
                variable_rate=variable_rate,
                fixed_rate=fixed_rate,
                comparison_rate=comparison_rate,
                loan_purpose=loan_purpose,
                repayment_type=repayment_type,
                offset_available=offset_available,
                redraw_available=redraw_available,
                minimum_loan_amount="",
                maximum_loan_amount="",
                application_fee=fees.get('application_fee', ''),
                annual_fee=fees.get('annual_fee', ''),
                early_exit_fee=fees.get('early_exit_fee', ''),
                other_fees=fees.get('other_fees', ''),
                features=features,
                application_url=application_url,
                last_updated=product.get('lastUpdated', '')
            )
            
        except Exception as e:
            logger.warning(f"Error creating enhanced product: {e}")
            return None
    
    def extract_loan_purpose_enhanced(self, product: Dict) -> str:
        """Enhanced loan purpose extraction"""
        text = " ".join([
            product.get('description', ''),
            product.get('name', ''),
            str(product.get('additionalInformation', {}))
        ]).lower()
        
        has_investment = any(word in text for word in ['investment', 'investor', 'rental'])
        has_owner_occ = any(word in text for word in ['owner occupier', 'owner-occupier', 'ppor', 'principal place'])
        
        if has_investment and has_owner_occ:
            return "Both"
        elif has_investment:
            return "Investment"
        elif has_owner_occ:
            return "Owner Occupier"
        else:
            return "Both"  # Default for most home loans
    
    def extract_repayment_type_enhanced(self, product: Dict) -> str:
        """Enhanced repayment type extraction"""
        text = " ".join([
            product.get('description', ''),
            product.get('name', ''),
            str(product.get('additionalInformation', {}))
        ]).lower()
        
        has_pi = any(phrase in text for phrase in ['principal and interest', 'p&i', 'principal & interest'])
        has_io = any(phrase in text for phrase in ['interest only', 'interest-only', 'i/o'])
        
        if has_pi and has_io:
            return "Both"
        elif has_io:
            return "Interest Only"
        else:
            return "Principal and Interest"  # Default
    
    def extract_features_enhanced(self, product: Dict) -> str:
        """Enhanced feature extraction"""
        features = []
        
        description = product.get('description', '').lower()
        name = product.get('name', '').lower()
        
        # Common features to look for
        feature_keywords = {
            'offset': 'Offset Account',
            'redraw': 'Redraw Facility',
            'extra repayment': 'Extra Repayments',
            'flexible': 'Flexible Repayments',
            'split': 'Split Loan Option',
            'construction': 'Construction Loan',
            'no fee': 'No Ongoing Fees',
            'low rate': 'Low Rate'
        }
        
        for keyword, feature in feature_keywords.items():
            if keyword in description or keyword in name:
                features.append(feature)
        
        return " | ".join(features) if features else ""
    
    def extract_fees_from_description(self, description: str) -> Dict[str, str]:
        """Extract fees from product description"""
        fees = {}
        
        # Look for fee mentions
        fee_patterns = {
            'application_fee': [r'application fee.*?\$(\d+)', r'setup fee.*?\$(\d+)'],
            'annual_fee': [r'annual fee.*?\$(\d+)', r'yearly fee.*?\$(\d+)'],
            'early_exit_fee': [r'exit fee.*?\$(\d+)', r'break fee.*?\$(\d+)']
        }
        
        for fee_type, patterns in fee_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, description.lower())
                if match:
                    fees[fee_type] = f"${match.group(1)}"
                    break
        
        # Check for "no fees" mentions
        if any(phrase in description.lower() for phrase in ['no fees', 'no ongoing fees', 'fee-free']):
            fees['other_fees'] = 'No ongoing fees'
        
        return fees
    
    def scrape_all_banks(self) -> List[HomeLoanProduct]:
        """Main scraping method"""
        self.setup_selenium()
        all_products = []
        
        for bank_name, api_url in self.banks.items():
            try:
                logger.info(f"Processing {bank_name}...")
                
                # Get API data
                api_products = self.fetch_api_products(bank_name, api_url)
                
                # Get web data as supplement
                web_data = self.scrape_web_data(bank_name)
                
                # Merge and enhance data
                enhanced_products = self.merge_api_and_web_data(api_products, web_data, bank_name)
                all_products.extend(enhanced_products)
                
                logger.info(f"Total enhanced products from {bank_name}: {len(enhanced_products)}")
                
                time.sleep(2)  # Be respectful
                
            except Exception as e:
                logger.error(f"Error processing {bank_name}: {e}")
        
        if self.driver:
            self.driver.quit()
        
        self.all_products = all_products
        logger.info(f"Total enhanced products: {len(all_products)}")
        return all_products
    
    def save_to_csv(self, filename: str = None) -> str:
        """Save enhanced data to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_home_loans_{timestamp}.csv"
        
        try:
            if not self.all_products:
                logger.warning("No products to save")
                return filename
            
            # Define CSV columns in the order requested by user
            fieldnames = [
                'Bank', 'Product Name', 'Variable Interest Rate', 'Fixed Interest Rate', 
                'Comparison Rate', 'Loan Purpose', 'Repayment Type', 'Offset Available',
                'Redraw Available', 'Application Fee', 'Annual Fee', 'Early Exit Fee',
                'Other Fees', 'Features', 'Description', 'Application URL', 'Product ID'
            ]
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in self.all_products:
                    row = {
                        'Bank': product.bank_name,
                        'Product Name': product.product_name,
                        'Variable Interest Rate': product.variable_rate,
                        'Fixed Interest Rate': product.fixed_rate,
                        'Comparison Rate': product.comparison_rate,
                        'Loan Purpose': product.loan_purpose,
                        'Repayment Type': product.repayment_type,
                        'Offset Available': product.offset_available,
                        'Redraw Available': product.redraw_available,
                        'Application Fee': product.application_fee,
                        'Annual Fee': product.annual_fee,
                        'Early Exit Fee': product.early_exit_fee,
                        'Other Fees': product.other_fees,
                        'Features': product.features,
                        'Description': product.description,
                        'Application URL': product.application_url,
                        'Product ID': product.product_id
                    }
                    writer.writerow(row)
            
            logger.info(f"Enhanced data saved to {filename}")
            
            # Print summary
            print(f"\n=== ENHANCED SCRAPING SUMMARY ===")
            print(f"Total products: {len(self.all_products)}")
            print(f"Banks processed: {len(set(p.bank_name for p in self.all_products))}")
            print(f"Products with rates: {len([p for p in self.all_products if p.variable_rate or p.fixed_rate])}")
            print(f"Products with features: {len([p for p in self.all_products if p.features])}")
            print(f"Data saved to: {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            raise

def main():
    """Main function"""
    print("Enhanced Home Loan Scraper")
    print("=" * 40)
    
    scraper = EnhancedHomeLoanScraper()
    
    try:
        products = scraper.scrape_all_banks()
        
        if products:
            filename = scraper.save_to_csv()
            print(f"\nScraping completed!")
            print(f"Enhanced data saved to: {filename}")
        else:
            print("No products found.")
            
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()


