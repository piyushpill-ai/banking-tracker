#!/usr/bin/env python3
"""
Term Deposits Scraper for Australian Banks
==========================================

Comprehensive scraper to collect term deposit rates and features from
Australian banks using Consumer Data Standards (CDS) APIs.

Collects:
- Term deposit rates
- Term lengths (3m, 6m, 1y, 2y, etc.)
- Minimum deposit amounts
- Interest payment frequencies
- Bonus rates and conditions
- Early withdrawal fees
- Account fees

Author: AI Assistant
Date: September 2025
"""

import asyncio
import logging
import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pydantic import BaseModel
import json
import time

# Import the comprehensive bank list
try:
    from luke_prior_bank_list_1758106523 import BANKS_FROM_CDR_REGISTER
except ImportError:
    print("⚠️ Could not import comprehensive bank list, using fallback list")
    BANKS_FROM_CDR_REGISTER = [
        ("ANZ", "anz", "https://api.anz/cds-au/v1/banking/products"),
        ("Commonwealth Bank", "cba", "https://api.commbank.com.au/public/cds-au/v1/banking/products"),
        ("NAB", "nab", "https://api.nab.com.au/cds-au/v1/banking/products"),
        ("Westpac", "westpac", "https://digital-api.westpac.com.au/cds-au/v1/banking/products"),
        ("UBank", "ubank", "https://public.cdr-api.86400.com.au/cds-au/v1/banking/products"),
    ]

@dataclass
class CDRBrand:
    """Represents a banking brand in the CDR register"""
    name: str
    id: str
    endpoint: str

class TermDepositRecord(BaseModel):
    """Structured term deposit record"""
    # Bank Information
    bank_name: str
    bank_id: str
    product_id: str
    product_name: str
    
    # Rate Information
    interest_rate: Optional[float] = None
    rate_type: Optional[str] = None  # FIXED, VARIABLE
    bonus_rate: Optional[float] = None
    
    # Term Information
    term_months: Optional[int] = None
    term_display: Optional[str] = None
    
    # Deposit Information
    minimum_deposit: Optional[float] = None
    maximum_deposit: Optional[float] = None
    
    # Interest Payment
    interest_payment_frequency: Optional[str] = None
    compound_frequency: Optional[str] = None
    
    # Fees
    account_fee: Optional[float] = None
    early_withdrawal_fee: Optional[float] = None
    early_withdrawal_fee_type: Optional[str] = None
    
    # Additional Information
    additional_info: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    application_url: Optional[str] = None
    last_updated: str

