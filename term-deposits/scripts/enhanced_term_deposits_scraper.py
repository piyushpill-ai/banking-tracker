#!/usr/bin/env python3
"""
Enhanced Term Deposits Scraper - Individual Rate Records
========================================================

Extracts ALL term deposit rate variations as individual records.
Similar to enhanced_rate_scraper.py but for term deposits.

Collects variant-level data:
- Different term lengths (3m, 6m, 1y, 2y, etc.)  
- Deposit amount tiers ($5K, $50K, $100K+)
- Promotional vs standard rates
- New money vs rollover rates
- Interest payment frequencies

Author: AI Assistant
Date: September 2025
"""

import requests
import json
import time
import csv
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import os
import sys

# Add parent directory to path to import bank list
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the comprehensive bank list
try:
    from luke_prior_bank_list_1758106523 import BANKS_FROM_CDR_REGISTER
except ImportError:
    print("⚠️ Could not import bank list, using fallback")
    BANKS_FROM_CDR_REGISTER = [
        ("ANZ", "anz", "https://api.anz/cds-au/v1/banking/products"),
        ("CommBank", "commbank", "https://api.commbank.com.au/public/cds-au/v1/banking/products"),
        ("NATIONAL AUSTRALIA BANK", "nab", "https://openbank.api.nab.com.au/cds-au/v1/banking/products"),
        ("Westpac", "westpac", "https://digital-api.westpac.com.au/cds-au/v1/banking/products"),
        ("UBank", "ubank", "https://public.cdr-api.86400.com.au/cds-au/v1/banking/products"),
    ]

@dataclass
class TermDepositRateRecord:
    """Individual term deposit rate record"""
    # Bank Information
    bank_name: str
    bank_id: str
    product_id: str
    product_name: str
    
    # Rate Information
    interest_rate: Optional[float]
    rate_type: str  # FIXED, VARIABLE, BONUS
    base_rate: Optional[float]
    bonus_rate: Optional[float]
    
    # Term Information
    term_months: Optional[int]
    term_display: Optional[str]
    term_unit: Optional[str]  # MONTH, DAY, YEAR
    
    # Deposit Tiers
    tier_name: Optional[str]
    tier_minimum: Optional[float]
    tier_maximum: Optional[float]
    minimum_deposit: Optional[float]
    maximum_deposit: Optional[float]
    
    # Interest Payment
    calculation_frequency: Optional[str]  # How often interest calculated
    application_frequency: Optional[str]  # How often interest paid
    payment_frequency: Optional[str]     # Alternative field name
    
    # Conditions
    introductory_rate: bool
    promotional_rate: bool
    additional_value: Optional[str]  # Promo conditions, etc.
    
    # Additional Information
    additional_info: Optional[str]
    eligibility_criteria: Optional[str]
    application_url: Optional[str]
    last_updated: str

class EnhancedTermDepositsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Enhanced-TermDeposits-Scraper/1.0',
            'Accept': 'application/json'
        })
        
        # Setup logging to ../data/
        log_file = f'../data/enhanced_term_deposits_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.rate_records: List[TermDepositRateRecord] = []
        self.success_count = 0
        self.error_count = 0
        self.errors = {}
    
    def _is_valid_rate(self, rate) -> bool:
        """Check if rate is a valid numeric value > 0"""
        try:
            if rate is None:
                return False
            rate_float = float(rate)
            return rate_float > 0
        except (ValueError, TypeError):
            return False
        
    def fetch_products_basic(self, bank_name: str, bank_id: str, endpoint: str) -> List[Dict]:
        """Fetch basic product list for term deposits"""
        api_versions = ['3', '4', '2', '1']
        
        for version in api_versions:
            try:
                headers = {'x-v': version}
                response = self.session.get(endpoint, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    products = data.get('data', {}).get('products', [])
                    
                    # Filter for term deposits
                    term_deposit_products = [
                        product for product in products 
                        if product.get('productCategory') == 'TERM_DEPOSITS'
                    ]
                    
                    if term_deposit_products:
                        self.logger.info(f"✅ {bank_name}: Found {len(term_deposit_products)} term deposit products (v{version})")
                        return term_deposit_products
                        
                elif response.status_code == 406:
                    continue  # Try next version
                else:
                    self.logger.warning(f"⚠️ {bank_name}: HTTP {response.status_code} with v{version}")
                    continue
                    
            except Exception as e:
                self.logger.warning(f"⚠️ {bank_name}: Error with v{version}: {str(e)}")
                continue
        
        self.logger.error(f"❌ {bank_name}: All product fetch attempts failed")
        return []
    
    def fetch_product_details(self, bank_name: str, endpoint: str, product_id: str) -> Optional[Dict]:
        """Fetch detailed product information including deposit rates"""
        base_endpoint = endpoint.rstrip('/banking/products')
        detail_endpoint = f"{base_endpoint}/banking/products/{product_id}"
        
        api_versions = ['3', '4', '2', '1']
        
        for version in api_versions:
            try:
                headers = {'x-v': version}
                response = self.session.get(detail_endpoint, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    product_detail = data.get('data', {})
                    
                    if product_detail:
                        return product_detail
                        
                elif response.status_code == 404:
                    break  # Product not found, don't try other versions
                elif response.status_code == 406:
                    continue  # Try next version
                    
            except Exception as e:
                continue
        
        return None
    
    def extract_rate_records(self, bank_name: str, bank_id: str, endpoint: str, 
                           basic_product: Dict, detailed_product: Optional[Dict]) -> List[TermDepositRateRecord]:
        """Extract all rate variations as individual records"""
        records = []
        
        # Basic product info
        product_id = basic_product.get('productId', '')
        product_name = basic_product.get('name', 'Unknown Product')
        application_url = basic_product.get('applicationUri', '')
        last_updated = datetime.now().isoformat()
        
        if detailed_product:
            # Get deposit rates array
            deposit_rates = detailed_product.get('depositRates', [])
            
            if deposit_rates:
                for rate in deposit_rates:
                    record = self.create_rate_record(
                        bank_name, bank_id, product_id, product_name,
                        rate, application_url, last_updated
                    )
                    if record:
                        records.append(record)
            else:
                # No detailed rates, create basic record
                record = TermDepositRateRecord(
                    bank_name=bank_name,
                    bank_id=bank_id,
                    product_id=product_id,
                    product_name=product_name,
                    interest_rate=None,
                    rate_type="UNKNOWN",
                    base_rate=None,
                    bonus_rate=None,
                    term_months=None,
                    term_display="Not Specified",
                    term_unit=None,
                    tier_name=None,
                    tier_minimum=None,
                    tier_maximum=None,
                    minimum_deposit=None,
                    maximum_deposit=None,
                    calculation_frequency=None,
                    application_frequency=None,
                    payment_frequency=None,
                    introductory_rate=False,
                    promotional_rate=False,
                    additional_value=None,
                    additional_info=basic_product.get('description', ''),
                    eligibility_criteria=None,
                    application_url=application_url,
                    last_updated=last_updated
                )
                records.append(record)
        else:
            # No detailed product data available
            record = TermDepositRateRecord(
                bank_name=bank_name,
                bank_id=bank_id,
                product_id=product_id,
                product_name=product_name,
                interest_rate=None,
                rate_type="UNKNOWN",
                base_rate=None,
                bonus_rate=None,
                term_months=None,
                term_display="Not Specified",
                term_unit=None,
                tier_name=None,
                tier_minimum=None,
                tier_maximum=None,
                minimum_deposit=None,
                maximum_deposit=None,
                calculation_frequency=None,
                application_frequency=None,
                payment_frequency=None,
                introductory_rate=False,
                promotional_rate=False,
                additional_value=None,
                additional_info=basic_product.get('description', ''),
                eligibility_criteria=None,
                application_url=application_url,
                last_updated=last_updated
            )
            records.append(record)
        
        return records
    
    def create_rate_record(self, bank_name: str, bank_id: str, product_id: str, 
                          product_name: str, rate_data: Dict, application_url: str, 
                          last_updated: str) -> Optional[TermDepositRateRecord]:
        """Create a single rate record from deposit rate data"""
        try:
            # Extract rate information
            raw_rate = rate_data.get('rate')
            interest_rate = None
            if raw_rate is not None:
                try:
                    interest_rate = float(raw_rate)
                except (ValueError, TypeError):
                    pass
            rate_type = rate_data.get('depositRateType', 'UNKNOWN')
            
            # Parse rate components
            base_rate = None
            bonus_rate = None
            
            # Some banks separate base and bonus rates
            if rate_type == 'BONUS':
                bonus_rate = interest_rate
            else:
                base_rate = interest_rate
            
            # Extract term information
            term_months = None
            term_display = "Not Specified"
            term_unit = None
            
            additional_value = rate_data.get('additionalValue', '')
            if additional_value:
                # Parse term from additionalValue (e.g., "P3M" = 3 months, "P1Y" = 1 year)
                if additional_value.startswith('P'):
                    try:
                        if 'M' in additional_value:
                            term_months = int(additional_value.replace('P', '').replace('M', ''))
                            term_display = f"{term_months} month{'s' if term_months != 1 else ''}"
                            term_unit = 'MONTH'
                        elif 'Y' in additional_value:
                            years = int(additional_value.replace('P', '').replace('Y', ''))
                            term_months = years * 12
                            term_display = f"{years} year{'s' if years != 1 else ''}"
                            term_unit = 'YEAR'
                        elif 'D' in additional_value:
                            days = int(additional_value.replace('P', '').replace('D', ''))
                            term_months = days // 30  # Approximate
                            term_display = f"{days} days"
                            term_unit = 'DAY'
                    except (ValueError, AttributeError):
                        pass
            
            # Extract tier information
            tier_name = None
            tier_minimum = None
            tier_maximum = None
            minimum_deposit = None
            maximum_deposit = None
            
            # Check for tiers in rate data
            tiers = rate_data.get('tiers', [])
            if tiers:
                # Use the first tier for this record
                tier = tiers[0]
                tier_name = tier.get('name')
                tier_minimum = tier.get('minimumValue')
                tier_maximum = tier.get('maximumValue')
                
                # Set deposit limits from tier
                minimum_deposit = tier_minimum
                maximum_deposit = tier_maximum
            
            # Extract frequency information
            calculation_frequency = rate_data.get('calculationFrequency')
            application_frequency = rate_data.get('applicationFrequency')
            payment_frequency = rate_data.get('paymentFrequency') or application_frequency
            
            # Check for promotional/introductory rates
            introductory_rate = rate_type in ['INTRODUCTORY', 'PROMOTIONAL']
            promotional_rate = 'PROMOTIONAL' in rate_type or 'PROMO' in (additional_value or '').upper()
            
            # Additional information
            additional_info = rate_data.get('additionalInfo', '')
            
            return TermDepositRateRecord(
                bank_name=bank_name,
                bank_id=bank_id,
                product_id=product_id,
                product_name=product_name,
                interest_rate=interest_rate,
                rate_type=rate_type,
                base_rate=base_rate,
                bonus_rate=bonus_rate,
                term_months=term_months,
                term_display=term_display,
                term_unit=term_unit,
                tier_name=tier_name,
                tier_minimum=tier_minimum,
                tier_maximum=tier_maximum,
                minimum_deposit=minimum_deposit,
                maximum_deposit=maximum_deposit,
                calculation_frequency=calculation_frequency,
                application_frequency=application_frequency,
                payment_frequency=payment_frequency,
                introductory_rate=introductory_rate,
                promotional_rate=promotional_rate,
                additional_value=additional_value,
                additional_info=additional_info,
                eligibility_criteria=None,
                application_url=application_url,
                last_updated=last_updated
            )
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error creating rate record: {str(e)}")
            return None
    
    def process_bank(self, bank_name: str, bank_id: str, endpoint: str) -> List[TermDepositRateRecord]:
        """Process a single bank and extract all rate records"""
        records = []
        
        try:
            self.logger.info(f"🏦 {bank_name}: Processing term deposits...")
            
            # Step 1: Get basic product list
            basic_products = self.fetch_products_basic(bank_name, bank_id, endpoint)
            
            if not basic_products:
                return records
            
            # Step 2: Process each product for detailed rates
            for product in basic_products:
                product_id = product.get('productId', '')
                
                # Get detailed product information
                detailed_product = self.fetch_product_details(bank_name, endpoint, product_id)
                
                # Extract rate records
                product_records = self.extract_rate_records(
                    bank_name, bank_id, endpoint, product, detailed_product
                )
                records.extend(product_records)
                
                # Small delay between requests
                time.sleep(0.1)
            
            # Summary
            rates_with_values = [r for r in records if r.interest_rate and self._is_valid_rate(r.interest_rate)]
            self.logger.info(f"✅ {bank_name}: {len(records)} records ({len(rates_with_values)} with rates)")
            
            self.success_count += 1
            
        except Exception as e:
            self.logger.error(f"❌ {bank_name}: {str(e)}")
            self.errors[bank_name] = str(e)
            self.error_count += 1
        
        return records
    
    def save_data(self, records: List[TermDepositRateRecord]):
        """Save all collected records to CSV and JSON"""
        if not records:
            self.logger.warning("⚠️ No records to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert to dictionaries
        data_dicts = []
        for record in records:
            # Convert dataclass to dict
            record_dict = {
                'bank_name': record.bank_name,
                'bank_id': record.bank_id,
                'product_id': record.product_id,
                'product_name': record.product_name,
                'interest_rate': record.interest_rate,
                'rate_type': record.rate_type,
                'base_rate': record.base_rate,
                'bonus_rate': record.bonus_rate,
                'term_months': record.term_months,
                'term_display': record.term_display,
                'term_unit': record.term_unit,
                'tier_name': record.tier_name,
                'tier_minimum': record.tier_minimum,
                'tier_maximum': record.tier_maximum,
                'minimum_deposit': record.minimum_deposit,
                'maximum_deposit': record.maximum_deposit,
                'calculation_frequency': record.calculation_frequency,
                'application_frequency': record.application_frequency,
                'payment_frequency': record.payment_frequency,
                'introductory_rate': record.introductory_rate,
                'promotional_rate': record.promotional_rate,
                'additional_value': record.additional_value,
                'additional_info': record.additional_info,
                'eligibility_criteria': record.eligibility_criteria,
                'application_url': record.application_url,
                'last_updated': record.last_updated
            }
            data_dicts.append(record_dict)
        
        # Save to CSV
        csv_file = f'../data/enhanced_term_deposits_{timestamp}.csv'
        
        import pandas as pd
        df = pd.DataFrame(data_dicts)
        df.to_csv(csv_file, index=False)
        
        # Save to JSON
        json_file = f'../data/enhanced_term_deposits_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(data_dicts, f, indent=2, default=str)
        
        self.logger.info(f"💾 Enhanced term deposits data saved:")
        self.logger.info(f"   📄 CSV: {csv_file}")
        self.logger.info(f"   📄 JSON: {json_file}")
    
    def run_enhanced_collection(self, max_banks: Optional[int] = None):
        """Run the enhanced term deposits collection"""
        start_time = datetime.now()
        self.logger.info("🚀 Starting Enhanced Term Deposits Collection...")
        self.logger.info(f"📊 Target: {len(BANKS_FROM_CDR_REGISTER)} banks")
        
        # Limit banks for testing if specified
        banks_to_process = BANKS_FROM_CDR_REGISTER[:max_banks] if max_banks else BANKS_FROM_CDR_REGISTER
        
        # Process banks in parallel
        all_records = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_bank = {
                executor.submit(self.process_bank, bank[0], bank[1], bank[2]): bank
                for bank in banks_to_process
            }
            
            for future in as_completed(future_to_bank):
                bank = future_to_bank[future]
                try:
                    records = future.result()
                    all_records.extend(records)
                except Exception as e:
                    self.logger.error(f"❌ {bank[0]}: {str(e)}")
        
        # Save all data
        self.save_data(all_records)
        
        # Final summary
        duration = datetime.now() - start_time
        rates_with_values = [r for r in all_records if r.interest_rate and self._is_valid_rate(r.interest_rate)]
        
        self.logger.info("")
        self.logger.info("📊 ENHANCED TERM DEPOSITS COLLECTION COMPLETE!")
        self.logger.info(f"⏱️  Duration: {duration}")
        self.logger.info(f"🏦 Banks processed: {len(banks_to_process)}")
        self.logger.info(f"✅ Successful: {self.success_count}")
        self.logger.info(f"❌ Failed: {self.error_count}")
        self.logger.info(f"📊 Total rate records: {len(all_records)}")
        self.logger.info(f"💰 Records with rates: {len(rates_with_values)}")
        
        print(f"\n🎉 Enhanced Term Deposits Collection Complete!")
        print(f"📊 Total rate records: {len(all_records)}")
        print(f"💰 Records with rates: {len(rates_with_values)}")
        print(f"📄 Saved to: ../data/enhanced_term_deposits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        print(f"🚀 Ready for enhanced dashboard!")

def main():
    """Main execution function"""
    scraper = EnhancedTermDepositsScraper()
    
    # Run collection for all banks (or limit for testing)
    # scraper.run_enhanced_collection(max_banks=10)  # Test with 10 banks
    scraper.run_enhanced_collection()  # Full collection

if __name__ == "__main__":
    main()
