#!/usr/bin/env python3
"""
Improved CDR Scraper with Proper Feature Extraction

Now correctly extracts offset, redraw, loan purpose, and repayment type
from the actual data structure discovered in the Open Banking Tracker.
"""

import json
import csv
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ImprovedHomeLoanProduct:
    """Improved data structure with proper feature extraction"""
    brand_id: str
    brand_name: str
    product_id: str
    product_name: str
    description: str
    variable_rate: str
    fixed_rate_1yr: str
    fixed_rate_2yr: str
    fixed_rate_3yr: str
    fixed_rate_4yr: str
    fixed_rate_5yr: str
    comparison_rate: str
    loan_purpose: str  # Properly extracted from rate.purpose
    repayment_type: str  # Properly extracted from rate.repaymentType
    offset_available: str  # From direct offset field
    redraw_available: str  # From direct redraw field
    application_fee: str
    annual_fee: str
    exit_fee: str
    other_fees: str
    features_summary: str
    application_url: str
    last_updated: str
    monthly_repayment_300k: str
    monthly_repayment_500k: str
    monthly_repayment_750k: str

class ImprovedCDRScraper:
    """Improved scraper with proper feature extraction"""
    
    def __init__(self):
        self.residential_mortgages_url = "https://raw.githubusercontent.com/LukePrior/open-banking-tracker/main/aggregate/RESIDENTIAL_MORTGAGES/data.json"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
        self.all_products = []
    
    def fetch_mortgage_data(self) -> List[Dict[str, Any]]:
        """Fetch residential mortgage data"""
        try:
            logger.info("Fetching mortgage data with improved extraction...")
            response = self.session.get(self.residential_mortgages_url, timeout=60)
            
            if response.status_code == 200:
                products = response.json()
                logger.info(f"Retrieved {len(products)} mortgage products")
                return products
            else:
                logger.warning(f"Failed to fetch data: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching mortgage data: {e}")
            return []
    
    def extract_rates_improved(self, product: Dict[str, Any]) -> Dict[str, str]:
        """Extract rates with improved logic"""
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
                        else:
                            # If no period specified, put in 3yr as default
                            if not rates['fixed_rate_3yr']:
                                rates['fixed_rate_3yr'] = rate_str
            
        except Exception as e:
            logger.warning(f"Error extracting rates: {e}")
        
        return rates
    
    def extract_loan_purpose_improved(self, product: Dict[str, Any]) -> str:
        """Extract loan purpose from rate.purpose field"""
        try:
            rate_data = product.get('rate', [])
            purposes = set()
            
            for rate in rate_data:
                purpose = rate.get('purpose', '').upper()
                if purpose:
                    purposes.add(purpose)
            
            if not purposes:
                return "Not Specified"
            elif len(purposes) == 1:
                purpose = list(purposes)[0]
                if purpose == 'INVESTMENT':
                    return "Investment"
                elif purpose == 'OWNER_OCCUPIED':
                    return "Owner Occupier"
                else:
                    return purpose.title()
            else:
                # Multiple purposes found
                has_investment = 'INVESTMENT' in purposes
                has_owner_occ = 'OWNER_OCCUPIED' in purposes
                
                if has_investment and has_owner_occ:
                    return "Both"
                elif has_investment:
                    return "Investment"
                elif has_owner_occ:
                    return "Owner Occupier"
                else:
                    return "Both"
                    
        except Exception as e:
            logger.warning(f"Error extracting loan purpose: {e}")
            return "Not Specified"
    
    def extract_repayment_type_improved(self, product: Dict[str, Any]) -> str:
        """Extract repayment type from rate.repaymentType field"""
        try:
            rate_data = product.get('rate', [])
            repayment_types = set()
            
            for rate in rate_data:
                repayment_type = rate.get('repaymentType', '').upper()
                if repayment_type:
                    repayment_types.add(repayment_type)
            
            if not repayment_types:
                return "Not Specified"
            elif len(repayment_types) == 1:
                repayment_type = list(repayment_types)[0]
                if repayment_type == 'PRINCIPAL_AND_INTEREST':
                    return "Principal and Interest"
                elif repayment_type == 'INTEREST_ONLY':
                    return "Interest Only"
                else:
                    return repayment_type.replace('_', ' ').title()
            else:
                # Multiple repayment types found
                has_pi = 'PRINCIPAL_AND_INTEREST' in repayment_types
                has_io = 'INTEREST_ONLY' in repayment_types
                
                if has_pi and has_io:
                    return "Both"
                elif has_pi:
                    return "Principal and Interest"
                elif has_io:
                    return "Interest Only"
                else:
                    return "Both"
                    
        except Exception as e:
            logger.warning(f"Error extracting repayment type: {e}")
            return "Not Specified"
    
    def extract_features_improved(self, product: Dict[str, Any]) -> Dict[str, str]:
        """Extract features from direct offset/redraw fields"""
        features = {
            'offset_available': 'N',
            'redraw_available': 'N',
            'features_summary': ''
        }
        
        try:
            # Check direct offset field
            offset = product.get('offset')
            if offset is True or (isinstance(offset, str) and offset.lower() in ['true', 'yes', 'y', '1']):
                features['offset_available'] = 'Y'
            
            # Check direct redraw field  
            redraw = product.get('redraw')
            if redraw is True or (isinstance(redraw, str) and redraw.lower() in ['true', 'yes', 'y', '1']):
                features['redraw_available'] = 'Y'
            
            # Create features summary
            feature_list = []
            if features['offset_available'] == 'Y':
                feature_list.append('Offset Account')
            if features['redraw_available'] == 'Y':
                feature_list.append('Redraw Facility')
            
            # Check for other features in product name or any description
            product_name = product.get('productName', '').lower()
            brand_name = product.get('brandName', '').lower()
            
            if any(word in product_name or word in brand_name for word in ['package', 'premium', 'advantage']):
                feature_list.append('Package Product')
            
            if any(word in product_name for word in ['construction', 'building']):
                feature_list.append('Construction Loan')
                
            if any(word in product_name for word in ['split', 'portion']):
                feature_list.append('Split Loan Option')
            
            features['features_summary'] = ' | '.join(feature_list) if feature_list else ''
            
        except Exception as e:
            logger.warning(f"Error extracting features: {e}")
        
        return features
    
    def calculate_repayments_improved(self, rates: Dict[str, str]) -> Dict[str, str]:
        """Calculate monthly repayments for standard amounts"""
        repayments = {
            'monthly_repayment_300k': '',
            'monthly_repayment_500k': '',
            'monthly_repayment_750k': ''
        }
        
        try:
            # Use variable rate first, then fixed rates as fallback
            rate_str = (rates.get('variable_rate') or 
                       rates.get('fixed_rate_1yr') or 
                       rates.get('fixed_rate_2yr') or 
                       rates.get('fixed_rate_3yr'))
            
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
            
        except Exception as e:
            logger.warning(f"Error calculating repayments: {e}")
        
        return repayments
    
    def process_products_improved(self, products: List[Dict[str, Any]]) -> List[ImprovedHomeLoanProduct]:
        """Process products with improved feature extraction"""
        processed_products = []
        
        for i, product in enumerate(products):
            try:
                if i % 100 == 0:
                    logger.info(f"Processing product {i+1}/{len(products)}")
                
                # Extract basic info
                brand_id = product.get('brandId', '')
                brand_name = product.get('brandName', f'Brand-{brand_id}')
                product_id = product.get('productId', '')
                product_name = product.get('productName', 'Unnamed Product')
                
                # Extract rates
                rates = self.extract_rates_improved(product)
                
                # Extract loan purpose and repayment type (the key fix!)
                loan_purpose = self.extract_loan_purpose_improved(product)
                repayment_type = self.extract_repayment_type_improved(product)
                
                # Extract features (the other key fix!)
                features = self.extract_features_improved(product)
                
                # Calculate repayments
                repayments = self.calculate_repayments_improved(rates)
                
                improved_product = ImprovedHomeLoanProduct(
                    brand_id=brand_id,
                    brand_name=brand_name,
                    product_id=product_id,
                    product_name=product_name,
                    description=f"Product from {brand_name}",
                    variable_rate=rates['variable_rate'],
                    fixed_rate_1yr=rates['fixed_rate_1yr'],
                    fixed_rate_2yr=rates['fixed_rate_2yr'],
                    fixed_rate_3yr=rates['fixed_rate_3yr'],
                    fixed_rate_4yr=rates['fixed_rate_4yr'],
                    fixed_rate_5yr=rates['fixed_rate_5yr'],
                    comparison_rate=rates['comparison_rate'],
                    loan_purpose=loan_purpose,  # Now properly extracted!
                    repayment_type=repayment_type,  # Now properly extracted!
                    offset_available=features['offset_available'],  # Now properly extracted!
                    redraw_available=features['redraw_available'],  # Now properly extracted!
                    application_fee='',
                    annual_fee='',
                    exit_fee='',
                    other_fees='',
                    features_summary=features['features_summary'],
                    application_url='',
                    last_updated='',
                    monthly_repayment_300k=repayments['monthly_repayment_300k'],
                    monthly_repayment_500k=repayments['monthly_repayment_500k'],
                    monthly_repayment_750k=repayments['monthly_repayment_750k']
                )
                
                processed_products.append(improved_product)
                
            except Exception as e:
                logger.warning(f"Error processing product {i}: {e}")
                continue
        
        return processed_products
    
    def scrape_improved_data(self) -> List[ImprovedHomeLoanProduct]:
        """Main method with improved extraction"""
        try:
            # Fetch data
            products = self.fetch_mortgage_data()
            
            if not products:
                logger.error("No products found")
                return []
            
            # Process with improved extraction
            processed_products = self.process_products_improved(products)
            
            self.all_products = processed_products
            logger.info(f"Successfully processed {len(processed_products)} products with improved features")
            
            return processed_products
            
        except Exception as e:
            logger.error(f"Error during improved scraping: {e}")
            return []
    
    def save_improved_csv(self, filename: str = None) -> str:
        """Save improved data to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"improved_home_loans_{timestamp}.csv"
        
        try:
            if not self.all_products:
                logger.warning("No products to save")
                return filename
            
            # CSV fieldnames
            fieldnames = [
                'Brand ID', 'Brand Name', 'Product ID', 'Product Name', 'Description',
                'Variable Rate', 'Fixed Rate 1Yr', 'Fixed Rate 2Yr', 'Fixed Rate 3Yr', 
                'Fixed Rate 4Yr', 'Fixed Rate 5Yr', 'Comparison Rate',
                'Loan Purpose', 'Repayment Type', 'Offset Available', 'Redraw Available',
                'Application Fee', 'Annual Fee', 'Exit Fee', 'Other Fees', 'Features',
                'Application URL', 'Last Updated', 'Monthly Repayment 300K',
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
                        'Application Fee': product.application_fee,
                        'Annual Fee': product.annual_fee,
                        'Exit Fee': product.exit_fee,
                        'Other Fees': product.other_fees,
                        'Features': product.features_summary,
                        'Application URL': product.application_url,
                        'Last Updated': product.last_updated,
                        'Monthly Repayment 300K': product.monthly_repayment_300k,
                        'Monthly Repayment 500K': product.monthly_repayment_500k,
                        'Monthly Repayment 750K': product.monthly_repayment_750k
                    }
                    writer.writerow(row)
            
            # Generate improved statistics
            self.print_improved_statistics(filename)
            
            return filename
            
        except Exception as e:
            logger.error(f"Error saving improved data: {e}")
            raise
    
    def print_improved_statistics(self, filename: str):
        """Print statistics with proper feature detection"""
        print(f"\n🎉 IMPROVED FEATURE EXTRACTION COMPLETE!")
        print("=" * 60)
        print(f"📊 Total Products: {len(self.all_products)}")
        print(f"💾 Data saved to: {filename}")
        
        # Loan purpose statistics
        loan_purposes = {}
        for product in self.all_products:
            purpose = product.loan_purpose
            loan_purposes[purpose] = loan_purposes.get(purpose, 0) + 1
        
        print(f"\n🏠 Loan Purpose Distribution:")
        for purpose, count in sorted(loan_purposes.items()):
            percentage = count / len(self.all_products) * 100
            print(f"   • {purpose}: {count} ({percentage:.1f}%)")
        
        # Repayment type statistics
        repayment_types = {}
        for product in self.all_products:
            rep_type = product.repayment_type
            repayment_types[rep_type] = repayment_types.get(rep_type, 0) + 1
        
        print(f"\n💳 Repayment Type Distribution:")
        for rep_type, count in sorted(repayment_types.items()):
            percentage = count / len(self.all_products) * 100
            print(f"   • {rep_type}: {count} ({percentage:.1f}%)")
        
        # Feature statistics
        with_offset = len([p for p in self.all_products if p.offset_available == 'Y'])
        with_redraw = len([p for p in self.all_products if p.redraw_available == 'Y'])
        with_features = len([p for p in self.all_products if p.features_summary])
        
        print(f"\n✨ Feature Coverage:")
        print(f"   • Offset accounts: {with_offset} ({with_offset/len(self.all_products)*100:.1f}%)")
        print(f"   • Redraw facility: {with_redraw} ({with_redraw/len(self.all_products)*100:.1f}%)")
        print(f"   • Products with features: {with_features} ({with_features/len(self.all_products)*100:.1f}%)")
        
        # Rate statistics
        with_variable = len([p for p in self.all_products if p.variable_rate])
        with_fixed = len([p for p in self.all_products if any([p.fixed_rate_1yr, p.fixed_rate_2yr, p.fixed_rate_3yr, p.fixed_rate_4yr, p.fixed_rate_5yr])])
        
        print(f"\n📈 Rate Coverage:")
        print(f"   • Variable rates: {with_variable} ({with_variable/len(self.all_products)*100:.1f}%)")
        print(f"   • Fixed rates: {with_fixed} ({with_fixed/len(self.all_products)*100:.1f}%)")

def main():
    """Main function with improved extraction"""
    print("🔧 IMPROVED Home Loan Feature Extractor")
    print("Fixing offset, redraw, loan purpose, and repayment type detection")
    print("=" * 65)
    
    scraper = ImprovedCDRScraper()
    
    try:
        products = scraper.scrape_improved_data()
        
        if products:
            filename = scraper.save_improved_csv()
            print(f"\n✅ SUCCESS: Improved feature extraction complete!")
            print(f"🎯 Now with proper loan purpose, repayment type, offset & redraw detection")
        else:
            print("❌ No products were found.")
            
    except Exception as e:
        logger.error(f"Improved scraping failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()


