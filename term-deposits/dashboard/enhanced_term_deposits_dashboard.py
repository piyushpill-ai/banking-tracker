#!/usr/bin/env python3
"""
Enhanced Term Deposits Dashboard
===============================

Streamlit dashboard that shows ALL banks and clearly indicates
which have rates vs which have product info only.

Author: AI Assistant
Date: September 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import os
import glob

# Page configuration
st.set_page_config(
    page_title="🏦 Finder - Enhanced Term Deposits Tracker",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_term_deposits_data():
    """Load the term deposits data"""
    try:
        files = glob.glob("../data/term_deposits_*.csv")
        if not files:
            return pd.DataFrame()
        
        latest_file = max(files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        
        # Clean and categorize data
        df['interest_rate'] = pd.to_numeric(df['interest_rate'], errors='coerce')
        df['minimum_deposit'] = pd.to_numeric(df['minimum_deposit'], errors='coerce')
        df['term_months'] = pd.to_numeric(df['term_months'], errors='coerce')
        
        # Add rate availability flag
        df['has_rate'] = (df['interest_rate'].notna() & (df['interest_rate'] > 0))
        
        # Add data quality indicators
        df['has_detailed_info'] = df['additional_info'].notna() & (df['additional_info'] != '')
        df['has_terms'] = df['term_display'].notna() & (df['term_display'] != 'Not specified')
        df['has_minimums'] = df['minimum_deposit'].notna() & (df['minimum_deposit'] > 0)
        
        # Create data quality score
        df['data_quality_score'] = (
            df['has_rate'].astype(int) * 3 +  # Rates are most important
            df['has_detailed_info'].astype(int) +
            df['has_terms'].astype(int) +
            df['has_minimums'].astype(int)
        )
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def format_rate(rate):
    """Format rate for display"""
    if pd.isna(rate) or rate == 0:
        return "Call bank"
    return f"{rate:.2f}%"

def format_currency(amount):
    """Format currency for display"""
    if pd.isna(amount) or amount == 0:
        return "Not specified"
    return f"${amount:,.0f}"

def main():
    """Main dashboard function"""
    
    # Title and header
    st.title("🏦 Finder - Enhanced Term Deposits Tracker")
    st.markdown("### **Complete Bank Coverage + Rate Transparency**")
    st.markdown("*Shows ALL banks with clear indication of rate availability*")
    
    # Load data
    df = load_term_deposits_data()
    
    if df.empty:
        st.error("⚠️ No term deposit data available. Please run the scraper first.")
        st.stop()
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Banks", df['bank_name'].nunique())
    
    with col2:
        banks_with_rates = df[df['has_rate']]['bank_name'].nunique()
        st.metric("Banks with Rates", banks_with_rates)
    
    with col3:
        st.metric("Total Products", len(df))
    
    with col4:
        products_with_rates = len(df[df['has_rate']])
        st.metric("Products with Rates", products_with_rates)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Data availability filter
    data_filter = st.sidebar.selectbox(
        "**Show Banks With:**",
        options=['All Banks', 'Rates Available', 'Product Info Only', 'Best Data Quality'],
        index=0
    )
    
    # Bank selection
    if data_filter == 'Rates Available':
        available_banks = sorted(df[df['has_rate']]['bank_name'].unique())
    elif data_filter == 'Product Info Only':
        available_banks = sorted(df[~df['has_rate']]['bank_name'].unique())
    elif data_filter == 'Best Data Quality':
        available_banks = sorted(df[df['data_quality_score'] >= 3]['bank_name'].unique())
    else:
        available_banks = sorted(df['bank_name'].unique())
    
    selected_bank = st.sidebar.selectbox(
        "**Select Bank**",
        options=['All'] + available_banks,
        index=0
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if data_filter == 'Rates Available':
        filtered_df = filtered_df[filtered_df['has_rate']]
    elif data_filter == 'Product Info Only':
        filtered_df = filtered_df[~filtered_df['has_rate']]
    elif data_filter == 'Best Data Quality':
        filtered_df = filtered_df[filtered_df['data_quality_score'] >= 3]
    
    if selected_bank != 'All':
        filtered_df = filtered_df[filtered_df['bank_name'] == selected_bank]
    
    # Main content
    st.header(f"📊 {selected_bank} - Term Deposits Overview")
    
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📋 All Products", "💰 Rates Available", "📊 Bank Coverage"])
    
    with tab1:
        st.subheader("Complete Product Listing")
        
        # Enhanced display with rate availability
        display_df = filtered_df[[
            'bank_name', 'product_name', 'interest_rate', 'term_display',
            'minimum_deposit', 'has_rate', 'additional_info'
        ]].copy()
        
        # Format for display
        display_df['Bank'] = display_df['bank_name']
        display_df['Product'] = display_df['product_name']
        display_df['Rate'] = display_df['interest_rate'].apply(format_rate)
        display_df['Term'] = display_df['term_display'].fillna('Not specified')
        display_df['Min Deposit'] = display_df['minimum_deposit'].apply(format_currency)
        display_df['Rate Available'] = display_df['has_rate'].apply(lambda x: '✅ Yes' if x else '📞 Call bank')
        display_df['Details'] = display_df['additional_info'].fillna('Limited info').apply(
            lambda x: x[:100] + '...' if len(str(x)) > 100 else x
        )
        
        # Show formatted table
        st.dataframe(
            display_df[['Bank', 'Product', 'Rate', 'Term', 'Min Deposit', 'Rate Available', 'Details']],
            width='stretch',
            height=500
        )
    
    with tab2:
        st.subheader("Banks with Published Rates")
        
        rates_df = filtered_df[filtered_df['has_rate']]
        
        if rates_df.empty:
            st.info("No banks in current selection publish rates through their APIs.")
            st.markdown("**Banks typically requiring phone calls:**")
            no_rates = filtered_df[~filtered_df['has_rate']]['bank_name'].unique()
            for bank in no_rates[:10]:
                st.write(f"📞 {bank}")
        else:
            # Rate comparison chart
            fig = px.scatter(
                rates_df,
                x='term_months',
                y='interest_rate',
                color='bank_name',
                size='minimum_deposit',
                hover_data=['product_name'],
                title="Interest Rates by Term Length",
                labels={
                    'term_months': 'Term (Months)',
                    'interest_rate': 'Interest Rate (%)',
                    'bank_name': 'Bank'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Best rates summary
            st.subheader("🏆 Best Available Rates")
            best_rates = rates_df.loc[rates_df.groupby('term_display')['interest_rate'].idxmax()]
            
            for _, row in best_rates.iterrows():
                if pd.notna(row['interest_rate']):
                    st.write(f"**{row['term_display']}**: {row['interest_rate']:.2f}% - {row['bank_name']}")
    
    with tab3:
        st.subheader("Bank Coverage Analysis")
        
        # Bank coverage summary
        bank_summary = df.groupby('bank_name').agg({
            'product_name': 'count',
            'has_rate': 'any',
            'data_quality_score': 'max'
        }).reset_index()
        
        bank_summary.columns = ['Bank', 'Products', 'Has Rates', 'Quality Score']
        bank_summary['Rate Status'] = bank_summary['Has Rates'].apply(
            lambda x: '✅ Rates available' if x else '📞 Call for rates'
        )
        
        # Sort by quality score
        bank_summary = bank_summary.sort_values('Quality Score', ascending=False)
        
        st.dataframe(
            bank_summary[['Bank', 'Products', 'Rate Status', 'Quality Score']],
            width='stretch',
            height=400
        )
        
        # Coverage statistics
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Coverage Statistics:**")
            total_banks = len(bank_summary)
            with_rates = len(bank_summary[bank_summary['Has Rates']])
            st.write(f"• Total banks: {total_banks}")
            st.write(f"• With published rates: {with_rates} ({with_rates/total_banks*100:.1f}%)")
            st.write(f"• Require phone calls: {total_banks - with_rates} ({(total_banks-with_rates)/total_banks*100:.1f}%)")
        
        with col2:
            st.markdown("**🎯 Top Banks with Rates:**")
            top_rate_banks = bank_summary[bank_summary['Has Rates']].head(5)
            for _, row in top_rate_banks.iterrows():
                st.write(f"• {row['Bank']} ({row['Products']} products)")
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    **📊 Data Transparency:**
    - **Complete coverage**: {df['bank_name'].nunique()} banks, {len(df)} products
    - **Rate publishers**: {df[df['has_rate']]['bank_name'].nunique()} banks with real-time rates
    - **Call-for-rates**: {df[~df['has_rate']]['bank_name'].nunique()} banks require phone contact
    - **Industry reality**: Most banks don't publish term deposit rates via APIs
    """)

if __name__ == "__main__":
    main()


