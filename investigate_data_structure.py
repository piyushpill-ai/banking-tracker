#!/usr/bin/env python3
"""
Investigate the actual data structure to improve feature extraction
"""

import json
import requests
from pprint import pprint

def investigate_open_banking_data():
    """Investigate the actual structure of Open Banking Tracker data"""
    
    # Fetch a sample of the data
    url = "https://raw.githubusercontent.com/LukePrior/open-banking-tracker/main/aggregate/RESIDENTIAL_MORTGAGES/data.json"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            print(f"Total products: {len(data)}")
            print("\n=== SAMPLE PRODUCT STRUCTURE ===")
            
            # Look at first few products in detail
            for i, product in enumerate(data[:3]):
                print(f"\n--- Product {i+1} ---")
                print(f"Brand ID: {product.get('brandId', 'N/A')}")
                print(f"Product ID: {product.get('productId', 'N/A')}")
                print(f"Name: {product.get('name', 'N/A')}")
                print(f"Description: {product.get('description', 'N/A')[:200]}...")
                
                # Check rate structure
                rates = product.get('rate', [])
                print(f"\nRates ({len(rates)} found):")
                for j, rate in enumerate(rates[:3]):
                    print(f"  Rate {j+1}: {rate}")
                
                # Look for any feature-related fields
                print(f"\nAll available keys: {list(product.keys())}")
                
                # Check if there are any feature indicators in description
                desc = product.get('description', '').lower()
                features_found = []
                if 'offset' in desc:
                    features_found.append('offset')
                if 'redraw' in desc:
                    features_found.append('redraw')
                if 'investment' in desc:
                    features_found.append('investment')
                if 'owner occupier' in desc or 'owner-occupier' in desc:
                    features_found.append('owner-occupier')
                if 'principal and interest' in desc or 'p&i' in desc:
                    features_found.append('principal-interest')
                if 'interest only' in desc or 'interest-only' in desc:
                    features_found.append('interest-only')
                
                print(f"Features detected in description: {features_found}")
                
                if i == 0:  # For first product, try to get detailed data
                    brand_id = product.get('brandId', '')
                    product_id = product.get('productId', '')
                    detail_url = f"https://raw.githubusercontent.com/LukePrior/open-banking-tracker/main/data/{brand_id}/{product_id}.json"
                    
                    print(f"\nTrying detailed URL: {detail_url}")
                    try:
                        detail_response = requests.get(detail_url, timeout=10)
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            print("✅ Detailed data available!")
                            print(f"Detailed keys: {list(detail_data.keys())}")
                            
                            # Check for features
                            if 'features' in detail_data:
                                print(f"Features found: {detail_data['features'][:3] if detail_data['features'] else 'None'}")
                            
                            # Check for fees  
                            if 'fees' in detail_data:
                                print(f"Fees found: {detail_data['fees'][:3] if detail_data['fees'] else 'None'}")
                                
                            # Check for eligibility
                            if 'eligibility' in detail_data:
                                print(f"Eligibility found: {detail_data['eligibility'][:2] if detail_data['eligibility'] else 'None'}")
                                
                        else:
                            print(f"❌ Detailed data not available: {detail_response.status_code}")
                    except Exception as e:
                        print(f"❌ Error fetching detailed data: {e}")
            
            # Analyze rate types across all products
            print("\n=== RATE TYPE ANALYSIS ===")
            rate_types = {}
            repayment_types = {}
            
            for product in data[:100]:  # Check first 100 products
                rates = product.get('rate', [])
                for rate in rates:
                    rate_type = rate.get('lendingRateType', 'Unknown')
                    rate_types[rate_type] = rate_types.get(rate_type, 0) + 1
                    
                    repayment_type = rate.get('repaymentType', 'Unknown')
                    repayment_types[repayment_type] = repayment_types.get(repayment_type, 0) + 1
            
            print("Rate types found:")
            for rate_type, count in sorted(rate_types.items()):
                print(f"  {rate_type}: {count}")
                
            print("\nRepayment types found:")
            for repayment_type, count in sorted(repayment_types.items()):
                print(f"  {repayment_type}: {count}")
                
            # Check for products with specific features in descriptions
            print("\n=== FEATURE DETECTION IN DESCRIPTIONS ===")
            offset_count = 0
            redraw_count = 0
            investment_count = 0
            owner_occ_count = 0
            
            for product in data[:500]:  # Check first 500 products
                desc = (product.get('description', '') + ' ' + product.get('name', '')).lower()
                if 'offset' in desc:
                    offset_count += 1
                if 'redraw' in desc:
                    redraw_count += 1
                if 'investment' in desc:
                    investment_count += 1
                if any(phrase in desc for phrase in ['owner occupier', 'owner-occupier', 'ppor']):
                    owner_occ_count += 1
            
            print(f"Products with 'offset' in description: {offset_count}/500")
            print(f"Products with 'redraw' in description: {redraw_count}/500")
            print(f"Products with 'investment' in description: {investment_count}/500") 
            print(f"Products with 'owner occupier' in description: {owner_occ_count}/500")
            
        else:
            print(f"Failed to fetch data: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    investigate_open_banking_data()


