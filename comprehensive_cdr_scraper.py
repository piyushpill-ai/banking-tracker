#!/usr/bin/env python3
"""
Comprehensive CDR-Based Home Loan Scraper

Leverages the Open Banking Tracker and official CDR register to access
1000+ mortgage products from 100+ brands, inspired by LukePrior/mortgage-manager.
"""

import json
import csv
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
import re
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ComprehensiveCDRProduct:
    """Comprehensive data structure based on CDR standards"""
    brand_id: str
    brand_name: str
    product_id: str
    product_name: str
    product_category: str
    description: str
    variable_rate: str
    fixed_rate_1yr: str
    fixed_rate_2yr: str
    fixed_rate_3yr: str
    fixed_rate_4yr: str
    fixed_rate_5yr: str
    comparison_rate: str
    loan_purpose: str
    repayment_type: str
    offset_available: str
    redraw_available: str
    split_loan_available: str
    construction_available: str
    application_fee: str
    annual_fee: str
    monthly_fee: str
    exit_fee: str
    valuation_fee: str
    settlement_fee: str
    other_fees: str
    features: str
    eligibility: str
    constraints: str
    minimum_amount: str
    maximum_amount: str
    application_url: str
    last_updated: str
    monthly_repayment_300k: str
    monthly_repayment_500k: str
    monthly_repayment_750k: str

