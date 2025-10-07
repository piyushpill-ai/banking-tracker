#!/usr/bin/env python3
"""
Generate comprehensive bank list from CDR register API
This creates a complete, up-to-date list of all Australian banking institutions
"""

import requests
import json
import time
from typing import List, Dict

def fetch_cdr_banking_data():
    """Fetch all banking data holders from CDR register"""
    print("🔍 Fetching comprehensive banking data from CDR register...")
    
    url = "https://api.cdr.gov.au/cdr-register/v1/all/data-holders/brands/summary"
    headers = {"x-v": "1"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Fetched {len(data['data'])} total brands from CDR register")
        
        # Filter for banking only
        banking_brands = []
        for brand in data['data']:
            industries = brand.get('industries', [])
            if 'banking' in industries:
                banking_brands.append(brand)
        
        print(f"🏦 Found {len(banking_brands)} banking institutions")
        return banking_brands
        
    except Exception as e:
        print(f"❌ Error fetching CDR data: {e}")
        return []

def process_banking_brands(brands: List[Dict]) -> List[tuple]:
    """Process banking brands into our format"""
    processed_banks = []
    
    for brand in brands:
        brand_name = brand.get('brandName', 'Unknown Bank')
        public_base_uri = brand.get('publicBaseUri', '')
        logo_uri = brand.get('logoUri', '')
        
        if not public_base_uri:
            print(f"⚠️ {brand_name}: No public base URI")
            continue
            
        # Construct products endpoint
        products_endpoint = construct_products_endpoint(public_base_uri)
        
        # Generate brand ID (simplified)
        brand_id = generate_brand_id(brand_name)
        
        processed_banks.append((brand_name, brand_id, products_endpoint, public_base_uri, logo_uri))
        print(f"✅ {brand_name}: {products_endpoint}")
    
    return processed_banks

def construct_products_endpoint(base_uri: str) -> str:
    """Construct CDS products endpoint from base URI"""
    if not base_uri.endswith('/'):
        base_uri += '/'
    
    # Remove common trailing paths that might interfere
    if base_uri.endswith('/api/'):
        base_uri = base_uri[:-4]
    elif base_uri.endswith('/public/'):
        # Keep /public/ as it's often needed
        pass
    elif base_uri.endswith('/openbanking/'):
        base_uri = base_uri[:-12]
    elif base_uri.endswith('/OpenBanking/'):
        base_uri = base_uri[:-12]
    
    # Ensure trailing slash
    if not base_uri.endswith('/'):
        base_uri += '/'
    
    # Construct the CDS products endpoint
    products_endpoint = f"{base_uri}cds-au/v1/banking/products"
    
    return products_endpoint

def generate_brand_id(brand_name: str) -> str:
    """Generate a simple brand ID from brand name"""
    # Clean up the name and create ID
    clean_name = brand_name.lower()
    clean_name = clean_name.replace(' ', '-')
    clean_name = clean_name.replace('.', '')
    clean_name = clean_name.replace('&', 'and')
    clean_name = clean_name.replace('(', '').replace(')', '')
    clean_name = clean_name.replace(',', '')
    clean_name = clean_name.replace("'", '')
    clean_name = clean_name.replace('"', '')
    
    # Limit length
    if len(clean_name) > 50:
        clean_name = clean_name[:50]
    
    return clean_name

def save_bank_list(banks: List[tuple]):
    """Save the comprehensive bank list"""
    timestamp = int(time.time())
    
    # Save as Python file for direct import
    py_file = f"comprehensive_bank_list_{timestamp}.py"
    with open(py_file, 'w') as f:
        f.write("#!/usr/bin/env python3\n")
        f.write('"""\n')
        f.write("Comprehensive Australian Banking Institution List\n")
        f.write(f"Generated from CDR Register API: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Banks: {len(banks)}\n")
        f.write('"""\n\n')
        
        f.write("# Format: (Bank Name, Brand ID, Products Endpoint, Base URI, Logo URI)\n")
        f.write("COMPREHENSIVE_BANK_LIST = [\n")
        
        for bank_name, brand_id, products_endpoint, base_uri, logo_uri in banks:
            f.write(f'    ("{bank_name}", "{brand_id}", "{products_endpoint}", "{base_uri}", "{logo_uri}"),\n')
        
        f.write("]\n\n")
        
        # Add convenience functions
        f.write("def get_bank_endpoints():\n")
        f.write('    """Get list of (name, brand_id, endpoint) tuples for luke_prior_realtime.py"""\n')
        f.write("    return [(name, brand_id, endpoint) for name, brand_id, endpoint, _, _ in COMPREHENSIVE_BANK_LIST]\n\n")
        
        f.write("def get_bank_by_name(name):\n")
        f.write('    """Get bank details by name"""\n')
        f.write("    for bank in COMPREHENSIVE_BANK_LIST:\n")
        f.write("        if bank[0] == name:\n")
        f.write("            return bank\n")
        f.write("    return None\n\n")
        
        f.write("def get_major_banks():\n")
        f.write('    """Get the Big 4 + major banks"""\n')
        f.write("    major_bank_names = ['ANZ', 'CommBank', 'NATIONAL AUSTRALIA BANK', 'Westpac', \n")
        f.write("                       'ING BANK (Australia) Ltd', 'Macquarie Bank Limited', 'UBank']\n")
        f.write("    return [get_bank_by_name(name) for name in major_bank_names if get_bank_by_name(name)]\n\n")
        
        f.write(f"# Metadata\n")
        f.write(f"GENERATION_DATE = '{time.strftime('%Y-%m-%d %H:%M:%S')}'\n")
        f.write(f"TOTAL_BANKS = {len(banks)}\n")
        f.write(f"CDR_REGISTER_URL = 'https://api.cdr.gov.au/cdr-register/v1/all/data-holders/brands/summary'\n")
    
    # Save as JSON for external use
    json_file = f"comprehensive_bank_list_{timestamp}.json"
    json_data = {
        "generation_date": time.strftime('%Y-%m-%d %H:%M:%S'),
        "total_banks": len(banks),
        "cdr_register_url": "https://api.cdr.gov.au/cdr-register/v1/all/data-holders/brands/summary",
        "banks": [
            {
                "name": bank_name,
                "brand_id": brand_id,
                "products_endpoint": products_endpoint,
                "base_uri": base_uri,
                "logo_uri": logo_uri
            }
            for bank_name, brand_id, products_endpoint, base_uri, logo_uri in banks
        ]
    }
    
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    # Save as simple list for luke_prior_realtime.py
    simple_file = f"luke_prior_bank_list_{timestamp}.py"
    with open(simple_file, 'w') as f:
        f.write("# Simple bank list for luke_prior_realtime.py\n")
        f.write("# Generated from CDR Register\n\n")
        f.write("BANKS_FROM_CDR_REGISTER = [\n")
        
        for bank_name, brand_id, products_endpoint, _, _ in banks:
            f.write(f'    ("{bank_name}", "{brand_id}", "{products_endpoint}"),\n')
        
        f.write("]\n")
    
    print(f"\n💾 Saved comprehensive bank list:")
    print(f"   🐍 Python: {py_file}")
    print(f"   📄 JSON: {json_file}")
    print(f"   🎯 Simple: {simple_file}")
    
    return py_file, json_file, simple_file

def main():
    """Main execution"""
    print("🚀 Comprehensive Bank List Generator")
    print("=" * 50)
    
    # Fetch data from CDR register
    banking_brands = fetch_cdr_banking_data()
    
    if not banking_brands:
        print("❌ No banking data retrieved")
        return
    
    # Process the brands
    processed_banks = process_banking_brands(banking_brands)
    
    if not processed_banks:
        print("❌ No banks processed successfully")
        return
    
    # Save the results
    py_file, json_file, simple_file = save_bank_list(processed_banks)
    
    print(f"\n📊 Summary:")
    print(f"   🏦 Total banking institutions: {len(processed_banks)}")
    print(f"   📅 Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show some examples
    print(f"\n🎯 Sample banks:")
    for bank_name, brand_id, products_endpoint, _, _ in processed_banks[:5]:
        print(f"   {bank_name}: {products_endpoint}")
    
    if len(processed_banks) > 5:
        print(f"   ... and {len(processed_banks) - 5} more")
    
    print(f"\n✅ Ready to use in luke_prior_realtime.py!")
    print(f"   Import from: {simple_file}")

if __name__ == "__main__":
    main()


