#!/usr/bin/env python3
"""
Enhanced Real-Time CDR Scraper

Works with known bank endpoints and can be easily updated when CDR register is available.
Gets fresh data directly from bank APIs with real-time rates and features.
"""

import json
import csv
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging
import concurrent.futures
from pathlib import Path
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class RealTimeProduct:
    """Real-time product with enhanced features"""
    # Source
    bank_name: str
    brand_id: str
    product_id: str
    
    # Product details
    product_name: str
    product_category: str
    description: str
    
    # Rates - properly extracted
    variable_rate: Optional[float]
    fixed_rate_1yr: Optional[float]
    fixed_rate_2yr: Optional[float]
    fixed_rate_3yr: Optional[float]
    fixed_rate_4yr: Optional[float]
    fixed_rate_5yr: Optional[float]
    comparison_rate: Optional[float]
    
    # Loan characteristics - properly extracted
    loan_purpose: str
    repayment_type: str
    
    # Features - properly extracted
    offset_available: bool
    redraw_available: bool
    extra_repayments: bool
    split_loan: bool
    construction_loan: bool
    
    # Fees - when available
    application_fee: Optional[float]
    annual_fee: Optional[float]
    monthly_fee: Optional[float]
    exit_fee: Optional[float]
    
    # Constraints
    minimum_amount: Optional[float]
    maximum_amount: Optional[float]
    
    # URLs
    application_url: str
    info_url: str
    
    # Metadata
    effective_from: str
    last_updated: str
    data_freshness: str
    
    # Calculated
    monthly_repayment_300k: Optional[float]
    monthly_repayment_500k: Optional[float]
    monthly_repayment_750k: Optional[float]