class ComprehensiveCDRScraper:
    """Enhanced scraper using CDR register and Open Banking Tracker data"""
    
    def __init__(self):
        # Open Banking Tracker URLs (inspired by mortgage-manager)
        self.cdr_register_url = "https://api.cdr.gov.au/cdr-register/v1/banking/register"
        self.open_banking_base = "https://raw.githubusercontent.com/LukePrior/open-banking-tracker/main"
        self.residential_mortgages_url = f"{self.open_banking_base}/aggregate/RESIDENTIAL_MORTGAGES/data.json"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
        
        self.all_products = []
        self.brand_mapping = {}
    
    def fetch_cdr_register(self) -> Dict[str, Any]:
        """Fetch the official CDR register to get all authorized banking institutions"""
        try:
            logger.info("Fetching CDR register for all authorized banking institutions...")
            response = self.session.get(self.cdr_register_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                brands = data.get('data', [])
                logger.info(f"Found {len(brands)} authorized banking brands in CDR register")
                
                # Create brand mapping
                for brand in brands:
                    brand_id = brand.get('brandId', '')
                    brand_name = brand.get('brandName', '')
                    if brand_id and brand_name:
                        self.brand_mapping[brand_id] = {
                            'name': brand_name,
                            'legal_entity': brand.get('legalEntityName', ''),
                            'industry': brand.get('industry', ''),
                            'endpoints': brand.get('endpointDetail', {})
                        }
                
                return data
            else:
                logger.warning(f"Failed to fetch CDR register: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching CDR register: {e}")
            return {}
    
    def fetch_aggregated_mortgages(self) -> List[Dict[str, Any]]:
        """Fetch pre-aggregated residential mortgage data from Open Banking Tracker"""
        try:
            logger.info("Fetching aggregated residential mortgage data...")
            response = self.session.get(self.residential_mortgages_url, timeout=60)
            
            if response.status_code == 200:
                products = response.json()
                logger.info(f"Retrieved {len(products)} mortgage products from Open Banking Tracker")
                return products
            else:
                logger.warning(f"Failed to fetch aggregated data: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching aggregated mortgage data: {e}")
            return []
    
    def fetch_detailed_product(self, brand_id: str, product_id: str) -> Dict[str, Any]:
        """Fetch detailed product information from Open Banking Tracker"""
        try:
            detail_url = f"{self.open_banking_base}/data/{brand_id}/{product_id}.json"
            response = self.session.get(detail_url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.debug(f"No detailed data for {brand_id}/{product_id}")
                return {}
                
        except Exception as e:
            logger.debug(f"Error fetching detailed product {brand_id}/{product_id}: {e}")
            return {}
    
    def extract_rates_comprehensive(self, product: Dict[str, Any]) -> Dict[str, str]:
        """Extract comprehensive rate information"""
        rates = {
            'variable_rate': '',
            'fixed_rate_1yr': '',
            'fixed_rate_2yr': '',
            'fixed_rate_3yr': '',
            'fixed_rate_4yr': '',
            'fixed_rate_5yr': '',
            'comparison_rate': ''
        }
        
        try:
            rate_data = product.get('rate', [])
            
            for rate in rate_data:
                rate_type = rate.get('lendingRateType', '').upper()
                rate_value = rate.get('rate', 0)
                period = rate.get('period', 0)
                
                if rate_value and isinstance(rate_value, (int, float)):
                    rate_str = f"{rate_value:.2f}%"
                    
                    if rate_type == 'VARIABLE':
                        rates['variable_rate'] = rate_str
                    elif rate_type == 'FIXED':
                        # Map period to specific fixed rate fields
                        if period == 12:  # 1 year
                            rates['fixed_rate_1yr'] = rate_str
                        elif period == 24:  # 2 years
                            rates['fixed_rate_2yr'] = rate_str
                        elif period == 36:  # 3 years
                            rates['fixed_rate_3yr'] = rate_str
                        elif period == 48:  # 4 years
                            rates['fixed_rate_4yr'] = rate_str
                        elif period == 60:  # 5 years
                            rates['fixed_rate_5yr'] = rate_str
                    elif 'COMPARISON' in rate_type:
                        rates['comparison_rate'] = rate_str
            
        except Exception as e:
            logger.warning(f"Error extracting rates: {e}")
        
        return rates
    
    def extract_fees_comprehensive(self, detailed_product: Dict[str, Any]) -> Dict[str, str]:
        """Extract comprehensive fee information"""
        fees = {
            'application_fee': '',
            'annual_fee': '',
            'monthly_fee': '',
            'exit_fee': '',
            'valuation_fee': '',
            'settlement_fee': '',
            'other_fees': ''
        }
        
        try:
            fee_data = detailed_product.get('fees', [])
            other_fees_list = []
            
            for fee in fee_data:
                fee_type = fee.get('feeType', '').lower()
                name = fee.get('name', '').lower()
                amount = fee.get('amount')
                rate = fee.get('rate')
                
                # Format fee amount
                fee_value = ''
                if amount:
                    fee_value = f"${amount:.0f}" if isinstance(amount, (int, float)) else str(amount)
                elif rate:
                    fee_value = f"{rate:.2f}%" if isinstance(rate, (int, float)) else str(rate)
                
                if not fee_value:
                    continue
                
                # Map to specific fee categories
                if 'application' in fee_type or 'application' in name or 'establishment' in name:
                    fees['application_fee'] = fee_value
                elif 'annual' in fee_type or 'annual' in name or 'yearly' in name:
                    fees['annual_fee'] = fee_value
                elif 'monthly' in fee_type or 'monthly' in name:
                    fees['monthly_fee'] = fee_value
                elif 'exit' in fee_type or 'exit' in name or 'termination' in name:
                    fees['exit_fee'] = fee_value
                elif 'valuation' in name or 'valuation' in fee_type:
                    fees['valuation_fee'] = fee_value
                elif 'settlement' in name or 'settlement' in fee_type:
                    fees['settlement_fee'] = fee_value
                else:
                    other_fees_list.append(f"{fee.get('name', 'Fee')}: {fee_value}")
            
            if other_fees_list:
                fees['other_fees'] = " | ".join(other_fees_list)
            
        except Exception as e:
            logger.warning(f"Error extracting fees: {e}")
        
        return fees
    
    def extract_features_comprehensive(self, detailed_product: Dict[str, Any]) -> Dict[str, str]:
        """Extract comprehensive feature information"""
        features_info = {
            'offset_available': 'N',
            'redraw_available': 'N',
            'split_loan_available': 'N',
            'construction_available': 'N',
            'features': ''
        }
        
        try:
            features = detailed_product.get('features', [])
            feature_names = []
            
            for feature in features:
                feature_type = feature.get('featureType', '').lower()
                description = feature.get('description', '').lower()
                
                # Check for specific features
                if 'offset' in feature_type or 'offset' in description:
                    features_info['offset_available'] = 'Y'
                    feature_names.append('Offset Account')
                
                if 'redraw' in feature_type or 'redraw' in description:
                    features_info['redraw_available'] = 'Y'
                    feature_names.append('Redraw Facility')
                
                if any(word in feature_type or word in description for word in ['split', 'portion']):
                    features_info['split_loan_available'] = 'Y'
                    feature_names.append('Split Loan')
                
                if 'construction' in feature_type or 'construction' in description:
                    features_info['construction_available'] = 'Y'
                    feature_names.append('Construction Loan')
                
                # Add other features
                if feature.get('featureType'):
                    formatted_feature = feature['featureType'].replace('_', ' ').title()
                    if formatted_feature not in feature_names:
                        feature_names.append(formatted_feature)
            
            features_info['features'] = ' | '.join(feature_names) if feature_names else ''
            
        except Exception as e:
            logger.warning(f"Error extracting features: {e}")
        
        return features_info
    
    def calculate_monthly_repayments(self, rates: Dict[str, str]) -> Dict[str, str]:
        """Calculate monthly repayments for standard loan amounts"""
        repayments = {
            'monthly_repayment_300k': '',
            'monthly_repayment_500k': '',
            'monthly_repayment_750k': ''
        }
        
        try:
            # Use variable rate if available, otherwise use lowest fixed rate
            rate_str = rates.get('variable_rate') or rates.get('fixed_rate_1yr') or rates.get('fixed_rate_2yr')
            
            if rate_str and '%' in rate_str:
                annual_rate = float(rate_str.replace('%', '')) / 100
                monthly_rate = annual_rate / 12
                n_payments = 30 * 12  # 30 years
                
                loan_amounts = [300000, 500000, 750000]
                repayment_keys = ['monthly_repayment_300k', 'monthly_repayment_500k', 'monthly_repayment_750k']
                
                for loan_amount, key in zip(loan_amounts, repayment_keys):
                    if monthly_rate > 0:
                        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
                        repayments[key] = f"${monthly_payment:,.0f}"
                    else:
                        repayments[key] = "Interest-free"
            
        except Exception as e:
            logger.warning(f"Error calculating repayments: {e}")
        
        return repayments
    
    def process_comprehensive_products(self, products: List[Dict[str, Any]]) -> List[ComprehensiveCDRProduct]:
        """Process products into comprehensive format"""
        processed_products = []
        
        for i, product in enumerate(products):
            try:
                if i % 50 == 0:
                    logger.info(f"Processing product {i+1}/{len(products)}")
                
                # Basic product info
                brand_id = product.get('brandId', '')
                product_id = product.get('productId', '')
                
                # Get brand name from mapping
                brand_info = self.brand_mapping.get(brand_id, {})
                brand_name = brand_info.get('name', f'Brand-{brand_id}')
                
                # Extract rates
                rates = self.extract_rates_comprehensive(product)
                
                # Get detailed product information
                detailed_product = self.fetch_detailed_product(brand_id, product_id)
                
                # Extract fees and features
                fees = self.extract_fees_comprehensive(detailed_product)
                features = self.extract_features_comprehensive(detailed_product)
                
                # Calculate repayments
                repayments = self.calculate_monthly_repayments(rates)
                
                # Extract other information
                eligibility = self.extract_eligibility(detailed_product)
                constraints = self.extract_constraints(detailed_product)
                loan_amounts = self.extract_loan_amounts(detailed_product)
                
                # Determine loan purpose and repayment type
                loan_purpose = self.determine_loan_purpose(product, detailed_product)
                repayment_type = self.determine_repayment_type(product, detailed_product)
                
                comprehensive_product = ComprehensiveCDRProduct(
                    brand_id=brand_id,
                    brand_name=brand_name,
                    product_id=product_id,
                    product_name=product.get('name', ''),
                    product_category=product.get('productCategory', ''),
                    description=product.get('description', '')[:500] + "..." if len(product.get('description', '')) > 500 else product.get('description', ''),
                    variable_rate=rates['variable_rate'],
                    fixed_rate_1yr=rates['fixed_rate_1yr'],
                    fixed_rate_2yr=rates['fixed_rate_2yr'],
                    fixed_rate_3yr=rates['fixed_rate_3yr'],
                    fixed_rate_4yr=rates['fixed_rate_4yr'],
                    fixed_rate_5yr=rates['fixed_rate_5yr'],
                    comparison_rate=rates['comparison_rate'],
                    loan_purpose=loan_purpose,
                    repayment_type=repayment_type,
                    offset_available=features['offset_available'],
                    redraw_available=features['redraw_available'],
                    split_loan_available=features['split_loan_available'],
                    construction_available=features['construction_available'],
                    application_fee=fees['application_fee'],
                    annual_fee=fees['annual_fee'],
                    monthly_fee=fees['monthly_fee'],
                    exit_fee=fees['exit_fee'],
                    valuation_fee=fees['valuation_fee'],
                    settlement_fee=fees['settlement_fee'],
                    other_fees=fees['other_fees'],
                    features=features['features'],
                    eligibility=eligibility,
                    constraints=constraints,
                    minimum_amount=loan_amounts.get('min', ''),
                    maximum_amount=loan_amounts.get('max', ''),
                    application_url=detailed_product.get('applicationUri', ''),
                    last_updated=product.get('lastUpdated', ''),
                    monthly_repayment_300k=repayments['monthly_repayment_300k'],
                    monthly_repayment_500k=repayments['monthly_repayment_500k'],
                    monthly_repayment_750k=repayments['monthly_repayment_750k']
                )
                
                processed_products.append(comprehensive_product)
                
                # Small delay to be respectful
                if i % 10 == 0:
                    time.sleep(0.5)
                    
            except Exception as e:
                logger.warning(f"Error processing product {i}: {e}")
                continue
        
        return processed_products
    
    def extract_eligibility(self, detailed_product: Dict[str, Any]) -> str:
        """Extract eligibility requirements"""
        try:
            eligibility_list = detailed_product.get('eligibility', [])
            requirements = []
            
            for item in eligibility_list:
                description = item.get('description', '')
                if description:
                    requirements.append(description)
            
            return ' | '.join(requirements) if requirements else ''
            
        except Exception as e:
            logger.warning(f"Error extracting eligibility: {e}")
            return ''
    
    def extract_constraints(self, detailed_product: Dict[str, Any]) -> str:
        """Extract product constraints"""
        try:
            constraints_list = detailed_product.get('constraints', [])
            constraints = []
            
            for item in constraints_list:
                description = item.get('description', '')
                if description:
                    constraints.append(description)
            
            return ' | '.join(constraints) if constraints else ''
            
        except Exception as e:
            logger.warning(f"Error extracting constraints: {e}")
            return ''
    
    def extract_loan_amounts(self, detailed_product: Dict[str, Any]) -> Dict[str, str]:
        """Extract minimum and maximum loan amounts"""
        amounts = {'min': '', 'max': ''}
        
        try:
            constraints = detailed_product.get('constraints', [])
            
            for constraint in constraints:
                constraint_type = constraint.get('constraintType', '').lower()
                value = constraint.get('value')
                
                if value and 'min' in constraint_type and 'amount' in constraint_type:
                    amounts['min'] = f"${value:,.0f}" if isinstance(value, (int, float)) else str(value)
                elif value and 'max' in constraint_type and 'amount' in constraint_type:
                    amounts['max'] = f"${value:,.0f}" if isinstance(value, (int, float)) else str(value)
            
        except Exception as e:
            logger.warning(f"Error extracting loan amounts: {e}")
        
        return amounts
    
    def determine_loan_purpose(self, product: Dict[str, Any], detailed_product: Dict[str, Any]) -> str:
        """Determine loan purpose from product data"""
        try:
            text_fields = [
                product.get('description', ''),
                product.get('name', ''),
                str(detailed_product.get('eligibility', [])),
                str(detailed_product.get('constraints', []))
            ]
            
            combined_text = ' '.join(text_fields).lower()
            
            has_investment = any(word in combined_text for word in ['investment', 'investor', 'rental', 'non-owner'])
            has_owner_occ = any(phrase in combined_text for phrase in ['owner occupier', 'owner-occupier', 'ppor', 'principal place'])
            
            if has_investment and has_owner_occ:
                return "Both"
            elif has_investment:
                return "Investment"
            elif has_owner_occ:
                return "Owner Occupier"
            else:
                return "Both"  # Default for residential mortgages
                
        except Exception as e:
            logger.warning(f"Error determining loan purpose: {e}")
            return "Both"
    
    def determine_repayment_type(self, product: Dict[str, Any], detailed_product: Dict[str, Any]) -> str:
        """Determine repayment type from product data"""
        try:
            text_fields = [
                product.get('description', ''),
                str(detailed_product.get('features', [])),
                str(detailed_product.get('constraints', []))
            ]
            
            combined_text = ' '.join(text_fields).lower()
            
            has_pi = any(phrase in combined_text for phrase in ['principal and interest', 'p&i', 'principal & interest'])
            has_io = any(phrase in combined_text for phrase in ['interest only', 'interest-only', 'i/o'])
            
            if has_pi and has_io:
                return "Both"
            elif has_io:
                return "Interest Only"
            elif has_pi:
                return "Principal and Interest"
            else:
                return "Both"  # Default assumption
                
        except Exception as e:
            logger.warning(f"Error determining repayment type: {e}")
            return "Both"
    
    def scrape_comprehensive_cdr_data(self) -> List[ComprehensiveCDRProduct]:
        """Main method to scrape comprehensive CDR data"""
        try:
            # Step 1: Get CDR register for brand mapping
            logger.info("🏛️  Fetching CDR register...")
            self.fetch_cdr_register()
            
            # Step 2: Get aggregated mortgage data
            logger.info("🏠 Fetching aggregated residential mortgage data...")
            products = self.fetch_aggregated_mortgages()
            
            if not products:
                logger.error("No products found from aggregated data")
                return []
            
            # Step 3: Process products comprehensively
            logger.info(f"⚙️  Processing {len(products)} products...")
            processed_products = self.process_comprehensive_products(products)
            
            self.all_products = processed_products
            logger.info(f"✅ Successfully processed {len(processed_products)} comprehensive products")
            
            return processed_products
            
        except Exception as e:
            logger.error(f"Error during comprehensive CDR scraping: {e}")
            return []
    
    def save_to_csv(self, filename: str = None) -> str:
        """Save comprehensive CDR data to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_cdr_mortgages_{timestamp}.csv"
        
        try:
            if not self.all_products:
                logger.warning("No products to save")
                return filename
            
            # Comprehensive CSV fieldnames matching all data fields
            fieldnames = [
                'Brand ID', 'Brand Name', 'Product ID', 'Product Name', 'Category',
                'Description', 'Variable Rate', 'Fixed Rate 1Yr', 'Fixed Rate 2Yr', 
                'Fixed Rate 3Yr', 'Fixed Rate 4Yr', 'Fixed Rate 5Yr', 'Comparison Rate',
                'Loan Purpose', 'Repayment Type', 'Offset Available', 'Redraw Available',
                'Split Loan Available', 'Construction Available', 'Application Fee', 
                'Annual Fee', 'Monthly Fee', 'Exit Fee', 'Valuation Fee', 'Settlement Fee',
                'Other Fees', 'Features', 'Eligibility', 'Constraints', 'Minimum Amount',
                'Maximum Amount', 'Application URL', 'Last Updated', 'Monthly Repayment 300K',
                'Monthly Repayment 500K', 'Monthly Repayment 750K'
            ]
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in self.all_products:
                    row = {
                        'Brand ID': product.brand_id,
                        'Brand Name': product.brand_name,
                        'Product ID': product.product_id,
                        'Product Name': product.product_name,
                        'Category': product.product_category,
                        'Description': product.description,
                        'Variable Rate': product.variable_rate,
                        'Fixed Rate 1Yr': product.fixed_rate_1yr,
                        'Fixed Rate 2Yr': product.fixed_rate_2yr,
                        'Fixed Rate 3Yr': product.fixed_rate_3yr,
                        'Fixed Rate 4Yr': product.fixed_rate_4yr,
                        'Fixed Rate 5Yr': product.fixed_rate_5yr,
                        'Comparison Rate': product.comparison_rate,
                        'Loan Purpose': product.loan_purpose,
                        'Repayment Type': product.repayment_type,
                        'Offset Available': product.offset_available,
                        'Redraw Available': product.redraw_available,
                        'Split Loan Available': product.split_loan_available,
                        'Construction Available': product.construction_available,
                        'Application Fee': product.application_fee,
                        'Annual Fee': product.annual_fee,
                        'Monthly Fee': product.monthly_fee,
                        'Exit Fee': product.exit_fee,
                        'Valuation Fee': product.valuation_fee,
                        'Settlement Fee': product.settlement_fee,
                        'Other Fees': product.other_fees,
                        'Features': product.features,
                        'Eligibility': product.eligibility,
                        'Constraints': product.constraints,
                        'Minimum Amount': product.minimum_amount,
                        'Maximum Amount': product.maximum_amount,
                        'Application URL': product.application_url,
                        'Last Updated': product.last_updated,
                        'Monthly Repayment 300K': product.monthly_repayment_300k,
                        'Monthly Repayment 500K': product.monthly_repayment_500k,
                        'Monthly Repayment 750K': product.monthly_repayment_750k
                    }
                    writer.writerow(row)
            
            logger.info(f"Comprehensive CDR data saved to {filename}")
            
            # Generate comprehensive statistics
            self.print_comprehensive_statistics(filename)
            
            return filename
            
        except Exception as e:
            logger.error(f"Error saving comprehensive CDR data: {e}")
            raise
    
    def print_comprehensive_statistics(self, filename: str):
        """Print comprehensive statistics about the scraped data"""
        print(f"\n🎉 COMPREHENSIVE CDR MORTGAGE DATABASE CREATED")
        print("=" * 70)
        print(f"📊 Total Products: {len(self.all_products)}")
        print(f"🏛️  Unique Brands: {len(set(p.brand_name for p in self.all_products))}")
        print(f"💾 Data saved to: {filename}")
        
        # Rate statistics
        with_variable = len([p for p in self.all_products if p.variable_rate])
        with_fixed = len([p for p in self.all_products if any([p.fixed_rate_1yr, p.fixed_rate_2yr, p.fixed_rate_3yr, p.fixed_rate_4yr, p.fixed_rate_5yr])])
        with_comparison = len([p for p in self.all_products if p.comparison_rate])
        
        print(f"\n📈 Rate Coverage:")
        print(f"   • Variable rates: {with_variable} ({with_variable/len(self.all_products)*100:.1f}%)")
        print(f"   • Fixed rates: {with_fixed} ({with_fixed/len(self.all_products)*100:.1f}%)")
        print(f"   • Comparison rates: {with_comparison} ({with_comparison/len(self.all_products)*100:.1f}%)")
        
        # Feature statistics
        with_offset = len([p for p in self.all_products if p.offset_available == 'Y'])
        with_redraw = len([p for p in self.all_products if p.redraw_available == 'Y'])
        with_split = len([p for p in self.all_products if p.split_loan_available == 'Y'])
        
        print(f"\n🏠 Feature Coverage:")
        print(f"   • Offset accounts: {with_offset} ({with_offset/len(self.all_products)*100:.1f}%)")
        print(f"   • Redraw facility: {with_redraw} ({with_redraw/len(self.all_products)*100:.1f}%)")
        print(f"   • Split loans: {with_split} ({with_split/len(self.all_products)*100:.1f}%)")
        
        # Fee statistics
        with_app_fee = len([p for p in self.all_products if p.application_fee])
        with_annual_fee = len([p for p in self.all_products if p.annual_fee])
        
        print(f"\n💰 Fee Coverage:")
        print(f"   • Application fees: {with_app_fee} ({with_app_fee/len(self.all_products)*100:.1f}%)")
        print(f"   • Annual fees: {with_annual_fee} ({with_annual_fee/len(self.all_products)*100:.1f}%)")
        
        print(f"\n🎯 Data Sources:")
        print(f"   • CDR Register: {self.cdr_register_url}")
        print(f"   • Open Banking Tracker: {self.residential_mortgages_url}")
        print(f"   • Inspired by: https://github.com/LukePrior/mortgage-manager")
        
        print(f"\n📋 CSV includes 35 comprehensive columns covering:")
        print("   • Complete rate matrix (variable + 5 fixed terms)")
        print("   • Comprehensive fee breakdown (6+ fee types)")
        print("   • Advanced features (offset, redraw, split, construction)")
        print("   • Monthly repayment calculations for 3 loan amounts")
        print("   • Eligibility requirements and constraints")
        print("   • Brand mapping from official CDR register")

def main():
    """Main function to run the comprehensive CDR scraper"""
    print("🏛️  Comprehensive CDR Mortgage Database Scraper")
    print("Leveraging Open Banking Tracker & Official CDR Register")
    print("Inspired by LukePrior/mortgage-manager")
    print("=" * 70)
    
    scraper = ComprehensiveCDRScraper()
    
    try:
        products = scraper.scrape_comprehensive_cdr_data()
        
        if products:
            filename = scraper.save_to_csv()
            print(f"\n✅ SUCCESS: Comprehensive mortgage database created!")
            print(f"🔗 Based on the same data source as mortgage-manager")
            print(f"📈 Scales from 4 banks to 100+ financial institutions")
        else:
            print("❌ No products were found.")
            
    except Exception as e:
        logger.error(f"Comprehensive CDR scraping failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
