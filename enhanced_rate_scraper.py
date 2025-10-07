#!/usr/bin/env python3
"""
Enhanced Real-Time Banking Tracker - Individual Rate Records
Extracts ALL rate variations as individual records (Luke Prior style)
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
    ]

@dataclass
class LendingRateRecord:
    """Individual lending rate record"""
    brand_name: str
    brand_id: str
    product_id: str
    product_name: str
    rate_type: str  # VARIABLE, FIXED, etc.
    rate_value: float
    comparison_rate: Optional[float]
    
    # Rate specifics
    fixed_term_months: Optional[int]
    loan_purpose: str  # OWNER_OCCUPIED, INVESTMENT
    repayment_type: str  # PRINCIPAL_AND_INTEREST, INTEREST_ONLY
    
    # LVR and tiers
    lvr_min: Optional[float]
    lvr_max: Optional[float]
    tier_name: Optional[str]
    tier_min: Optional[float]
    tier_max: Optional[float]
    
    # Features
    offset_available: bool
    redraw_available: bool
    
    # Additional info
    additional_info: Optional[str]
    application_url: Optional[str]
    last_updated: str

class EnhancedRateScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Enhanced-Rate-Scraper/1.0',
            'Accept': 'application/json'
        })
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.rate_records: List[LendingRateRecord] = []
        self.success_count = 0
        self.error_count = 0
        self.errors = {}
        
    def fetch_products_basic(self, bank_name: str, bank_id: str, endpoint: str) -> List[Dict]:
        """Fetch basic product list"""
        api_versions = ['3', '4', '2', '1']
        
        for version in api_versions:
            try:
                headers = {'x-v': version}
                response = self.session.get(endpoint, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    products = data.get('data', {}).get('products', [])
                    
                    # Filter for residential mortgages
                    mortgage_products = [
                        product for product in products 
                        if product.get('productCategory') == 'RESIDENTIAL_MORTGAGES'
                    ]
                    
                    if mortgage_products:
                        self.logger.info(f"✅ {bank_name}: Found {len(mortgage_products)} mortgage products (v{version})")
                        return mortgage_products
                        
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
        """Fetch detailed product information including lending rates"""
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
                           basic_product: Dict, detailed_product: Optional[Dict]) -> List[LendingRateRecord]:
        """Extract all rate variations as individual records"""
        records = []
        
        # Basic product info
        product_id = basic_product.get('productId', '')
        product_name = basic_product.get('name', 'Unknown Product')
        
        # Features from basic or detailed product
        offset_available = False
        redraw_available = False
        application_url = basic_product.get('applicationUri', '')
        last_updated = datetime.now().isoformat()
        
        if detailed_product:
            # Get features
            features = detailed_product.get('features', [])
            for feature in features:
                feature_type = feature.get('featureType', '')
                if feature_type == 'OFFSET':
                    offset_available = True
                elif feature_type == 'REDRAW':
                    redraw_available = True
            
            # Get lending rates
            lending_rates = detailed_product.get('lendingRates', [])
            
            if lending_rates:
                for rate in lending_rates:
                    record = self.create_rate_record(
                        bank_name, bank_id, product_id, product_name,
                        rate, offset_available, redraw_available,
                        application_url, last_updated
                    )
                    if record:
                        records.append(record)
            else:
                # No detailed rates, create basic record
                record = LendingRateRecord(
                    brand_name=bank_name,
                    brand_id=bank_id,
                    product_id=product_id,
                    product_name=product_name,
                    rate_type="UNKNOWN",
                    rate_value=0.0,
                    comparison_rate=None,
                    fixed_term_months=None,
                    loan_purpose="Not Specified",
                    repayment_type="Not Specified",
                    lvr_min=None,
                    lvr_max=None,
                    tier_name=None,
                    tier_min=None,
                    tier_max=None,
                    offset_available=offset_available,
                    redraw_available=redraw_available,
                    additional_info=None,
                    application_url=application_url,
                    last_updated=last_updated
                )
                records.append(record)
        else:
            # No detailed product data, create basic record
            record = LendingRateRecord(
                brand_name=bank_name,
                brand_id=bank_id,
                product_id=product_id,
                product_name=product_name,
                rate_type="UNKNOWN",
                rate_value=0.0,
                comparison_rate=None,
                fixed_term_months=None,
                loan_purpose="Not Specified",
                repayment_type="Not Specified",
                lvr_min=None,
                lvr_max=None,
                tier_name=None,
                tier_min=None,
                tier_max=None,
                offset_available=offset_available,
                redraw_available=redraw_available,
                additional_info=None,
                application_url=application_url,
                last_updated=last_updated
            )
            records.append(record)
        
        return records
    
    def create_rate_record(self, bank_name: str, bank_id: str, product_id: str, 
                          product_name: str, rate_data: Dict, offset_available: bool,
                          redraw_available: bool, application_url: str, 
                          last_updated: str) -> Optional[LendingRateRecord]:
        """Create a rate record from lending rate data"""
        try:
            rate_type = rate_data.get('lendingRateType', 'UNKNOWN')
            rate_value = float(rate_data.get('rate', 0.0))
            comparison_rate = rate_data.get('comparisonRate')
            if comparison_rate:
                comparison_rate = float(comparison_rate)
            
            # Extract additional rate details
            additional_value = rate_data.get('additionalValue', '')
            additional_info = rate_data.get('additionalInfo', '')
            
            # Parse fixed term from additionalValue (like "P1Y", "P2Y", etc.)
            fixed_term_months = None
            if rate_type == 'FIXED' and additional_value:
                fixed_term_months = self.parse_period_to_months(additional_value)
            
            # Get loan purpose and repayment type
            loan_purpose = rate_data.get('loanPurpose', 'Not Specified')
            repayment_type = rate_data.get('repaymentType', 'Not Specified')
            
            # Handle tiers (LVR ranges)
            tiers = rate_data.get('tiers', [])
            if tiers:
                # Create a record for each tier
                records = []
                for tier in tiers:
                    tier_record = LendingRateRecord(
                        brand_name=bank_name,
                        brand_id=bank_id,
                        product_id=product_id,
                        product_name=product_name,
                        rate_type=rate_type,
                        rate_value=rate_value,
                        comparison_rate=comparison_rate,
                        fixed_term_months=fixed_term_months,
                        loan_purpose=loan_purpose,
                        repayment_type=repayment_type,
                        lvr_min=tier.get('minimumValue'),
                        lvr_max=tier.get('maximumValue'),
                        tier_name=tier.get('name'),
                        tier_min=tier.get('minimumValue'),
                        tier_max=tier.get('maximumValue'),
                        offset_available=offset_available,
                        redraw_available=redraw_available,
                        additional_info=additional_info,
                        application_url=application_url,
                        last_updated=last_updated
                    )
                    records.append(tier_record)
                return records[0] if records else None  # Return first for simplicity
            else:
                # Single record without tiers
                return LendingRateRecord(
                    brand_name=bank_name,
                    brand_id=bank_id,
                    product_id=product_id,
                    product_name=product_name,
                    rate_type=rate_type,
                    rate_value=rate_value,
                    comparison_rate=comparison_rate,
                    fixed_term_months=fixed_term_months,
                    loan_purpose=loan_purpose,
                    repayment_type=repayment_type,
                    lvr_min=None,
                    lvr_max=None,
                    tier_name=None,
                    tier_min=None,
                    tier_max=None,
                    offset_available=offset_available,
                    redraw_available=redraw_available,
                    additional_info=additional_info,
                    application_url=application_url,
                    last_updated=last_updated
                )
                
        except Exception as e:
            self.logger.warning(f"Error creating rate record: {e}")
            return None
    
    def parse_period_to_months(self, period_str: str) -> Optional[int]:
        """Parse ISO 8601 period to months (P1Y = 12, P2Y = 24, etc.)"""
        try:
            if period_str.startswith('P') and 'Y' in period_str:
                years = int(period_str.replace('P', '').replace('Y', ''))
                return years * 12
            elif period_str.startswith('P') and 'M' in period_str:
                months = int(period_str.replace('P', '').replace('M', ''))
                return months
        except:
            pass
        return None
    
    def process_bank(self, bank_name: str, bank_id: str, endpoint: str) -> List[LendingRateRecord]:
        """Process a single bank and extract all rate records"""
        records = []
        
        try:
            self.logger.info(f"🏦 {bank_name}: Processing...")
            
            # Fetch basic products
            basic_products = self.fetch_products_basic(bank_name, bank_id, endpoint)
            
            if not basic_products:
                self.error_count += 1
                self.errors[bank_name] = "No mortgage products found"
                return records
            
            # Process each product for detailed rates
            for basic_product in basic_products:
                product_id = basic_product.get('productId', '')
                
                # Fetch detailed product info
                detailed_product = self.fetch_product_details(bank_name, endpoint, product_id)
                
                # Extract rate records
                product_records = self.extract_rate_records(
                    bank_name, bank_id, endpoint, basic_product, detailed_product
                )
                
                records.extend(product_records)
            
            if records:
                self.success_count += 1
                rate_count = len([r for r in records if r.rate_value > 0])
                self.logger.info(f"✅ {bank_name}: {len(records)} records ({rate_count} with rates)")
            else:
                self.error_count += 1
                self.errors[bank_name] = "No rate records extracted"
                
        except Exception as e:
            self.error_count += 1
            self.errors[bank_name] = str(e)
            self.logger.error(f"❌ {bank_name}: {str(e)}")
        
        return records
    
    def collect_all_rates(self, max_workers: int = 10) -> List[LendingRateRecord]:
        """Collect all rate records from all banks"""
        self.logger.info("🚀 Enhanced Rate Scraper - Individual Rate Records")
        self.logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Use all banks for comprehensive data collection
        banks_to_process = BANKS_FROM_CDR_REGISTER  # All 120 banks
        
        self.logger.info(f"🏦 Processing {len(banks_to_process)} banks for detailed rates...")
        
        # Process banks in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.process_bank, bank_name, bank_id, endpoint): bank_name
                for bank_name, bank_id, endpoint in banks_to_process
            }
            
            for future in as_completed(futures):
                bank_name = futures[future]
                try:
                    bank_records = future.result()
                    self.rate_records.extend(bank_records)
                except Exception as e:
                    self.logger.error(f"❌ {bank_name}: {str(e)}")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        self.logger.info(f"\n📊 COLLECTION COMPLETE!")
        self.logger.info(f"⏱️  Duration: {duration}")
        self.logger.info(f"🏦 Banks processed: {len(banks_to_process)}")
        self.logger.info(f"✅ Successful: {self.success_count}")
        self.logger.info(f"❌ Failed: {self.error_count}")
        self.logger.info(f"📊 Total rate records: {len(self.rate_records)}")
        
        # Count records with actual rates
        records_with_rates = len([r for r in self.rate_records if r.rate_value > 0])
        self.logger.info(f"💰 Records with rates: {records_with_rates}")
        
        return self.rate_records
    
    def save_rate_records(self, filename: str = "enhanced_mortgage_rates"):
        """Save rate records to CSV and JSON"""
        if not self.rate_records:
            self.logger.warning("No rate records to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as CSV
        csv_file = f"{filename}_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Bank Name', 'Bank ID', 'Product ID', 'Product Name',
                'Rate Type', 'Rate (%)', 'Comparison Rate (%)',
                'Fixed Term (Months)', 'Loan Purpose', 'Repayment Type',
                'LVR Min (%)', 'LVR Max (%)', 'Tier Name', 'Tier Min', 'Tier Max',
                'Offset Available', 'Redraw Available', 'Additional Info',
                'Application URL', 'Last Updated'
            ])
            
            # Data rows
            for record in self.rate_records:
                writer.writerow([
                    record.brand_name, record.brand_id, record.product_id, record.product_name,
                    record.rate_type, 
                    f"{record.rate_value * 100:.3f}" if record.rate_value > 0 else '',
                    f"{record.comparison_rate * 100:.3f}" if record.comparison_rate else '',
                    record.fixed_term_months,
                    record.loan_purpose, record.repayment_type,
                    record.lvr_min, record.lvr_max, record.tier_name, record.tier_min, record.tier_max,
                    'Y' if record.offset_available else 'N',
                    'Y' if record.redraw_available else 'N',
                    record.additional_info, record.application_url, record.last_updated
                ])
        
        # Save as JSON
        json_file = f"{filename}_{timestamp}.json"
        json_data = []
        for record in self.rate_records:
            json_data.append({
                'bankName': record.brand_name,
                'bankId': record.brand_id,
                'productId': record.product_id,
                'productName': record.product_name,
                'rateType': record.rate_type,
                'rateValue': record.rate_value,
                'comparisonRate': record.comparison_rate,
                'fixedTermMonths': record.fixed_term_months,
                'loanPurpose': record.loan_purpose,
                'repaymentType': record.repayment_type,
                'lvrMin': record.lvr_min,
                'lvrMax': record.lvr_max,
                'tierName': record.tier_name,
                'tierMin': record.tier_min,
                'tierMax': record.tier_max,
                'offsetAvailable': record.offset_available,
                'redrawAvailable': record.redraw_available,
                'additionalInfo': record.additional_info,
                'applicationUrl': record.application_url,
                'lastUpdated': record.last_updated
            })
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Rate records saved:")
        self.logger.info(f"   📄 CSV: {csv_file}")
        self.logger.info(f"   📄 JSON: {json_file}")

def main():
    """Main execution"""
    scraper = EnhancedRateScraper()
    
    # Collect all rate records
    rate_records = scraper.collect_all_rates()
    
    # Save results
    scraper.save_rate_records()
    
    print(f"\n🎉 Enhanced Rate Collection Complete!")
    print(f"📊 Total individual rate records: {len(rate_records)}")
    print(f"💰 Records with actual rates: {len([r for r in rate_records if r.rate_value > 0])}")

if __name__ == "__main__":
    main()
