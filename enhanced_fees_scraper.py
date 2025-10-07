#!/usr/bin/env python3
"""
Enhanced Fees Scraper - Collects detailed rate AND fees information
Adds the missing fee fields requested for the dashboard
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
class MortgageRateWithFees:
    """Complete mortgage rate record with fees information"""
    # Basic info
    brand_name: str
    brand_id: str
    product_id: str
    product_name: str
    
    # Rate info
    rate_type: str
    rate_value: float
    comparison_rate: Optional[float]
    fixed_term_months: Optional[int]
    loan_purpose: str
    repayment_type: str
    
    # LVR and tiers
    lvr_min: Optional[float]
    lvr_max: Optional[float]
    tier_name: Optional[str]
    
    # Features
    offset_available: bool
    redraw_available: bool
    
    # Fees (NEW)
    application_fee: Optional[float]
    application_fee_frequency: Optional[str]
    offset_fee: Optional[float]
    offset_fee_frequency: Optional[str]
    annual_fee: Optional[float]
    monthly_fee: Optional[float]
    exit_fee: Optional[float]
    redraw_fee: Optional[float]
    other_ongoing_fees: Optional[str]
    
    # Additional info
    additional_info: Optional[str]
    application_url: Optional[str]
    last_updated: str

class EnhancedFeesScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Enhanced-Fees-Scraper/1.0',
            'Accept': 'application/json'
        })
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.rate_records: List[MortgageRateWithFees] = []
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
                    continue
                else:
                    continue
                    
            except Exception as e:
                continue
        
        return []
    
    def fetch_product_details(self, bank_name: str, endpoint: str, product_id: str) -> Optional[Dict]:
        """Fetch detailed product information including lending rates AND fees"""
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
                    break
                elif response.status_code == 406:
                    continue
                    
            except Exception as e:
                continue
        
        return None
    
    def extract_fees_info(self, detailed_product: Dict) -> Dict[str, Any]:
        """Extract comprehensive fees information from product details"""
        fees_info = {
            'application_fee': None,
            'application_fee_frequency': None,
            'offset_fee': None,
            'offset_fee_frequency': None,
            'annual_fee': None,
            'monthly_fee': None,
            'exit_fee': None,
            'redraw_fee': None,
            'other_ongoing_fees': None
        }
        
        fees = detailed_product.get('fees', [])
        ongoing_fees = []
        
        for fee in fees:
            fee_type = fee.get('feeType', '').upper()
            amount = fee.get('amount')
            additional_value = fee.get('additionalValue', '')
            name = fee.get('name', '')
            
            # Convert amount to float if present
            if amount:
                try:
                    amount = float(amount)
                except:
                    amount = None
            
            # Map fee types to our structure
            if fee_type == 'UPFRONT':
                # Check if it's application fee
                if any(keyword in name.lower() for keyword in ['application', 'establishment', 'setup']):
                    fees_info['application_fee'] = amount
                    fees_info['application_fee_frequency'] = 'Once-off'
                    
            elif fee_type == 'PERIODIC':
                # Check frequency and type
                if additional_value:
                    freq = self.parse_frequency(additional_value)
                    
                    # Annual fees
                    if freq == 'Annual' or 'annual' in name.lower():
                        fees_info['annual_fee'] = amount
                        
                    # Monthly fees
                    elif freq == 'Monthly' or 'monthly' in name.lower():
                        fees_info['monthly_fee'] = amount
                        
                    # Offset-related fees
                    elif any(keyword in name.lower() for keyword in ['offset']):
                        fees_info['offset_fee'] = amount
                        fees_info['offset_fee_frequency'] = freq
                        
                    else:
                        ongoing_fees.append(f"{name}: ${amount} {freq}")
                        
            elif fee_type == 'EXIT':
                fees_info['exit_fee'] = amount
                
            elif fee_type == 'TRANSACTION':
                # Check if it's redraw fee
                if any(keyword in name.lower() for keyword in ['redraw']):
                    fees_info['redraw_fee'] = amount
                else:
                    ongoing_fees.append(f"{name}: ${amount} per transaction")
                    
            else:
                # Other fees
                ongoing_fees.append(f"{name}: ${amount} ({fee_type})")
        
        # Combine other ongoing fees
        if ongoing_fees:
            fees_info['other_ongoing_fees'] = '; '.join(ongoing_fees[:3])  # Limit to first 3
        
        return fees_info
    
    def parse_frequency(self, period_str: str) -> str:
        """Parse ISO 8601 period to readable frequency"""
        try:
            if period_str.startswith('P'):
                if 'Y' in period_str:
                    return 'Annual'
                elif 'M' in period_str:
                    months = int(period_str.replace('P', '').replace('M', ''))
                    if months == 1:
                        return 'Monthly'
                    elif months == 3:
                        return 'Quarterly'
                    elif months == 6:
                        return 'Half-yearly'
                    else:
                        return f'Every {months} months'
                elif 'D' in period_str:
                    days = int(period_str.replace('P', '').replace('D', ''))
                    if days == 1:
                        return 'Daily'
                    elif days == 7:
                        return 'Weekly'
                    else:
                        return f'Every {days} days'
        except:
            pass
        return period_str
    
    def create_complete_record(self, bank_name: str, bank_id: str, product_id: str, 
                             product_name: str, rate_data: Dict, fees_info: Dict,
                             offset_available: bool, redraw_available: bool, 
                             application_url: str, last_updated: str) -> Optional[MortgageRateWithFees]:
        """Create complete mortgage record with rates and fees"""
        try:
            rate_type = rate_data.get('lendingRateType', 'UNKNOWN')
            rate_value = float(rate_data.get('rate', 0.0))
            comparison_rate = rate_data.get('comparisonRate')
            if comparison_rate:
                comparison_rate = float(comparison_rate)
            
            # Parse additional details
            additional_value = rate_data.get('additionalValue', '')
            additional_info = rate_data.get('additionalInfo', '')
            
            # Parse fixed term
            fixed_term_months = None
            if rate_type == 'FIXED' and additional_value:
                fixed_term_months = self.parse_period_to_months(additional_value)
            
            # Get loan purpose and repayment type
            loan_purpose = rate_data.get('loanPurpose', 'Not Specified')
            repayment_type = rate_data.get('repaymentType', 'Not Specified')
            
            # Handle tiers
            tiers = rate_data.get('tiers', [])
            tier_info = {}
            if tiers:
                first_tier = tiers[0]
                tier_info = {
                    'lvr_min': first_tier.get('minimumValue'),
                    'lvr_max': first_tier.get('maximumValue'),
                    'tier_name': first_tier.get('name')
                }
            else:
                tier_info = {
                    'lvr_min': None,
                    'lvr_max': None,
                    'tier_name': None
                }
            
            return MortgageRateWithFees(
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
                lvr_min=tier_info['lvr_min'],
                lvr_max=tier_info['lvr_max'],
                tier_name=tier_info['tier_name'],
                offset_available=offset_available,
                redraw_available=redraw_available,
                application_fee=fees_info.get('application_fee'),
                application_fee_frequency=fees_info.get('application_fee_frequency'),
                offset_fee=fees_info.get('offset_fee'),
                offset_fee_frequency=fees_info.get('offset_fee_frequency'),
                annual_fee=fees_info.get('annual_fee'),
                monthly_fee=fees_info.get('monthly_fee'),
                exit_fee=fees_info.get('exit_fee'),
                redraw_fee=fees_info.get('redraw_fee'),
                other_ongoing_fees=fees_info.get('other_ongoing_fees'),
                additional_info=additional_info,
                application_url=application_url,
                last_updated=last_updated
            )
                
        except Exception as e:
            self.logger.warning(f"Error creating complete record: {e}")
            return None
    
    def parse_period_to_months(self, period_str: str) -> Optional[int]:
        """Parse ISO 8601 period to months"""
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
    
    def process_bank(self, bank_name: str, bank_id: str, endpoint: str) -> List[MortgageRateWithFees]:
        """Process a single bank and extract complete rate + fees records"""
        records = []
        
        try:
            self.logger.info(f"🏦 {bank_name}: Processing rates and fees...")
            
            # Fetch basic products
            basic_products = self.fetch_products_basic(bank_name, bank_id, endpoint)
            
            if not basic_products:
                self.error_count += 1
                self.errors[bank_name] = "No mortgage products found"
                return records
            
            # Process each product for detailed rates and fees
            for basic_product in basic_products:
                product_id = basic_product.get('productId', '')
                product_name = basic_product.get('name', 'Unknown Product')
                application_url = basic_product.get('applicationUri', '')
                last_updated = datetime.now().isoformat()
                
                # Fetch detailed product info
                detailed_product = self.fetch_product_details(bank_name, endpoint, product_id)
                
                if detailed_product:
                    # Extract features
                    offset_available = False
                    redraw_available = False
                    features = detailed_product.get('features', [])
                    for feature in features:
                        feature_type = feature.get('featureType', '')
                        if feature_type == 'OFFSET':
                            offset_available = True
                        elif feature_type == 'REDRAW':
                            redraw_available = True
                    
                    # Extract fees information
                    fees_info = self.extract_fees_info(detailed_product)
                    
                    # Get lending rates
                    lending_rates = detailed_product.get('lendingRates', [])
                    
                    if lending_rates:
                        for rate in lending_rates:
                            record = self.create_complete_record(
                                bank_name, bank_id, product_id, product_name,
                                rate, fees_info, offset_available, redraw_available,
                                application_url, last_updated
                            )
                            if record:
                                records.append(record)
            
            if records:
                self.success_count += 1
                rate_count = len([r for r in records if r.rate_value > 0])
                fees_count = len([r for r in records if r.application_fee or r.annual_fee or r.monthly_fee])
                self.logger.info(f"✅ {bank_name}: {len(records)} records ({rate_count} rates, {fees_count} with fees)")
            else:
                self.error_count += 1
                self.errors[bank_name] = "No complete records extracted"
                
        except Exception as e:
            self.error_count += 1
            self.errors[bank_name] = str(e)
            self.logger.error(f"❌ {bank_name}: {str(e)}")
        
        return records
    
    def collect_complete_data(self, max_workers: int = 8) -> List[MortgageRateWithFees]:
        """Collect complete rate and fees data from all banks"""
        self.logger.info("🚀 Enhanced Fees Scraper - Complete Rate + Fees Data")
        self.logger.info("=" * 65)
        
        start_time = datetime.now()
        
        # Process all banks for comprehensive fee data
        banks_to_process = BANKS_FROM_CDR_REGISTER
        
        self.logger.info(f"🏦 Processing {len(banks_to_process)} banks for rates + fees...")
        
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
        
        self.logger.info(f"\n📊 COMPLETE DATA COLLECTION FINISHED!")
        self.logger.info(f"⏱️  Duration: {duration}")
        self.logger.info(f"🏦 Banks processed: {len(banks_to_process)}")
        self.logger.info(f"✅ Successful: {self.success_count}")
        self.logger.info(f"❌ Failed: {self.error_count}")
        self.logger.info(f"📊 Total complete records: {len(self.rate_records)}")
        
        # Count records with fees
        records_with_fees = len([r for r in self.rate_records if 
                               r.application_fee or r.annual_fee or r.monthly_fee or r.offset_fee])
        self.logger.info(f"💰 Records with fees: {records_with_fees}")
        
        return self.rate_records
    
    def save_complete_data(self, filename: str = "complete_mortgage_data"):
        """Save complete rate and fees records"""
        if not self.rate_records:
            self.logger.warning("No complete records to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as CSV
        csv_file = f"{filename}_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header - ALL the fields requested
            writer.writerow([
                'Bank Name', 'Product Name', 'Variant Name', 'Interest Rate (%)', 'Comparison Rate (%)',
                'Owner Occupier / Investor', 'Fixed / Variable', 'P&I / Interest Only',
                'Offset Available', 'Offset Fee ($)', 'Offset Fee Frequency',
                'Application Fee ($)', 'Application Fee Frequency',
                'Annual Fee ($)', 'Monthly Fee ($)', 'Exit Fee ($)', 'Redraw Fee ($)',
                'Other Ongoing Fees', 'Fixed Term (Months)', 'LVR Min (%)', 'LVR Max (%)',
                'Application URL', 'Last Updated'
            ])
            
            # Data rows
            for record in self.rate_records:
                writer.writerow([
                    record.brand_name, record.product_name, 
                    record.tier_name or 'Standard',
                    f"{record.rate_value * 100:.3f}" if record.rate_value > 0 else '',
                    f"{record.comparison_rate * 100:.3f}" if record.comparison_rate else '',
                    record.loan_purpose.replace('_', ' ').title(),
                    record.rate_type,
                    record.repayment_type.replace('_', ' ').title(),
                    'Y' if record.offset_available else 'N',
                    record.offset_fee if record.offset_fee else '',
                    record.offset_fee_frequency if record.offset_fee_frequency else '',
                    record.application_fee if record.application_fee else '',
                    record.application_fee_frequency if record.application_fee_frequency else '',
                    record.annual_fee if record.annual_fee else '',
                    record.monthly_fee if record.monthly_fee else '',
                    record.exit_fee if record.exit_fee else '',
                    record.redraw_fee if record.redraw_fee else '',
                    record.other_ongoing_fees if record.other_ongoing_fees else '',
                    record.fixed_term_months if record.fixed_term_months else '',
                    record.lvr_min if record.lvr_min else '',
                    record.lvr_max if record.lvr_max else '',
                    record.application_url, record.last_updated
                ])
        
        self.logger.info(f"💾 Complete data saved:")
        self.logger.info(f"   📄 CSV: {csv_file}")
        
        return csv_file

def main():
    """Main execution"""
    scraper = EnhancedFeesScraper()
    
    # Collect complete data
    complete_records = scraper.collect_complete_data()
    
    # Save results
    csv_file = scraper.save_complete_data()
    
    print(f"\n🎉 Complete Rate + Fees Collection Finished!")
    print(f"📊 Total records: {len(complete_records)}")
    print(f"💰 Records with fees: {len([r for r in complete_records if r.application_fee or r.annual_fee or r.monthly_fee])}")
    print(f"📄 Saved to: {csv_file}")
    print(f"\n🚀 Ready for enhanced Streamlit dashboard!")

if __name__ == "__main__":
    main()
