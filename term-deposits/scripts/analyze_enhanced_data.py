#!/usr/bin/env python3
"""
Quick analysis script for enhanced term deposits data
"""

import pandas as pd

def main():
    # Load the latest enhanced data
    df = pd.read_csv('../data/enhanced_term_deposits_20250918_100119.csv')
    
    print('🔍 DETAILED ENHANCED DATA ANALYSIS')
    print('=' * 50)
    
    # Basic stats
    print(f'📊 Total records: {len(df)}')
    with_rates = df[df['interest_rate'].notna() & (df['interest_rate'] > 0)]
    print(f'💰 Records with rates: {len(with_rates)} ({len(with_rates)/len(df)*100:.1f}%)')
    print()
    
    # Sample of best rates
    print('🏆 Top 10 highest rates:')
    top_rates = with_rates.sort_values('interest_rate', ascending=False).head(10)
    for _, row in top_rates.iterrows():
        rate = row['interest_rate']
        term = row['term_display'] if pd.notna(row['term_display']) else 'Not specified'
        bank = row['bank_name']
        product = row['product_name'][:30] + '...' if len(row['product_name']) > 30 else row['product_name']
        print(f'   {rate:.3f}% - {term} - {bank}')
        print(f'      Product: {product}')
    
    print()
    print('💵 Deposit tier examples:')
    tiered = df[df['tier_minimum'].notna()]
    if not tiered.empty:
        print(f'   Found {len(tiered)} records with tier information')
        for _, row in tiered.head(5).iterrows():
            tier_min = row['tier_minimum']
            tier_max = row['tier_maximum'] if pd.notna(row['tier_maximum']) else 'unlimited'
            rate = row['interest_rate'] if pd.notna(row['interest_rate']) else 'N/A'
            bank = row['bank_name']
            print(f'   {bank}: ${tier_min:,.0f} - {tier_max} → {rate}%')
    else:
        print('   No tier data found in this sample')
    
    print()
    print('🎯 Comparison with original approach:')
    print('   Original: 350 products from 56 banks → 128 with rates (36.6%)')
    print(f'   Enhanced: {len(df)} variants from 2 banks → {len(with_rates)} with rates ({len(with_rates)/len(df)*100:.1f}%)')
    print('   🚀 Improvement: Much higher rate coverage per bank!')

if __name__ == "__main__":
    main()


