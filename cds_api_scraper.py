#!/usr/bin/env python3
"""
Consumer Data Standards API Home Loan Scraper

This scraper calls the Consumer Data Standards APIs directly to extract home loan data
from Australian banks and exports to CSV format.
"""

import json
import csv
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class HomeLoanProduct:
    """Data structure for home loan products"""
    bank_name: str
    product_id: str
    product_name: str
    product_category: str
    product_sub_category: str
    brand: str
    description: str
    interest_rate: str
    comparison_rate: str
    loan_purpose: str  # Investment / Owner Occupier / Both
    repayment_type: str  # Principal and Interest / Interest Only / Both
    offset_available: str  # Y/N
    redraw_available: str  # Y/N
    minimum_loan_amount: str
    maximum_loan_amount: str
    fees: Dict[str, str]  # Dictionary of fee types and amounts
    features: List[str]  # List of features
    eligibility: List[str]  # List of eligibility criteria
    constraints: List[str]  # List of constraints
    application_url: str
    effective_from: str
    last_updated: str

class ConsumerDataStandardsAPIScraper:
    """Scraper for Consumer Data Standards APIs"""
    
    def __init__(self):
        self.banks = {
            'ANZ': 'https://api.anz/cds-au/v1/banking/products',
            'CommBank': 'https://api.commbank.com.au/public/cds-au/v1/banking/products',
            'NAB': 'https://openbank.api.nab.com.au/cds-au/v1/banking/products',
            'Westpac': 'https://digital-api.westpac.com.au/cds-au/v1/banking/products'
        }
        self.all_products = []
        self.session = requests.Session()
        
        # Set common headers for API requests
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-AU,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        })
    
    def fetch_products_from_bank(self, bank_name: str, api_url: str) -> List[Dict[str, Any]]:
        """Fetch product data from a specific bank's API"""
        try:
            logger.info(f"Fetching products from {bank_name}: {api_url}")
            
            # Add specific headers that might be required
            headers = {}
            
            # Some banks might require specific headers - most require version 3
            if bank_name == 'CommBank':
                headers['x-v'] = '3'  # API version header commonly used in CDS
            elif bank_name == 'Westpac':
                headers['x-v'] = '3'
            elif bank_name == 'ANZ':
                headers['x-v'] = '3'
            elif bank_name == 'NAB':
                headers['x-v'] = '3'
            
            response = self.session.get(api_url, headers=headers, timeout=30)
            
            logger.info(f"{bank_name} API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('data', {}).get('products', [])
                logger.info(f"Retrieved {len(products)} products from {bank_name}")
                return products
            else:
                logger.warning(f"Failed to fetch from {bank_name}: {response.status_code} - {response.text[:200]}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching from {bank_name}: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {bank_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching from {bank_name}: {e}")
            return []
    
    def get_detailed_product_info(self, bank_name: str, product_id: str) -> Dict[str, Any]:
        """Get detailed product information including rates and fees"""
        try:
            # Construct detail URL (common pattern in CDS APIs)
            base_url = self.banks[bank_name]
            detail_url = f"{base_url}/{product_id}"
            
            headers = {'x-v': '3'}
            response = self.session.get(detail_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                logger.warning(f"Failed to get details for {product_id} from {bank_name}: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.warning(f"Error getting details for {product_id} from {bank_name}: {e}")
            return {}
    
    def extract_home_loan_products(self, products: List[Dict], bank_name: str) -> List[HomeLoanProduct]:
        """Extract and process home loan products from API data"""
        home_loans = []
        
        for product in products:
            try:
                # Filter for residential mortgages/home loans
                category = product.get('productCategory', '').lower()
                name = product.get('name', '').lower()
                description = product.get('description', '').lower()
                
                # Check if this is a home loan/residential mortgage
                is_home_loan = (
                    'residential' in category or 
                    'mortgage' in category or
                    'home loan' in name or
                    'mortgage' in name or
                    'residential' in name or
                    'home loan' in description or
                    'mortgage' in description or
                    'residential' in description
                )
                
                if not is_home_loan:
                    continue
                
                # Get detailed product information
                product_id = product.get('productId', '')
                detailed_info = self.get_detailed_product_info(bank_name, product_id)
                
                # Extract basic information
                home_loan = self.create_home_loan_product(product, detailed_info, bank_name)
                
                if home_loan:
                    home_loans.append(home_loan)
                    
            except Exception as e:
                logger.warning(f"Error processing product from {bank_name}: {e}")
                continue
        
        logger.info(f"Extracted {len(home_loans)} home loan products from {bank_name}")
        return home_loans
    
    def create_home_loan_product(self, product: Dict, detailed_info: Dict, bank_name: str) -> Optional[HomeLoanProduct]:
        """Create a HomeLoanProduct from API data"""
        try:
            # Extract basic product information
            product_id = product.get('productId', '')
            product_name = product.get('name', '')
            product_category = product.get('productCategory', '')
            brand = product.get('brand', bank_name)
            description = product.get('description', '')
            
            # Extract rates
            interest_rates = self.extract_interest_rates(detailed_info)
            comparison_rates = self.extract_comparison_rates(detailed_info)
            
            # Extract loan purposes and repayment types
            loan_purpose = self.extract_loan_purpose(product, detailed_info)
            repayment_type = self.extract_repayment_type(product, detailed_info)
            
            # Extract features
            features = self.extract_features(detailed_info)
            offset_available = "Y" if any("offset" in str(f).lower() for f in features) else "N"
            redraw_available = "Y" if any("redraw" in str(f).lower() for f in features) else "N"
            
            # Extract fees
            fees = self.extract_fees(detailed_info)
            
            # Extract eligibility and constraints
            eligibility = self.extract_eligibility(detailed_info)
            constraints = self.extract_constraints(detailed_info)
            
            # Extract loan amounts
            min_amount, max_amount = self.extract_loan_amounts(detailed_info)
            
            # Extract application URL
            application_url = self.extract_application_url(product, detailed_info)
            
            # Extract timestamps
            effective_from = product.get('effectiveFrom', '')
            last_updated = product.get('lastUpdated', '')
            
            return HomeLoanProduct(
                bank_name=bank_name,
                product_id=product_id,
                product_name=product_name,
                product_category=product_category,
                product_sub_category=product.get('productSubCategory', ''),
                brand=brand,
                description=description,
                interest_rate=interest_rates,
                comparison_rate=comparison_rates,
                loan_purpose=loan_purpose,
                repayment_type=repayment_type,
                offset_available=offset_available,
                redraw_available=redraw_available,
                minimum_loan_amount=min_amount,
                maximum_loan_amount=max_amount,
                fees=fees,
                features=features,
                eligibility=eligibility,
                constraints=constraints,
                application_url=application_url,
                effective_from=effective_from,
                last_updated=last_updated
            )
            
        except Exception as e:
            logger.warning(f"Error creating HomeLoanProduct: {e}")
            return None
    
    def extract_interest_rates(self, detailed_info: Dict) -> str:
        """Extract interest rates from detailed product info"""
        rates = []
        
        try:
            lending_rates = detailed_info.get('lendingRates', [])
            for rate in lending_rates:
                rate_type = rate.get('lendingRateType', '')
                rate_value = rate.get('rate', '')
                
                if rate_value:
                    rate_str = f"{rate_value * 100:.2f}%" if isinstance(rate_value, (int, float)) else str(rate_value)
                    if rate_type:
                        rates.append(f"{rate_type}: {rate_str}")
                    else:
                        rates.append(rate_str)
            
            return " | ".join(rates) if rates else ""
            
        except Exception as e:
            logger.warning(f"Error extracting interest rates: {e}")
            return ""
    
    def extract_comparison_rates(self, detailed_info: Dict) -> str:
        """Extract comparison rates from detailed product info"""
        try:
            # Look for comparison rate in various places
            comparison_rate = detailed_info.get('comparisonRate')
            if comparison_rate:
                if isinstance(comparison_rate, (int, float)):
                    return f"{comparison_rate * 100:.2f}%"
                return str(comparison_rate)
            
            # Check in lending rates
            lending_rates = detailed_info.get('lendingRates', [])
            for rate in lending_rates:
                if 'comparison' in rate.get('lendingRateType', '').lower():
                    rate_value = rate.get('rate', '')
                    if rate_value:
                        return f"{rate_value * 100:.2f}%" if isinstance(rate_value, (int, float)) else str(rate_value)
            
            return ""
            
        except Exception as e:
            logger.warning(f"Error extracting comparison rates: {e}")
            return ""
    
    def extract_loan_purpose(self, product: Dict, detailed_info: Dict) -> str:
        """Extract loan purpose (Investment/Owner Occupier/Both)"""
        try:
            # Check in constraints or eligibility
            constraints = detailed_info.get('constraints', [])
            eligibility = detailed_info.get('eligibility', [])
            features = detailed_info.get('features', [])
            
            all_text = " ".join([
                product.get('description', ''),
                str(constraints),
                str(eligibility),
                str(features)
            ]).lower()
            
            has_investment = 'investment' in all_text
            has_owner_occupier = 'owner occupier' in all_text or 'owner-occupier' in all_text or 'ppor' in all_text
            
            if has_investment and has_owner_occupier:
                return "Both"
            elif has_investment:
                return "Investment"
            elif has_owner_occupier:
                return "Owner Occupier"
            else:
                return "Not Specified"
                
        except Exception as e:
            logger.warning(f"Error extracting loan purpose: {e}")
            return "Not Specified"
    
    def extract_repayment_type(self, product: Dict, detailed_info: Dict) -> str:
        """Extract repayment type (Principal and Interest/Interest Only/Both)"""
        try:
            features = detailed_info.get('features', [])
            constraints = detailed_info.get('constraints', [])
            
            all_text = " ".join([
                product.get('description', ''),
                str(features),
                str(constraints)
            ]).lower()
            
            has_pi = 'principal and interest' in all_text or 'p&i' in all_text
            has_io = 'interest only' in all_text or 'i/o' in all_text
            
            if has_pi and has_io:
                return "Both"
            elif has_pi:
                return "Principal and Interest"
            elif has_io:
                return "Interest Only"
            else:
                return "Not Specified"
                
        except Exception as e:
            logger.warning(f"Error extracting repayment type: {e}")
            return "Not Specified"
    
    def extract_features(self, detailed_info: Dict) -> List[str]:
        """Extract product features"""
        try:
            features = []
            feature_list = detailed_info.get('features', [])
            
            for feature in feature_list:
                feature_type = feature.get('featureType', '')
                description = feature.get('description', '')
                
                if feature_type:
                    if description:
                        features.append(f"{feature_type}: {description}")
                    else:
                        features.append(feature_type)
            
            return features
            
        except Exception as e:
            logger.warning(f"Error extracting features: {e}")
            return []
    
    def extract_fees(self, detailed_info: Dict) -> Dict[str, str]:
        """Extract fee information"""
        fees = {}
        
        try:
            fee_list = detailed_info.get('fees', [])
            
            for fee in fee_list:
                fee_type = fee.get('feeType', '')
                name = fee.get('name', fee_type)
                amount = fee.get('amount')
                rate = fee.get('rate')
                
                if amount:
                    fees[name] = f"${amount}"
                elif rate:
                    fees[name] = f"{rate * 100:.2f}%" if isinstance(rate, (int, float)) else str(rate)
                else:
                    fees[name] = "See terms"
            
            return fees
            
        except Exception as e:
            logger.warning(f"Error extracting fees: {e}")
            return {}
    
    def extract_eligibility(self, detailed_info: Dict) -> List[str]:
        """Extract eligibility criteria"""
        try:
            eligibility = []
            eligibility_list = detailed_info.get('eligibility', [])
            
            for item in eligibility_list:
                eligibility_type = item.get('eligibilityType', '')
                description = item.get('description', '')
                
                if description:
                    eligibility.append(description)
                elif eligibility_type:
                    eligibility.append(eligibility_type)
            
            return eligibility
            
        except Exception as e:
            logger.warning(f"Error extracting eligibility: {e}")
            return []
    
    def extract_constraints(self, detailed_info: Dict) -> List[str]:
        """Extract product constraints"""
        try:
            constraints = []
            constraint_list = detailed_info.get('constraints', [])
            
            for item in constraint_list:
                constraint_type = item.get('constraintType', '')
                description = item.get('description', '')
                
                if description:
                    constraints.append(description)
                elif constraint_type:
                    constraints.append(constraint_type)
            
            return constraints
            
        except Exception as e:
            logger.warning(f"Error extracting constraints: {e}")
            return []
    
    def extract_loan_amounts(self, detailed_info: Dict) -> tuple:
        """Extract minimum and maximum loan amounts"""
        try:
            constraints = detailed_info.get('constraints', [])
            
            min_amount = ""
            max_amount = ""
            
            for constraint in constraints:
                constraint_type = constraint.get('constraintType', '').lower()
                value = constraint.get('value')
                
                if 'min' in constraint_type and 'amount' in constraint_type:
                    min_amount = f"${value}" if value else ""
                elif 'max' in constraint_type and 'amount' in constraint_type:
                    max_amount = f"${value}" if value else ""
            
            return min_amount, max_amount
            
        except Exception as e:
            logger.warning(f"Error extracting loan amounts: {e}")
            return "", ""
    
    def extract_application_url(self, product: Dict, detailed_info: Dict) -> str:
        """Extract application URL"""
        try:
            # Check for application URI in product data
            app_url = detailed_info.get('applicationUri') or product.get('applicationUri', '')
            return app_url
            
        except Exception as e:
            logger.warning(f"Error extracting application URL: {e}")
            return ""
    
    def scrape_all_banks(self) -> List[HomeLoanProduct]:
        """Scrape home loan data from all banks"""
        all_home_loans = []
        
        for bank_name, api_url in self.banks.items():
            try:
                logger.info(f"Processing {bank_name}...")
                
                # Fetch products from bank
                products = self.fetch_products_from_bank(bank_name, api_url)
                
                if products:
                    # Extract home loan products
                    home_loans = self.extract_home_loan_products(products, bank_name)
                    all_home_loans.extend(home_loans)
                
                # Small delay between banks to be respectful
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing {bank_name}: {e}")
                continue
        
        self.all_products = all_home_loans
        logger.info(f"Total home loan products scraped: {len(all_home_loans)}")
        return all_home_loans
    
    def save_to_csv(self, filename: str = None) -> str:
        """Save scraped data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"home_loans_cds_api_{timestamp}.csv"
        
        try:
            if not self.all_products:
                logger.warning("No products to save")
                return filename
            
            # Convert products to dictionaries
            data_rows = []
            all_fee_types = set()
            
            # First pass: collect all unique fee types
            for product in self.all_products:
                all_fee_types.update(product.fees.keys())
            
            # Second pass: create rows with all fee columns
            for product in self.all_products:
                row = {
                    'Bank': product.bank_name,
                    'Product ID': product.product_id,
                    'Product Name': product.product_name,
                    'Category': product.product_category,
                    'Sub Category': product.product_sub_category,
                    'Brand': product.brand,
                    'Description': product.description[:500] + "..." if len(product.description) > 500 else product.description,
                    'Interest Rate': product.interest_rate,
                    'Comparison Rate': product.comparison_rate,
                    'Loan Purpose': product.loan_purpose,
                    'Repayment Type': product.repayment_type,
                    'Offset Available': product.offset_available,
                    'Redraw Available': product.redraw_available,
                    'Min Loan Amount': product.minimum_loan_amount,
                    'Max Loan Amount': product.maximum_loan_amount,
                    'Features': " | ".join(product.features) if product.features else "",
                    'Eligibility': " | ".join(product.eligibility) if product.eligibility else "",
                    'Constraints': " | ".join(product.constraints) if product.constraints else "",
                    'Application URL': product.application_url,
                    'Effective From': product.effective_from,
                    'Last Updated': product.last_updated
                }
                
                # Add fee columns
                for fee_type in sorted(all_fee_types):
                    row[f'Fee - {fee_type}'] = product.fees.get(fee_type, '')
                
                data_rows.append(row)
            
            # Write to CSV
            if data_rows:
                fieldnames = list(data_rows[0].keys())
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data_rows)
                
                logger.info(f"Data saved to {filename}")
                logger.info(f"Columns: {len(fieldnames)}")
                logger.info(f"Rows: {len(data_rows)}")
                
                # Print summary
                print(f"\n=== SCRAPING SUMMARY ===")
                print(f"Total products scraped: {len(data_rows)}")
                print(f"Banks processed: {len(set(row['Bank'] for row in data_rows))}")
                print(f"Unique fee types found: {len(all_fee_types)}")
                print(f"Data saved to: {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            raise

def main():
    """Main function to run the API scraper"""
    print("Consumer Data Standards API Home Loan Scraper")
    print("=" * 50)
    
    scraper = ConsumerDataStandardsAPIScraper()
    
    try:
        # Scrape all banks
        products = scraper.scrape_all_banks()
        
        if products:
            # Save to CSV
            filename = scraper.save_to_csv()
            print(f"\nScraping completed successfully!")
            print(f"Found {len(products)} home loan products")
            print(f"Data saved to: {filename}")
        else:
            print("No home loan products were found.")
            
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