class EnhancedRealTimeScraper:
    """Enhanced real-time scraper with known endpoints"""
    
    def __init__(self):
        # Known working endpoints (can be expanded)
        self.bank_endpoints = {
            'ANZ': {
                'name': 'ANZ',
                'base_url': 'https://api.anz',
                'products_endpoint': 'https://api.anz/cds-au/v1/banking/products',
                'brand_id': '13e52c9e-3c96-eb11-a823-000d3a884a20'
            },
            'CommBank': {
                'name': 'Commonwealth Bank',
                'base_url': 'https://api.commbank.com.au/public',
                'products_endpoint': 'https://api.commbank.com.au/public/cds-au/v1/banking/products',
                'brand_id': '25233bad-ddc7-ea11-a828-000d3a8842e1'
            },
            'NAB': {
                'name': 'National Australia Bank',
                'base_url': 'https://openbank.api.nab.com.au',
                'products_endpoint': 'https://openbank.api.nab.com.au/cds-au/v1/banking/products',
                'brand_id': 'aeb217c9-3c96-eb11-a823-000d3a884a20'
            },
            'Westpac': {
                'name': 'Westpac',
                'base_url': 'https://digital-api.westpac.com.au',
                'products_endpoint': 'https://digital-api.westpac.com.au/cds-au/v1/banking/products',
                'brand_id': '3cfb2b7c-3c96-eb11-a823-000d3a884a20'
            }
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Enhanced-Real-Time-CDR-Scraper/1.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-AU,en;q=0.9'
        })
        
        self.all_products = []
        self.errors = []
        
        # Create output directory
        self.output_dir = Path("realtime_data")
        self.output_dir.mkdir(exist_ok=True)
    
    def fetch_bank_products_enhanced(self, bank_code: str, bank_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """Fetch products from a bank with enhanced error handling"""
        try:
            logger.info(f"🏦 Fetching real-time data from {bank_info['name']}...")
            
            headers = {
                'x-v': '3',
                'Accept': 'application/json'
            }
            
            response = self.session.get(
                bank_info['products_endpoint'],
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('data', {}).get('products', [])
                
                # Filter for residential mortgages and add bank context
                residential_products = []
                for product in products:
                    category = product.get('productCategory', '').upper()
                    name = product.get('name', '').upper()
                    
                    if ('RESIDENTIAL' in category or 
                        'MORTGAGE' in category or 
                        'HOME' in name or 
                        'MORTGAGE' in name):
                        
                        # Add bank context
                        product['_bank_info'] = bank_info
                        product['_bank_code'] = bank_code
                        residential_products.append(product)
                
                logger.info(f"✅ {bank_info['name']}: {len(residential_products)} mortgage products")
                return residential_products
                
            else:
                error_msg = f"{bank_info['name']}: HTTP {response.status_code}"
                if response.status_code == 406:
                    error_msg += " (Version not supported - trying fallback)"
                    
                    # Try without version header
                    headers.pop('x-v', None)
                    response = self.session.get(bank_info['products_endpoint'], headers=headers, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        products = data.get('data', {}).get('products', [])
                        logger.info(f"✅ {bank_info['name']}: {len(products)} products (fallback)")
                        return products
                
                logger.warning(error_msg)
                self.errors.append(error_msg)
                return []
                
        except Exception as e:
            error_msg = f"{bank_info['name']}: {str(e)}"
            logger.warning(error_msg)
            self.errors.append(error_msg)
            return []
    
    def fetch_detailed_product_enhanced(self, bank_info: Dict[str, str], product_id: str) -> Dict[str, Any]:
        """Fetch detailed product information"""
        try:
            detail_url = f"{bank_info['products_endpoint']}/{product_id}"
            
            headers = {
                'x-v': '3',
                'Accept': 'application/json'
            }
            
            response = self.session.get(detail_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return response.json().get('data', {})
            elif response.status_code == 406:
                # Try without version
                headers.pop('x-v', None)
                response = self.session.get(detail_url, headers=headers, timeout=15)
                if response.status_code == 200:
                    return response.json().get('data', {})
            
            return {}
            
        except Exception as e:
            logger.debug(f"Could not fetch detailed product {product_id}: {e}")
            return {}
    
    def extract_rates_enhanced(self, product: Dict[str, Any], detailed_data: Dict[str, Any]) -> Dict[str, Optional[float]]:
        """Extract rates with enhanced logic"""
        rates = {
            'variable_rate': None,
            'fixed_rate_1yr': None,
            'fixed_rate_2yr': None,
            'fixed_rate_3yr': None,
            'fixed_rate_4yr': None,
            'fixed_rate_5yr': None,
            'comparison_rate': None
        }
        
        # Try detailed data first
        lending_rates = detailed_data.get('lendingRates', [])
        if not lending_rates:
            # Fallback to basic product data if available
            lending_rates = product.get('lendingRates', [])
        
        for rate in lending_rates:
            rate_type = rate.get('lendingRateType', '').upper()
            rate_value = rate.get('rate')
            additional_value = rate.get('additionalValue')  # For period info
            
            if rate_value is not None:
                if rate_type == 'VARIABLE':
                    rates['variable_rate'] = float(rate_value) * 100  # Convert to percentage
                elif rate_type == 'FIXED':
                    # Check period for fixed rates
                    if additional_value:
                        if additional_value.startswith('P1Y'):
                            rates['fixed_rate_1yr'] = float(rate_value) * 100
                        elif additional_value.startswith('P2Y'):
                            rates['fixed_rate_2yr'] = float(rate_value) * 100
                        elif additional_value.startswith('P3Y'):
                            rates['fixed_rate_3yr'] = float(rate_value) * 100
                        elif additional_value.startswith('P4Y'):
                            rates['fixed_rate_4yr'] = float(rate_value) * 100
                        elif additional_value.startswith('P5Y'):
                            rates['fixed_rate_5yr'] = float(rate_value) * 100
                elif 'COMPARISON' in rate_type:
                    rates['comparison_rate'] = float(rate_value) * 100
        
        return rates
    
    def extract_features_enhanced(self, product: Dict[str, Any], detailed_data: Dict[str, Any]) -> Dict[str, bool]:
        """Extract features with enhanced detection"""
        features = {
            'offset_available': False,
            'redraw_available': False,
            'extra_repayments': False,
            'split_loan': False,
            'construction_loan': False
        }
        
        # Check features in detailed data
        feature_list = detailed_data.get('features', [])
        for feature in feature_list:
            feature_type = feature.get('featureType', '').upper()
            description = feature.get('description', '').lower()
            
            if 'OFFSET' in feature_type or 'offset' in description:
                features['offset_available'] = True
            if 'REDRAW' in feature_type or 'redraw' in description:
                features['redraw_available'] = True
            if 'EXTRA' in feature_type or 'extra repayment' in description:
                features['extra_repayments'] = True
            if 'SPLIT' in feature_type or 'split' in description:
                features['split_loan'] = True
            if 'CONSTRUCTION' in feature_type or 'construction' in description:
                features['construction_loan'] = True
        
        # Also check product name and description
        product_text = f"{product.get('name', '')} {product.get('description', '')}".lower()
        
        if 'offset' in product_text:
            features['offset_available'] = True
        if 'redraw' in product_text:
            features['redraw_available'] = True
        if 'extra repayment' in product_text or 'additional repayment' in product_text:
            features['extra_repayments'] = True
        if 'split' in product_text:
            features['split_loan'] = True
        if 'construction' in product_text or 'building' in product_text:
            features['construction_loan'] = True
        
        return features
    
    def extract_loan_details_enhanced(self, product: Dict[str, Any], detailed_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract loan purpose and repayment type"""
        details = {
            'loan_purpose': 'Not Specified',
            'repayment_type': 'Not Specified'
        }
        
        # Check constraints and eligibility
        constraints = detailed_data.get('constraints', [])
        eligibility = detailed_data.get('eligibility', [])
        
        all_text = ' '.join([
            product.get('name', ''),
            product.get('description', ''),
            ' '.join([c.get('description', '') for c in constraints]),
            ' '.join([e.get('description', '') for e in eligibility])
        ]).lower()
        
        # Loan purpose
        if 'investment' in all_text and ('owner occupier' in all_text or 'owner-occupier' in all_text):
            details['loan_purpose'] = 'Both'
        elif 'investment' in all_text:
            details['loan_purpose'] = 'Investment'
        elif 'owner occupier' in all_text or 'owner-occupier' in all_text or 'ppor' in all_text:
            details['loan_purpose'] = 'Owner Occupier'
        else:
            details['loan_purpose'] = 'Both'  # Default for residential mortgages
        
        # Repayment type
        if ('principal and interest' in all_text or 'p&i' in all_text) and ('interest only' in all_text or 'i/o' in all_text):
            details['repayment_type'] = 'Both'
        elif 'interest only' in all_text or 'i/o' in all_text:
            details['repayment_type'] = 'Interest Only'
        elif 'principal and interest' in all_text or 'p&i' in all_text:
            details['repayment_type'] = 'Principal and Interest'
        else:
            details['repayment_type'] = 'Principal and Interest'  # Default
        
        return details
    
    def extract_fees_enhanced(self, detailed_data: Dict[str, Any]) -> Dict[str, Optional[float]]:
        """Extract fee information"""
        fees = {
            'application_fee': None,
            'annual_fee': None,
            'monthly_fee': None,
            'exit_fee': None
        }
        
        fee_list = detailed_data.get('fees', [])
        for fee in fee_list:
            fee_type = fee.get('feeType', '').upper()
            name = fee.get('name', '').lower()
            amount = fee.get('amount')
            
            if amount is not None:
                if 'APPLICATION' in fee_type or 'application' in name or 'establishment' in name:
                    fees['application_fee'] = float(amount)
                elif 'ANNUAL' in fee_type or 'annual' in name or 'yearly' in name:
                    fees['annual_fee'] = float(amount)
                elif 'MONTHLY' in fee_type or 'monthly' in name:
                    fees['monthly_fee'] = float(amount)
                elif 'EXIT' in fee_type or 'exit' in name or 'termination' in name:
                    fees['exit_fee'] = float(amount)
        
        return fees
    
    def calculate_monthly_repayment(self, rate: Optional[float], loan_amount: float) -> Optional[float]:
        """Calculate monthly repayment"""
        if rate is None or rate <= 0:
            return None
        
        monthly_rate = rate / 100 / 12
        n_payments = 30 * 12  # 30 years
        
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
            return round(monthly_payment, 2)
        
        return None
    
    def process_product_enhanced(self, product: Dict[str, Any]) -> RealTimeProduct:
        """Process product with enhanced extraction"""
        bank_info = product.get('_bank_info', {})
        
        # Get detailed product data
        product_id = product.get('productId', '')
        detailed_data = self.fetch_detailed_product_enhanced(bank_info, product_id)
        
        # Extract all components
        rates = self.extract_rates_enhanced(product, detailed_data)
        features = self.extract_features_enhanced(product, detailed_data)
        loan_details = self.extract_loan_details_enhanced(product, detailed_data)
        fees = self.extract_fees_enhanced(detailed_data)
        
        # Calculate repayments using the best available rate
        best_rate = (rates.get('variable_rate') or 
                    rates.get('fixed_rate_1yr') or 
                    rates.get('fixed_rate_2yr') or 
                    rates.get('fixed_rate_3yr'))
        
        return RealTimeProduct(
            bank_name=bank_info.get('name', ''),
            brand_id=bank_info.get('brand_id', ''),
            product_id=product_id,
            product_name=product.get('name', ''),
            product_category=product.get('productCategory', ''),
            description=product.get('description', ''),
            variable_rate=rates.get('variable_rate'),
            fixed_rate_1yr=rates.get('fixed_rate_1yr'),
            fixed_rate_2yr=rates.get('fixed_rate_2yr'),
            fixed_rate_3yr=rates.get('fixed_rate_3yr'),
            fixed_rate_4yr=rates.get('fixed_rate_4yr'),
            fixed_rate_5yr=rates.get('fixed_rate_5yr'),
            comparison_rate=rates.get('comparison_rate'),
            loan_purpose=loan_details.get('loan_purpose'),
            repayment_type=loan_details.get('repayment_type'),
            offset_available=features.get('offset_available'),
            redraw_available=features.get('redraw_available'),
            extra_repayments=features.get('extra_repayments'),
            split_loan=features.get('split_loan'),
            construction_loan=features.get('construction_loan'),
            application_fee=fees.get('application_fee'),
            annual_fee=fees.get('annual_fee'),
            monthly_fee=fees.get('monthly_fee'),
            exit_fee=fees.get('exit_fee'),
            minimum_amount=None,  # Would be in constraints
            maximum_amount=None,  # Would be in constraints
            application_url=product.get('applicationUri', ''),
            info_url=product.get('additionalInformationUri', ''),
            effective_from=product.get('effectiveFrom', ''),
            last_updated=product.get('lastUpdated', ''),
            data_freshness=datetime.now().isoformat(),
            monthly_repayment_300k=self.calculate_monthly_repayment(best_rate, 300000),
            monthly_repayment_500k=self.calculate_monthly_repayment(best_rate, 500000),
            monthly_repayment_750k=self.calculate_monthly_repayment(best_rate, 750000)
        )
    
    def run_enhanced_pipeline(self):
        """Run the enhanced real-time pipeline"""
        logger.info("🚀 Enhanced Real-Time CDR Pipeline Starting...")
        logger.info("=" * 55)
        
        start_time = datetime.now()
        all_products = []
        
        # Process each bank
        for bank_code, bank_info in self.bank_endpoints.items():
            try:
                # Fetch products
                products = self.fetch_bank_products_enhanced(bank_code, bank_info)
                
                # Process each product
                for product in products:
                    processed_product = self.process_product_enhanced(product)
                    all_products.append(processed_product)
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                error_msg = f"Error processing {bank_code}: {e}"
                logger.error(error_msg)
                self.errors.append(error_msg)
        
        self.all_products = all_products
        
        # Save results
        files_created = self.save_enhanced_results()
        
        # Print summary
        end_time = datetime.now()
        duration = end_time - start_time
        self.print_enhanced_summary(duration, files_created)
        
        return files_created
    
    def save_enhanced_results(self) -> Dict[str, str]:
        """Save enhanced results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        files_created = {}
        
        # Save CSV
        csv_file = self.output_dir / f"enhanced_realtime_mortgages_{timestamp}.csv"
        self.save_enhanced_csv(csv_file)
        files_created['csv'] = str(csv_file)
        
        # Save JSON
        json_file = self.output_dir / f"enhanced_realtime_mortgages_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump([asdict(product) for product in self.all_products], f, indent=2, default=str)
        files_created['json'] = str(json_file)
        
        return files_created
    
    def save_enhanced_csv(self, filename: Path):
        """Save enhanced CSV format"""
        fieldnames = [
            'Bank Name', 'Product ID', 'Product Name', 'Category', 'Description',
            'Variable Rate (%)', 'Fixed Rate 1Yr (%)', 'Fixed Rate 2Yr (%)', 
            'Fixed Rate 3Yr (%)', 'Fixed Rate 4Yr (%)', 'Fixed Rate 5Yr (%)',
            'Comparison Rate (%)', 'Loan Purpose', 'Repayment Type',
            'Offset Available', 'Redraw Available', 'Extra Repayments',
            'Split Loan', 'Construction Loan', 'Application Fee ($)',
            'Annual Fee ($)', 'Monthly Fee ($)', 'Exit Fee ($)',
            'Monthly Repayment $300K', 'Monthly Repayment $500K', 
            'Monthly Repayment $750K', 'Application URL', 'Last Updated',
            'Data Freshness'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in self.all_products:
                row = {
                    'Bank Name': product.bank_name,
                    'Product ID': product.product_id,
                    'Product Name': product.product_name,
                    'Category': product.product_category,
                    'Description': product.description[:150] + "..." if len(product.description) > 150 else product.description,
                    'Variable Rate (%)': f"{product.variable_rate:.2f}" if product.variable_rate else '',
                    'Fixed Rate 1Yr (%)': f"{product.fixed_rate_1yr:.2f}" if product.fixed_rate_1yr else '',
                    'Fixed Rate 2Yr (%)': f"{product.fixed_rate_2yr:.2f}" if product.fixed_rate_2yr else '',
                    'Fixed Rate 3Yr (%)': f"{product.fixed_rate_3yr:.2f}" if product.fixed_rate_3yr else '',
                    'Fixed Rate 4Yr (%)': f"{product.fixed_rate_4yr:.2f}" if product.fixed_rate_4yr else '',
                    'Fixed Rate 5Yr (%)': f"{product.fixed_rate_5yr:.2f}" if product.fixed_rate_5yr else '',
                    'Comparison Rate (%)': f"{product.comparison_rate:.2f}" if product.comparison_rate else '',
                    'Loan Purpose': product.loan_purpose,
                    'Repayment Type': product.repayment_type,
                    'Offset Available': 'Y' if product.offset_available else 'N',
                    'Redraw Available': 'Y' if product.redraw_available else 'N',
                    'Extra Repayments': 'Y' if product.extra_repayments else 'N',
                    'Split Loan': 'Y' if product.split_loan else 'N',
                    'Construction Loan': 'Y' if product.construction_loan else 'N',
                    'Application Fee ($)': f"{product.application_fee:.0f}" if product.application_fee else '',
                    'Annual Fee ($)': f"{product.annual_fee:.0f}" if product.annual_fee else '',
                    'Monthly Fee ($)': f"{product.monthly_fee:.0f}" if product.monthly_fee else '',
                    'Exit Fee ($)': f"{product.exit_fee:.0f}" if product.exit_fee else '',
                    'Monthly Repayment $300K': f"${product.monthly_repayment_300k:,.0f}" if product.monthly_repayment_300k else '',
                    'Monthly Repayment $500K': f"${product.monthly_repayment_500k:,.0f}" if product.monthly_repayment_500k else '',
                    'Monthly Repayment $750K': f"${product.monthly_repayment_750k:,.0f}" if product.monthly_repayment_750k else '',
                    'Application URL': product.application_url,
                    'Last Updated': product.last_updated,
                    'Data Freshness': product.data_freshness
                }
                writer.writerow(row)
    
    def print_enhanced_summary(self, duration: timedelta, files_created: Dict[str, str]):
        """Print enhanced summary"""
        print(f"\n🎉 ENHANCED REAL-TIME PIPELINE COMPLETE!")
        print("=" * 50)
        print(f"⏱️  Execution time: {duration}")
        print(f"🏦 Banks processed: {len(self.bank_endpoints)}")
        print(f"📊 Products collected: {len(self.all_products)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.all_products:
            # Feature statistics
            with_offset = len([p for p in self.all_products if p.offset_available])
            with_redraw = len([p for p in self.all_products if p.redraw_available])
            with_rates = len([p for p in self.all_products if p.variable_rate or p.fixed_rate_1yr])
            
            print(f"\n📈 Real-Time Data Quality:")
            print(f"   • Products with rates: {with_rates} ({with_rates/len(self.all_products)*100:.1f}%)")
            print(f"   • Products with offset: {with_offset} ({with_offset/len(self.all_products)*100:.1f}%)")
            print(f"   • Products with redraw: {with_redraw} ({with_redraw/len(self.all_products)*100:.1f}%)")
            
            # Bank distribution
            bank_counts = {}
            for product in self.all_products:
                bank_counts[product.bank_name] = bank_counts.get(product.bank_name, 0) + 1
            
            print(f"\n🏛️  Bank Distribution:")
            for bank, count in bank_counts.items():
                print(f"   • {bank}: {count} products")
        
        print(f"\n📁 Files created:")
        for format_type, filepath in files_created.items():
            print(f"   • {format_type.upper()}: {filepath}")
        
        print(f"\n🔄 Data Freshness: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("✅ Real-time data - no dependency on outdated repositories!")
        print("💡 Schedule this monthly for fresh mortgage data!")

def main():
    """Main function"""
    scraper = EnhancedRealTimeScraper()
    
    try:
        files_created = scraper.run_enhanced_pipeline()
        print(f"\n🎯 SUCCESS: Enhanced real-time scraper completed!")
        print(f"🚀 Fresh data collected directly from bank APIs!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Enhanced pipeline failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())


