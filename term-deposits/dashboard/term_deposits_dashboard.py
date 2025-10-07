#!/usr/bin/env python3
"""
Term Deposits Dashboard
======================

Streamlit dashboard for Australian term deposit rates and features.
Displays comprehensive term deposit comparison data collected from
Consumer Data Standards (CDS) APIs.

Features:
- Term deposit rates comparison
- Term length filtering
- Minimum deposit requirements
- Fee information
- Interactive filtering and sorting

Author: AI Assistant
Date: September 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import os
import glob

# Page configuration
st.set_page_config(
    page_title="🏦 Finder - Term Deposits Rate Tracker",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_term_deposits_data():
    """Load the term deposits data"""
    try:
        # Find the most recent term deposits data file
        files = glob.glob("../data/term_deposits_*.csv")
        if not files:
            return pd.DataFrame()
        
        latest_file = max(files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        
        # Clean and standardize the data
        df['interest_rate'] = pd.to_numeric(df['interest_rate'], errors='coerce')
        df['minimum_deposit'] = pd.to_numeric(df['minimum_deposit'], errors='coerce')
        df['maximum_deposit'] = pd.to_numeric(df['maximum_deposit'], errors='coerce')
        df['term_months'] = pd.to_numeric(df['term_months'], errors='coerce')
        df['account_fee'] = pd.to_numeric(df['account_fee'], errors='coerce')
        df['early_withdrawal_fee'] = pd.to_numeric(df['early_withdrawal_fee'], errors='coerce')
        
        # Clean term display
        df['term_display'] = df['term_display'].fillna('Not specified')
        df['rate_type'] = df['rate_type'].fillna('FIXED')
        df['additional_info'] = df['additional_info'].fillna('')
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def format_currency(amount):
    """Format currency for display"""
    if pd.isna(amount) or amount == 0:
        return ""
    return f"${amount:,.0f}"

def format_rate(rate):
    """Format rate for display"""
    if pd.isna(rate) or rate == 0:
        return ""
    return f"{rate:.2f}%"

def format_term_display_dataframe(df):
    """Format dataframe for better display"""
    formatted_df = df.copy()
    
    # Format rate columns
    if 'interest_rate' in formatted_df.columns:
        formatted_df['Interest Rate (%)'] = formatted_df['interest_rate'].apply(format_rate)
    
    if 'bonus_rate' in formatted_df.columns:
        formatted_df['Bonus Rate (%)'] = formatted_df['bonus_rate'].apply(format_rate)
    
    # Format currency columns
    currency_cols = ['minimum_deposit', 'maximum_deposit', 'account_fee', 'early_withdrawal_fee']
    for col in currency_cols:
        if col in formatted_df.columns:
            col_display = col.replace('_', ' ').title().replace('Deposit', 'Deposit ($)')
            if 'fee' in col.lower():
                col_display = col.replace('_', ' ').title().replace('Fee', 'Fee ($)')
            formatted_df[col_display] = formatted_df[col].apply(format_currency)
    
    return formatted_df

def main():
    """Main dashboard function"""
    
    # Title and header
    st.title("🏦 Finder - Term Deposits Rate Tracker")
    st.markdown("### **Real-Time Term Deposit Rates**")
    st.markdown("*Data sourced from Consumer Data Standards (CDS) APIs*")
    
    # Load data
    df = load_term_deposits_data()
    
    if df.empty:
        st.error("⚠️ No term deposit data available. Please run the scraper first.")
        st.markdown("Run: `python3 term-deposits/scripts/term_deposits_scraper.py`")
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Bank selection
    banks = sorted(df['bank_name'].unique())
    selected_bank = st.sidebar.selectbox(
        "**Select Bank**",
        options=['All'] + banks,
        index=0
    )
    
    # Term length filter
    available_terms = sorted([t for t in df['term_display'].unique() if pd.notna(t) and t != 'Not specified'])
    selected_terms = st.sidebar.multiselect(
        "**Term Length**",
        options=available_terms,
        default=available_terms
    )
    
    # Rate type filter
    rate_types = df['rate_type'].unique()
    selected_rate_types = st.sidebar.multiselect(
        "**Rate Type**",
        options=rate_types,
        default=rate_types
    )
    
    # Minimum deposit range
    if df['minimum_deposit'].notna().any():
        min_dep_min = int(df['minimum_deposit'].min()) if not pd.isna(df['minimum_deposit'].min()) else 0
        min_dep_max = int(df['minimum_deposit'].max()) if not pd.isna(df['minimum_deposit'].max()) else 100000
        
        deposit_range = st.sidebar.slider(
            "**Minimum Deposit Range**",
            min_value=min_dep_min,
            max_value=min_dep_max,
            value=(min_dep_min, min_dep_max),
            step=1000,
            format="$%d"
        )
    else:
        deposit_range = (0, 100000)
    
    # Interest rate range
    if df['interest_rate'].notna().any():
        rate_min = float(df['interest_rate'].min()) if not pd.isna(df['interest_rate'].min()) else 0.0
        rate_max = float(df['interest_rate'].max()) if not pd.isna(df['interest_rate'].max()) else 10.0
        
        rate_range = st.sidebar.slider(
            "**Interest Rate Range (%)**",
            min_value=rate_min,
            max_value=rate_max,
            value=(rate_min, rate_max),
            step=0.1,
            format="%.1f%%"
        )
    else:
        rate_range = (0.0, 10.0)
    
    # Product search
    search_term = st.sidebar.text_input("🔍 Search Products", "")
    
    # Sorting options
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔄 Sorting**")
    sort_by = st.sidebar.selectbox(
        "Sort by:",
        options=['Interest Rate (%)', 'Term Length', 'Minimum Deposit', 'Bank Name', 'Product Name'],
        index=0
    )
    sort_order = st.sidebar.selectbox(
        "Sort order:",
        options=['Descending', 'Ascending'],
        index=0
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    # Bank filter
    if selected_bank != 'All':
        filtered_df = filtered_df[filtered_df['bank_name'] == selected_bank]
    
    # Term filter
    if selected_terms:
        filtered_df = filtered_df[filtered_df['term_display'].isin(selected_terms)]
    
    # Rate type filter
    if selected_rate_types:
        filtered_df = filtered_df[filtered_df['rate_type'].isin(selected_rate_types)]
    
    # Deposit range filter
    filtered_df = filtered_df[
        (filtered_df['minimum_deposit'].isna()) | 
        ((filtered_df['minimum_deposit'] >= deposit_range[0]) & 
         (filtered_df['minimum_deposit'] <= deposit_range[1]))
    ]
    
    # Interest rate filter
    filtered_df = filtered_df[
        (filtered_df['interest_rate'].isna()) | 
        ((filtered_df['interest_rate'] >= rate_range[0]) & 
         (filtered_df['interest_rate'] <= rate_range[1]))
    ]
    
    # Search filter
    if search_term:
        mask = (
            filtered_df['product_name'].str.contains(search_term, case=False, na=False) |
            filtered_df['bank_name'].str.contains(search_term, case=False, na=False) |
            filtered_df['additional_info'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Apply sorting
    if not filtered_df.empty:
        ascending = sort_order == 'Ascending'
        if sort_by == 'Interest Rate (%)':
            sort_col_data = pd.to_numeric(filtered_df['interest_rate'], errors='coerce')
        elif sort_by == 'Term Length':
            sort_col_data = pd.to_numeric(filtered_df['term_months'], errors='coerce')
        elif sort_by == 'Minimum Deposit':
            sort_col_data = pd.to_numeric(filtered_df['minimum_deposit'], errors='coerce')
        else:
            sort_col_data = filtered_df[sort_by.lower().replace(' ', '_').replace('(%)', '')]
        
        filtered_df = filtered_df.iloc[sort_col_data.argsort()[::1 if ascending else -1]]
    
    # Main data table
    st.header(f"📊 {selected_bank} - Term Deposit Rates")
    
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Format the dataframe for display
    display_df = filtered_df[[
        'bank_name', 'product_name', 'interest_rate', 'rate_type',
        'term_display', 'minimum_deposit', 'maximum_deposit',
        'account_fee', 'early_withdrawal_fee', 'additional_info'
    ]].copy()
    
    # Rename columns for display
    display_columns = {
        'bank_name': 'Bank Name',
        'product_name': 'Product Name',
        'interest_rate': 'Interest Rate (%)',
        'rate_type': 'Rate Type',
        'term_display': 'Term Length',
        'minimum_deposit': 'Min Deposit ($)',
        'maximum_deposit': 'Max Deposit ($)',
        'account_fee': 'Account Fee ($)',
        'early_withdrawal_fee': 'Early Withdrawal Fee ($)',
        'additional_info': 'Additional Info'
    }
    
    display_df = display_df.rename(columns=display_columns)
    formatted_display_df = format_term_display_dataframe(display_df)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Complete Table", "📈 Rate Analysis", "💰 Deposit Analysis"])
    
    with tab1:
        st.subheader("Complete Term Deposit Information")
        
        # Display key columns for complete table
        key_columns = [
            'Bank Name', 'Product Name', 'Interest Rate (%)', 'Rate Type',
            'Term Length', 'Min Deposit ($)', 'Max Deposit ($)',
            'Account Fee ($)', 'Early Withdrawal Fee ($)'
        ]
        
        available_columns = [col for col in key_columns if col in formatted_display_df.columns]
        st.dataframe(
            formatted_display_df[available_columns],
            width='stretch',
            height=500
        )
    
    with tab2:
        st.subheader("Rate Analysis")
        
        if len(filtered_df) > 1 and filtered_df['interest_rate'].notna().any():
            # Rate distribution by term
            fig_rates = px.scatter(
                filtered_df[filtered_df['interest_rate'].notna()],
                x='term_months',
                y='interest_rate',
                color='bank_name',
                size='minimum_deposit',
                hover_data=['product_name', 'rate_type'],
                title="Interest Rates by Term Length",
                labels={
                    'term_months': 'Term (Months)',
                    'interest_rate': 'Interest Rate (%)',
                    'bank_name': 'Bank',
                    'minimum_deposit': 'Min Deposit ($)'
                }
            )
            fig_rates.update_layout(height=400)
            st.plotly_chart(fig_rates, use_container_width=True)
        else:
            st.info("Not enough data for rate visualization.")
    
    with tab3:
        st.subheader("Deposit Requirements Analysis")
        
        if len(filtered_df) > 1 and filtered_df['minimum_deposit'].notna().any():
            # Deposit requirements by bank
            deposit_data = filtered_df[filtered_df['minimum_deposit'].notna()]
            
            if not deposit_data.empty:
                fig_deposits = px.box(
                    deposit_data,
                    x='bank_name',
                    y='minimum_deposit',
                    title="Minimum Deposit Requirements by Bank"
                )
                fig_deposits.update_xaxis(tickangle=45)
                fig_deposits.update_layout(height=400)
                st.plotly_chart(fig_deposits, use_container_width=True)
        else:
            st.info("Not enough data for deposit analysis.")
    
    # Summary statistics
    st.markdown("---")
    if not filtered_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_rate = filtered_df['interest_rate'].mean()
            st.metric("Average Rate", format_rate(avg_rate) if not pd.isna(avg_rate) else "N/A")
        
        with col2:
            max_rate = filtered_df['interest_rate'].max()
            st.metric("Highest Rate", format_rate(max_rate) if not pd.isna(max_rate) else "N/A")
        
        with col3:
            min_deposit = filtered_df['minimum_deposit'].min()
            st.metric("Lowest Min Deposit", format_currency(min_deposit) if not pd.isna(min_deposit) else "N/A")
        
        with col4:
            st.metric("Total Products", len(filtered_df))

if __name__ == "__main__":
    main()