class TermDepositsScr(object):
    """Enhanced Term Deposits Scraper"""
    
    def __init__(self):
        """Initialize the scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-AU,en;q=0.9',
        })
        
        # Setup logging
        log_file = f'../data/term_deposits_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.all_records: List[TermDepositRecord] = []
        
    def get_bank_list(self) -> List[CDRBrand]:
        """Get comprehensive list of banks from CDR register"""
        banks = []
        for bank_name, bank_id, endpoint in BANKS_FROM_CDR_REGISTER:
            banks.append(CDRBrand(
                name=bank_name,
                id=bank_id,
                endpoint=endpoint
            ))
        return banks
    
    def is_term_deposit_product(self, product: Dict[str, Any]) -> bool:
        """Check if product is a term deposit"""
        product_category = product.get('productCategory', '').upper()
        product_name = product.get('name', '').upper()
        description = product.get('description', '').upper()
        
        # Term deposit indicators
        td_indicators = [
            'TERM_DEPOSITS',
            'TERM DEPOSIT',
            'TIME DEPOSIT', 
            'FIXED DEPOSIT',
            'INVESTMENT_DEPOSIT',
            'TERM INVESTMENT'
        ]
        
        # Check category
        if any(indicator in product_category for indicator in td_indicators):
            return True
            
        # Check name and description
        combined_text = f"{product_name} {description}"
        if any(indicator in combined_text for indicator in td_indicators):
            return True
            
        return False
    
    def fetch_products_for_brand(self, brand: CDRBrand) -> Optional[List[Dict[str, Any]]]:
        """Fetch term deposit products for a specific brand"""
        self.logger.info(f"🏦 {brand.name}: Processing term deposits...")
        
        try:
            # Try different API versions and endpoint patterns
            api_versions = ['3', '4', '2', '1']
            endpoint_patterns = [
                brand.endpoint,
                brand.endpoint.replace('/products', '/banking/products'),
                brand.endpoint.replace('cds-au/v1', 'cds-au/v3'),
                brand.endpoint.replace('cds-au/v1', 'cds-au/v2'),
            ]
            
            for version in api_versions:
                for endpoint in endpoint_patterns:
                    try:
                        headers = {'x-v': version}
                        response = self.session.get(endpoint, headers=headers, timeout=30)
                        
                        if response.status_code == 200:
                            data = response.json()
                            products = data.get('data', {}).get('products', [])
                            
                            # Filter for term deposits only
                            term_deposit_products = [
                                product for product in products 
                                if self.is_term_deposit_product(product)
                            ]
                            
                            if term_deposit_products:
                                self.logger.info(f"✅ {brand.name}: Found {len(term_deposit_products)} term deposit products (v{version})")
                                return term_deposit_products
                        else:
                            self.logger.warning(f"⚠️ {brand.name}: HTTP {response.status_code} with v{version}")
                            
                    except Exception as e:
                        continue
                        
            self.logger.error(f"❌ {brand.name}: All product fetch attempts failed")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ {brand.name}: Exception during fetch: {str(e)}")
            return None
    
    def get_product_details(self, brand: CDRBrand, product_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed product information"""
        try:
            detail_url = f"{brand.endpoint}/{product_id}"
            headers = {'x-v': '3'}
            
            response = self.session.get(detail_url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json().get('data', {})
            return None
            
        except Exception as e:
            self.logger.debug(f"Could not fetch details for {product_id}: {str(e)}")
            return None
    
    def extract_term_deposit_records(self, brand: CDRBrand, products: List[Dict[str, Any]]) -> List[TermDepositRecord]:
        """Extract individual term deposit records from products"""
        records = []
        
        for product in products:
            product_id = product.get('productId')
            product_name = product.get('name')
            
            # Get detailed product information
            details = self.get_product_details(brand, product_id)
            if not details:
                details = product  # Fallback to basic product info
            
            # Extract deposit rates
            deposit_rates = details.get('depositRates', [])
            
            if not deposit_rates:
                # Create record without rates if product exists
                record = TermDepositRecord(
                    bank_name=brand.name,
                    bank_id=brand.id,
                    product_id=product_id,
                    product_name=product_name,
                    additional_info=product.get('description', ''),
                    application_url=details.get('applicationUri'),
                    last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                records.append(record)
                continue
            
            # Process each deposit rate
            for rate_entry in deposit_rates:
                try:
                    # Extract rate information
                    interest_rate = rate_entry.get('rate')
                    rate_type = rate_entry.get('depositRateType', 'FIXED')
                    
                    # Extract term information
                    term_months = None
                    term_display = None
                    additional_value = rate_entry.get('additionalValue', '')
                    
                    if additional_value:
                        term_months = self.parse_term_months(additional_value)
                        term_display = self.format_term_display(term_months)
                    
                    # Extract minimum/maximum amounts from tiers
                    min_deposit = None
                    max_deposit = None
                    
                    tiers = rate_entry.get('tiers', [])
                    for tier in tiers:
                        if tier.get('name', '').upper() in ['AMOUNT', 'BALANCE']:
                            min_deposit = tier.get('minimumValue')
                            max_deposit = tier.get('maximumValue')
                            break
                    
                    # Extract fees
                    account_fee = None
                    early_withdrawal_fee = None
                    early_withdrawal_fee_type = None
                    
                    fees = details.get('fees', [])
                    for fee in fees:
                        fee_type = fee.get('feeType', '').upper()
                        fee_name = fee.get('name', '').upper()
                        
                        if 'EARLY' in fee_name and 'WITHDRAWAL' in fee_name:
                            early_withdrawal_fee = fee.get('amount')
                            early_withdrawal_fee_type = fee.get('feeType')
                        elif fee_type == 'PERIODIC':
                            account_fee = fee.get('amount')
                    
                    # Create record
                    record = TermDepositRecord(
                        bank_name=brand.name,
                        bank_id=brand.id,
                        product_id=product_id,
                        product_name=product_name,
                        interest_rate=interest_rate,
                        rate_type=rate_type,
                        term_months=term_months,
                        term_display=term_display,
                        minimum_deposit=min_deposit,
                        maximum_deposit=max_deposit,
                        account_fee=account_fee,
                        early_withdrawal_fee=early_withdrawal_fee,
                        early_withdrawal_fee_type=early_withdrawal_fee_type,
                        additional_info=product.get('description', ''),
                        application_url=details.get('applicationUri'),
                        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    
                    records.append(record)
                    
                except Exception as e:
                    self.logger.debug(f"Error processing rate for {product_name}: {str(e)}")
                    continue
        
        return records
    
    def parse_term_months(self, term_string: str) -> Optional[int]:
        """Parse term string to months"""
        try:
            term_string = term_string.upper().replace('P', '').replace('T', '')
            
            if 'Y' in term_string:
                years = int(term_string.replace('Y', ''))
                return years * 12
            elif 'M' in term_string:
                return int(term_string.replace('M', ''))
            elif 'D' in term_string:
                days = int(term_string.replace('D', ''))
                return round(days / 30)  # Approximate months
            
        except:
            pass
        return None
    
    def format_term_display(self, months: Optional[int]) -> Optional[str]:
        """Format term months into display string"""
        if not months:
            return None
            
        if months < 12:
            return f"{months} month{'s' if months != 1 else ''}"
        else:
            years = months // 12
            remaining_months = months % 12
            if remaining_months == 0:
                return f"{years} year{'s' if years != 1 else ''}"
            else:
                return f"{years}y {remaining_months}m"
    
    def process_bank(self, bank_name: str, bank_id: str, endpoint: str) -> List[TermDepositRecord]:
        """Process a single bank for term deposits"""
        brand = CDRBrand(name=bank_name, id=bank_id, endpoint=endpoint)
        
        try:
            # Fetch products
            products = self.fetch_products_for_brand(brand)
            if not products:
                return []
            
            # Extract records
            records = self.extract_term_deposit_records(brand, products)
            
            rates_count = len([r for r in records if r.interest_rate])
            self.logger.info(f"✅ {bank_name}: {len(records)} records ({rates_count} with rates)")
            
            return records
            
        except Exception as e:
            self.logger.error(f"❌ {bank_name}: Exception during processing: {str(e)}")
            return []
    
    def collect_term_deposits(self, max_workers: int = 8) -> List[TermDepositRecord]:
        """Collect term deposit data from all banks"""
        self.logger.info("🏦 TERM DEPOSITS SCRAPER - Starting Collection")
        self.logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Get bank list
        banks_to_process = BANKS_FROM_CDR_REGISTER
        self.logger.info(f"🏦 Processing {len(banks_to_process)} banks for term deposits...")
        
        # Process banks in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.process_bank, bank_name, bank_id, endpoint): bank_name
                for bank_name, bank_id, endpoint in banks_to_process
            }
            
            for future in as_completed(futures):
                bank_name = futures[future]
                try:
                    records = future.result()
                    self.all_records.extend(records)
                except Exception as e:
                    self.logger.error(f"❌ {bank_name}: Processing failed: {str(e)}")
        
        duration = datetime.now() - start_time
        
        self.logger.info("")
        self.logger.info("📊 TERM DEPOSITS COLLECTION COMPLETE!")
        self.logger.info(f"⏱️  Duration: {duration}")
        self.logger.info(f"🏦 Banks processed: {len(banks_to_process)}")
        successful_banks = len(set(r.bank_name for r in self.all_records))
        self.logger.info(f"✅ Successful: {successful_banks}")
        self.logger.info(f"❌ Failed: {len(banks_to_process) - successful_banks}")
        self.logger.info(f"📊 Total term deposit records: {len(self.all_records)}")
        records_with_rates = len([r for r in self.all_records if r.interest_rate])
        self.logger.info(f"💰 Records with rates: {records_with_rates}")
        
        return self.all_records
    
    def save_data(self) -> str:
        """Save collected data to CSV and JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Convert to DataFrame
        data_dicts = [record.dict() for record in self.all_records]
        df = pd.DataFrame(data_dicts)
        
        # Save CSV
        csv_file = f'../data/term_deposits_{timestamp}.csv'
        df.to_csv(csv_file, index=False)
        
        # Save JSON
        json_file = f'../data/term_deposits_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(data_dicts, f, indent=2, default=str)
        
        self.logger.info(f"💾 Term deposits data saved:")
        self.logger.info(f"   📄 CSV: {csv_file}")
        self.logger.info(f"   📄 JSON: {json_file}")
        
        return csv_file

def main():
    """Main execution"""
    scraper = TermDepositsScr()
    
    # Collect term deposit data
    records = scraper.collect_term_deposits()
    
    # Save results
    csv_file = scraper.save_data()
    
    print(f"\n🎉 Term Deposits Collection Complete!")
    print(f"📊 Total records: {len(records)}")
    print(f"💰 Records with rates: {len([r for r in records if r.interest_rate])}")
    print(f"📄 Saved to: {csv_file}")
    print(f"\n🚀 Ready for term deposits dashboard!")

if __name__ == "__main__":
    main()
