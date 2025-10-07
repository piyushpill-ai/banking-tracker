#!/usr/bin/env python3
"""
Real-Time CDR Data Pipeline

Replicates the LukePrior/mortgage-manager functionality but with live API calls
to get fresh, real-time mortgage data that can be refreshed monthly.
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
from urllib.parse import urljoin
import os
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class BankEndpoint:
    """Bank endpoint information from CDR register"""
    brand_id: str
    brand_name: str
    legal_entity_name: str
    industry: str
    product_base_uri: str
    public_base_uri: str
    status: str
    last_updated: str

@dataclass
class RealTimeHomeLoan:
    """Real-time home loan product structure"""
    # Source information
    brand_id: str
    brand_name: str
    legal_entity: str
    data_source_url: str
    
    # Product details
    product_id: str
    product_name: str
    product_category: str
    product_sub_category: str
    description: str
    
    # Rates (multiple possible)
    variable_rates: List[Dict[str, Any]]  # List of variable rate objects
    fixed_rates: List[Dict[str, Any]]     # List of fixed rate objects
    comparison_rate: str
    
    # Loan characteristics
    loan_purposes: List[str]              # Can be multiple
    repayment_types: List[str]           # Can be multiple
    
    # Features
    offset_available: bool
    redraw_available: bool
    split_loan_available: bool
    construction_available: bool
    features_list: List[str]
    
    # Fees
    application_fee: Optional[float]
    annual_fee: Optional[float]
    monthly_fee: Optional[float]
    exit_fee: Optional[float]
    other_fees: List[Dict[str, Any]]
    
    # Constraints and eligibility
    minimum_amount: Optional[float]
    maximum_amount: Optional[float]
    eligibility_criteria: List[str]
    constraints: List[str]
    
    # URLs and metadata
    application_uri: str
    additional_info_uri: str
    effective_from: str
    last_updated: str
    
    # Calculated fields
    monthly_repayment_300k: Optional[float]
    monthly_repayment_500k: Optional[float]
    monthly_repayment_750k: Optional[float]

class RealTimeCDRPipeline:
    """Real-time CDR data pipeline"""
    
    def __init__(self, output_dir: str = "cdr_data"):
        self.cdr_register_url = "https://api.cdr.gov.au/cdr-register/v1/banking/register"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Real-Time-CDR-Pipeline/1.0',
            'Accept': 'application/json',
            'x-v': '3'  # CDR API version
        })
        
        self.banks = []
        self.all_products = []
        self.errors = []
        
        # Rate limiting
        self.rate_limit_delay = 1.0  # Seconds between requests
        self.max_concurrent = 5      # Max concurrent requests
        
    def fetch_cdr_register(self) -> List[BankEndpoint]:
        """Fetch the complete CDR register with all banking institutions"""
        try:
            logger.info("🏛️  Fetching live CDR register...")
            response = self.session.get(self.cdr_register_url, timeout=30)
            
            if response.status_code == 200:
                register_data = response.json()
                banks = []
                
                for data_holder in register_data.get('data', []):
                    # Only process banking institutions
                    if data_holder.get('industry') != 'banking':
                        continue
                    
                    legal_entity_name = data_holder.get('legalEntityName', '')
                    
                    for brand in data_holder.get('dataHolderBrands', []):
                        brand_id = brand.get('brandId', '')
                        brand_name = brand.get('brandName', '')
                        status = brand.get('status', '')
                        last_updated = brand.get('lastUpdated', '')
                        
                        # Get endpoint details
                        endpoint_detail = brand.get('endpointDetail', {})
                        public_base_uri = endpoint_detail.get('publicBaseUri', '')
                        
                        if public_base_uri and status.upper() == 'ACTIVE':
                            # Construct product endpoint
                            product_base_uri = urljoin(public_base_uri, 'cds-au/v1/banking/products')
                            
                            bank = BankEndpoint(
                                brand_id=brand_id,
                                brand_name=brand_name,
                                legal_entity_name=legal_entity_name,
                                industry='banking',
                                product_base_uri=product_base_uri,
                                public_base_uri=public_base_uri,
                                status=status,
                                last_updated=last_updated
                            )
                            banks.append(bank)
                
                logger.info(f"✅ Found {len(banks)} active banking institutions")
                self.banks = banks
                
                # Save register data
                self.save_register_data(register_data)
                
                return banks
            else:
                logger.error(f"Failed to fetch CDR register: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching CDR register: {e}")
            return []
    
    def save_register_data(self, register_data: Dict[str, Any]):
        """Save the CDR register data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        register_file = self.output_dir / f"cdr_register_{timestamp}.json"
        
        with open(register_file, 'w') as f:
            json.dump(register_data, f, indent=2)
        
        logger.info(f"📄 CDR register saved to {register_file}")
    
    def fetch_bank_products(self, bank: BankEndpoint) -> List[Dict[str, Any]]:
        """Fetch products from a specific bank"""
        try:
            logger.info(f"🏦 Fetching products from {bank.brand_name}...")
            
            headers = {
                'x-v': '3',
                'Accept': 'application/json'
            }
            
            response = self.session.get(
                bank.product_base_uri, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('data', {}).get('products', [])
                
                # Filter for residential mortgages
                residential_products = []
                for product in products:
                    category = product.get('productCategory', '').upper()
                    if 'RESIDENTIAL' in category or 'MORTGAGE' in category:
                        # Add bank context to product
                        product['_bank_context'] = {
                            'brand_id': bank.brand_id,
                            'brand_name': bank.brand_name,
                            'legal_entity': bank.legal_entity_name,
                            'source_url': bank.product_base_uri
                        }
                        residential_products.append(product)
                
                logger.info(f"✅ {bank.brand_name}: {len(residential_products)} residential mortgage products")
                return residential_products
                
            else:
                error_msg = f"{bank.brand_name}: HTTP {response.status_code}"
                logger.warning(error_msg)
                self.errors.append(error_msg)
                return []
                
        except Exception as e:
            error_msg = f"{bank.brand_name}: {str(e)}"
            logger.warning(error_msg)
            self.errors.append(error_msg)
            return []
    
    def fetch_detailed_product(self, bank: BankEndpoint, product_id: str) -> Dict[str, Any]:
        """Fetch detailed product information"""
        try:
            detail_url = f"{bank.product_base_uri}/{product_id}"
            
            headers = {
                'x-v': '3',
                'Accept': 'application/json'
            }
            
            response = self.session.get(detail_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                return {}
                
        except Exception as e:
            logger.debug(f"Could not fetch detailed product {product_id} from {bank.brand_name}: {e}")
            return {}
    
    def process_product_to_structured_format(self, product: Dict[str, Any]) -> RealTimeHomeLoan:
        """Convert raw product data to structured format"""
        bank_context = product.get('_bank_context', {})
        
        # Basic product info
        product_id = product.get('productId', '')
        product_name = product.get('name', '')
        product_category = product.get('productCategory', '')
        product_sub_category = product.get('productSubCategory', '')
        description = product.get('description', '')
        
        # Extract rates
        variable_rates = []
        fixed_rates = []
        comparison_rate = ""
        
        # Extract loan purposes and repayment types
        loan_purposes = set()
        repayment_types = set()
        
        # For now, use basic product structure - we'll enhance with detailed calls
        
        # Features - basic extraction
        features_list = []
        offset_available = False
        redraw_available = False
        split_loan_available = False
        construction_available = False
        
        # Check product name and description for features
        text_content = f"{product_name} {description}".lower()
        if 'offset' in text_content:
            offset_available = True
            features_list.append('Offset Account')
        if 'redraw' in text_content:
            redraw_available = True
            features_list.append('Redraw Facility')
        if 'split' in text_content or 'portion' in text_content:
            split_loan_available = True
            features_list.append('Split Loan')
        if 'construction' in text_content or 'building' in text_content:
            construction_available = True
            features_list.append('Construction Loan')
        
        # Default values for now - will be enhanced with detailed API calls
        application_fee = None
        annual_fee = None
        monthly_fee = None
        exit_fee = None
        other_fees = []
        
        minimum_amount = None
        maximum_amount = None
        eligibility_criteria = []
        constraints = []
        
        application_uri = product.get('applicationUri', '')
        additional_info_uri = product.get('additionalInformationUri', '')
        effective_from = product.get('effectiveFrom', '')
        last_updated = product.get('lastUpdated', '')
        
        return RealTimeHomeLoan(
            brand_id=bank_context.get('brand_id', ''),
            brand_name=bank_context.get('brand_name', ''),
            legal_entity=bank_context.get('legal_entity', ''),
            data_source_url=bank_context.get('source_url', ''),
            product_id=product_id,
            product_name=product_name,
            product_category=product_category,
            product_sub_category=product_sub_category,
            description=description,
            variable_rates=variable_rates,
            fixed_rates=fixed_rates,
            comparison_rate=comparison_rate,
            loan_purposes=list(loan_purposes) if loan_purposes else ['Not Specified'],
            repayment_types=list(repayment_types) if repayment_types else ['Not Specified'],
            offset_available=offset_available,
            redraw_available=redraw_available,
            split_loan_available=split_loan_available,
            construction_available=construction_available,
            features_list=features_list,
            application_fee=application_fee,
            annual_fee=annual_fee,
            monthly_fee=monthly_fee,
            exit_fee=exit_fee,
            other_fees=other_fees,
            minimum_amount=minimum_amount,
            maximum_amount=maximum_amount,
            eligibility_criteria=eligibility_criteria,
            constraints=constraints,
            application_uri=application_uri,
            additional_info_uri=additional_info_uri,
            effective_from=effective_from,
            last_updated=last_updated,
            monthly_repayment_300k=None,
            monthly_repayment_500k=None,
            monthly_repayment_750k=None
        )
    
    def fetch_all_products_parallel(self) -> List[RealTimeHomeLoan]:
        """Fetch products from all banks in parallel"""
        all_products = []
        
        logger.info(f"🚀 Starting parallel data collection from {len(self.banks)} banks...")
        
        # Use ThreadPoolExecutor for parallel requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Submit all bank requests
            future_to_bank = {
                executor.submit(self.fetch_bank_products, bank): bank 
                for bank in self.banks
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_bank):
                bank = future_to_bank[future]
                try:
                    products = future.result()
                    
                    # Process each product
                    for product in products:
                        structured_product = self.process_product_to_structured_format(product)
                        all_products.append(structured_product)
                        
                    # Rate limiting
                    time.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    error_msg = f"Error processing {bank.brand_name}: {e}"
                    logger.error(error_msg)
                    self.errors.append(error_msg)
        
        logger.info(f"✅ Collected {len(all_products)} total products from real-time APIs")
        self.all_products = all_products
        return all_products
    
    def save_products_to_formats(self) -> Dict[str, str]:
        """Save products to multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        files_created = {}
        
        # 1. Save as JSON (complete data)
        json_file = self.output_dir / f"realtime_mortgages_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump([asdict(product) for product in self.all_products], f, indent=2, default=str)
        files_created['json'] = str(json_file)
        
        # 2. Save as CSV (flattened for easy use)
        csv_file = self.output_dir / f"realtime_mortgages_{timestamp}.csv"
        self.save_csv_format(csv_file)
        files_created['csv'] = str(csv_file)
        
        # 3. Save summary statistics
        summary_file = self.output_dir / f"pipeline_summary_{timestamp}.json"
        self.save_pipeline_summary(summary_file)
        files_created['summary'] = str(summary_file)
        
        return files_created
    
    def save_csv_format(self, filename: Path):
        """Save products in CSV format"""
        fieldnames = [
            'Brand ID', 'Brand Name', 'Legal Entity', 'Product ID', 'Product Name',
            'Category', 'Sub Category', 'Description', 'Loan Purposes', 'Repayment Types',
            'Offset Available', 'Redraw Available', 'Split Loan Available', 
            'Construction Available', 'Features', 'Application Fee', 'Annual Fee',
            'Monthly Fee', 'Exit Fee', 'Minimum Amount', 'Maximum Amount',
            'Application URL', 'Data Source URL', 'Last Updated'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in self.all_products:
                row = {
                    'Brand ID': product.brand_id,
                    'Brand Name': product.brand_name,
                    'Legal Entity': product.legal_entity,
                    'Product ID': product.product_id,
                    'Product Name': product.product_name,
                    'Category': product.product_category,
                    'Sub Category': product.product_sub_category,
                    'Description': product.description[:200] + "..." if len(product.description) > 200 else product.description,
                    'Loan Purposes': ' | '.join(product.loan_purposes),
                    'Repayment Types': ' | '.join(product.repayment_types),
                    'Offset Available': 'Y' if product.offset_available else 'N',
                    'Redraw Available': 'Y' if product.redraw_available else 'N',
                    'Split Loan Available': 'Y' if product.split_loan_available else 'N',
                    'Construction Available': 'Y' if product.construction_available else 'N',
                    'Features': ' | '.join(product.features_list),
                    'Application Fee': f"${product.application_fee:.0f}" if product.application_fee else '',
                    'Annual Fee': f"${product.annual_fee:.0f}" if product.annual_fee else '',
                    'Monthly Fee': f"${product.monthly_fee:.0f}" if product.monthly_fee else '',
                    'Exit Fee': f"${product.exit_fee:.0f}" if product.exit_fee else '',
                    'Minimum Amount': f"${product.minimum_amount:,.0f}" if product.minimum_amount else '',
                    'Maximum Amount': f"${product.maximum_amount:,.0f}" if product.maximum_amount else '',
                    'Application URL': product.application_uri,
                    'Data Source URL': product.data_source_url,
                    'Last Updated': product.last_updated
                }
                writer.writerow(row)
    
    def save_pipeline_summary(self, filename: Path):
        """Save pipeline execution summary"""
        summary = {
            'execution_timestamp': datetime.now().isoformat(),
            'total_banks_attempted': len(self.banks),
            'total_products_collected': len(self.all_products),
            'errors_encountered': len(self.errors),
            'error_details': self.errors,
            'banks_processed': [
                {
                    'brand_id': bank.brand_id,
                    'brand_name': bank.brand_name,
                    'status': bank.status,
                    'product_count': len([p for p in self.all_products if p.brand_id == bank.brand_id])
                }
                for bank in self.banks
            ],
            'feature_statistics': self.calculate_feature_statistics(),
            'data_freshness': {
                'pipeline_run': datetime.now().isoformat(),
                'oldest_product_update': min([p.last_updated for p in self.all_products if p.last_updated], default=''),
                'newest_product_update': max([p.last_updated for p in self.all_products if p.last_updated], default='')
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
    
    def calculate_feature_statistics(self) -> Dict[str, Any]:
        """Calculate statistics about the collected data"""
        if not self.all_products:
            return {}
        
        total = len(self.all_products)
        
        return {
            'total_products': total,
            'unique_brands': len(set(p.brand_name for p in self.all_products)),
            'products_with_offset': len([p for p in self.all_products if p.offset_available]),
            'products_with_redraw': len([p for p in self.all_products if p.redraw_available]),
            'products_with_split_loan': len([p for p in self.all_products if p.split_loan_available]),
            'products_with_construction': len([p for p in self.all_products if p.construction_available]),
            'offset_percentage': len([p for p in self.all_products if p.offset_available]) / total * 100,
            'redraw_percentage': len([p for p in self.all_products if p.redraw_available]) / total * 100
        }
    
    def run_full_pipeline(self) -> Dict[str, str]:
        """Run the complete real-time data pipeline"""
        logger.info("🚀 Starting Real-Time CDR Data Pipeline")
        logger.info("=" * 50)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Fetch CDR register
            banks = self.fetch_cdr_register()
            if not banks:
                raise Exception("No banks found in CDR register")
            
            # Step 2: Fetch products from all banks
            products = self.fetch_all_products_parallel()
            
            # Step 3: Save results
            files_created = self.save_products_to_formats()
            
            # Step 4: Print summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            self.print_pipeline_summary(duration, files_created)
            
            return files_created
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
    
    def print_pipeline_summary(self, duration: timedelta, files_created: Dict[str, str]):
        """Print pipeline execution summary"""
        print(f"\n🎉 REAL-TIME CDR PIPELINE COMPLETE!")
        print("=" * 50)
        print(f"⏱️  Execution time: {duration}")
        print(f"🏛️  Banks processed: {len(self.banks)}")
        print(f"📊 Products collected: {len(self.all_products)}")
        print(f"❌ Errors encountered: {len(self.errors)}")
        
        if self.all_products:
            stats = self.calculate_feature_statistics()
            print(f"\n📈 Data Quality:")
            print(f"   • Unique brands: {stats['unique_brands']}")
            print(f"   • Products with offset: {stats['products_with_offset']} ({stats['offset_percentage']:.1f}%)")
            print(f"   • Products with redraw: {stats['products_with_redraw']} ({stats['redraw_percentage']:.1f}%)")
        
        print(f"\n📁 Files created:")
        for format_type, filepath in files_created.items():
            print(f"   • {format_type.upper()}: {filepath}")
        
        print(f"\n🔄 Data Freshness: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("💡 Schedule this script to run monthly for fresh data!")

def main():
    """Main function to run the real-time pipeline"""
    pipeline = RealTimeCDRPipeline()
    
    try:
        files_created = pipeline.run_full_pipeline()
        print(f"\n✅ SUCCESS: Real-time CDR data pipeline completed!")
        print(f"🔗 Fresh data ready for use - no dependency on outdated repositories!")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())


