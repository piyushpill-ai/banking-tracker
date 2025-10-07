#!/usr/bin/env python3
"""
Complete Mortgage Dashboard - Streamlit App with ALL Fee Fields
Interactive dashboard with every field requested by the user
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="🏠 Finder - Open Banking FHL Rate Tracker",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_complete_mortgage_data():
    """Load the complete mortgage data with fees"""
    try:
        # Load the comprehensive fee dataset (complete rates + fees from 61 banks)
        df = pd.read_csv('complete_mortgage_data_20250917_214803.csv')
        
        # Clean and standardize the data (columns already in correct format)
        df['Interest Rate (%)'] = pd.to_numeric(df['Interest Rate (%)'], errors='coerce')
        df['Comparison Rate (%)'] = pd.to_numeric(df['Comparison Rate (%)'], errors='coerce')
        
        # Clean fee columns (data already includes comprehensive fee information)
        fee_columns = [
            'Offset Fee ($)', 'Application Fee ($)', 'Annual Fee ($)', 
            'Monthly Fee ($)', 'Exit Fee ($)', 'Redraw Fee ($)'
        ]
        
        for col in fee_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Handle missing values
        if 'Fixed Term (Months)' in df.columns:
            df['Fixed Term (Months)'] = df['Fixed Term (Months)'].fillna(0)
        else:
            df['Fixed Term (Months)'] = 0
            
        df['Variant Name'] = df['Variant Name'].fillna('Standard')
        
        # Clean other ongoing fees column
        if 'Other Ongoing Fees' in df.columns:
            df['Other Ongoing Fees'] = df['Other Ongoing Fees'].fillna('None')
        
        # Convert fixed term to readable format
        df['Fixed Term Display'] = df['Fixed Term (Months)'].apply(lambda x: 
            f"{int(x/12)} year{'s' if x/12 != 1 else ''}" if x > 0 else "N/A"
        )
        
        return df
    except FileNotFoundError:
        st.error("Complete mortgage data file not found. Please run the enhanced_fees_scraper.py first.")
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
    return f"{rate:.3f}%"


def main():
    """Main dashboard function"""
    
    # Title and header
    st.title("🏠 Finder - Open Banking FHL Rate Tracker")
    st.markdown("### **Real-Time Mortgage Rates and Fees**")
    st.markdown("*Data sourced from Consumer Data Standards (CDS) APIs*")
    
    # Load complete data
    df = load_complete_mortgage_data()
    
    if df.empty:
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Lender selection
    lenders = sorted(df['Bank Name'].unique())
    selected_lender = st.sidebar.selectbox(
        "**Select Lender**",
        options=lenders,
        index=0
    )
    
    # Additional filters
    st.sidebar.subheader("Additional Filters")
    
    rate_types = st.sidebar.multiselect(
        "Rate Type",
        options=df['Fixed / Variable'].unique(),
        default=df['Fixed / Variable'].unique()
    )
    
    loan_purposes = st.sidebar.multiselect(
        "Loan Purpose",
        options=df['Owner Occupier / Investor'].unique(),
        default=df['Owner Occupier / Investor'].unique()
    )
    
    repayment_types = st.sidebar.multiselect(
        "Repayment Type",
        options=df['P&I / Interest Only'].unique(),
        default=df['P&I / Interest Only'].unique()
    )
    
    # Offset filter
    offset_filter = st.sidebar.selectbox(
        "Offset Account",
        options=['All', 'Available', 'Not Available'],
        index=0
    )
    
    # Filter data based on selections
    filtered_df = df[
        (df['Bank Name'] == selected_lender) &
        (df['Fixed / Variable'].isin(rate_types)) &
        (df['Owner Occupier / Investor'].isin(loan_purposes)) &
        (df['P&I / Interest Only'].isin(repayment_types))
    ]
    
    # Apply offset filter
    if offset_filter == 'Available':
        filtered_df = filtered_df[filtered_df['Offset Available'] == 'Y']
    elif offset_filter == 'Not Available':
        filtered_df = filtered_df[filtered_df['Offset Available'] == 'N']
    
    
    # Main data table with ALL requested fields
    st.header(f"📋 {selected_lender} - Mortgage Rates & Fees")
    
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Prepare complete display dataframe with ALL requested fields
    display_df = filtered_df[[
        'Product Name',
        'Variant Name', 
        'Interest Rate (%)',
        'Comparison Rate (%)',
        'Owner Occupier / Investor',
        'Fixed / Variable',
        'P&I / Interest Only',
        'Offset Available',
        'Offset Fee ($)',
        'Offset Fee Frequency',
        'Application Fee ($)',
        'Application Fee Frequency',
        'Annual Fee ($)',
        'Monthly Fee ($)',
        'Exit Fee ($)',
        'Redraw Fee ($)',
        'Other Ongoing Fees',
        'Fixed Term Display',
        'LVR Min (%)',
        'LVR Max (%)'
    ]].copy()
    
    # Rename columns for final display
    display_df = display_df.rename(columns={
        'Fixed Term Display': 'Fixed Term',
        'Other Ongoing Fees': 'Other Fees'
    })
    
    # Format the dataframe for better display
    def format_complete_dataframe(df):
        """Format dataframe with all fee fields"""
        formatted_df = df.copy()
        
        # Format rate columns
        for col in ['Interest Rate (%)', 'Comparison Rate (%)']:
            if col in formatted_df.columns:
                formatted_df[col] = formatted_df[col].apply(format_rate)
        
        # Format fee columns
        fee_cols = ['Offset Fee ($)', 'Application Fee ($)', 'Annual Fee ($)', 
                   'Monthly Fee ($)', 'Exit Fee ($)', 'Redraw Fee ($)']
        for col in fee_cols:
            if col in formatted_df.columns:
                formatted_df[col] = formatted_df[col].apply(format_currency)
        
        # Clean up other fees column for display
        if 'Other Fees' in formatted_df.columns:
            formatted_df['Other Fees'] = formatted_df['Other Fees'].apply(
                lambda x: x[:100] + '...' if len(str(x)) > 100 else x
            )
        
        return formatted_df
    
    # Add search functionality
    search_term = st.text_input("🔍 Search products:", placeholder="Enter product or variant name...")
    if search_term:
        mask = (
            filtered_df['Product Name'].str.contains(search_term, case=False, na=False) |
            filtered_df['Variant Name'].str.contains(search_term, case=False, na=False)
        )
        display_df = display_df[mask]
    
    # Sort options
    sort_col1, sort_col2 = st.columns(2)
    with sort_col1:
        sort_by = st.selectbox(
            "Sort by:",
            options=['Interest Rate (%)', 'Comparison Rate (%)', 'Application Fee ($)', 'Product Name'],
            index=0
        )
    
    with sort_col2:
        sort_order = st.selectbox(
            "Sort order:",
            options=['Ascending', 'Descending'],
            index=0
        )
    
    # Apply sorting
    if not display_df.empty:
        ascending = sort_order == 'Ascending'
        if sort_by in ['Interest Rate (%)', 'Comparison Rate (%)']:
            # Handle both string and numeric columns
            col_data = display_df[sort_by]
            if col_data.dtype == 'object':
                # If string, remove % and convert to numeric
                sort_col_data = pd.to_numeric(col_data.astype(str).str.replace('%', '').str.replace('', '0'), errors='coerce')
            else:
                # If already numeric, use as-is
                sort_col_data = pd.to_numeric(col_data, errors='coerce')
            display_df = display_df.iloc[sort_col_data.argsort()[::1 if ascending else -1]]
        elif sort_by == 'Application Fee ($)':
            # Handle both string and numeric columns
            col_data = display_df[sort_by]
            if col_data.dtype == 'object':
                # If string, remove $ and , and convert to numeric
                sort_col_data = pd.to_numeric(col_data.astype(str).str.replace('$', '').str.replace(',', '').str.replace('', '0'), errors='coerce')
            else:
                # If already numeric, use as-is
                sort_col_data = pd.to_numeric(col_data, errors='coerce')
            display_df = display_df.iloc[sort_col_data.argsort()[::1 if ascending else -1]]
        else:
            display_df = display_df.sort_values(sort_by, ascending=ascending)
    
    # Format and display the complete table
    formatted_display_df = format_complete_dataframe(display_df)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Complete Table", "💰 Fees Focus", "📈 Rates Focus"])
    
    with tab1:
        st.subheader("Complete Mortgage Information")
        st.dataframe(
            formatted_display_df,
            width='stretch',
            height=500
        )
    
    with tab2:
        st.subheader("Fees Analysis")
        
        # Fee columns only
        fee_focused_df = formatted_display_df[[
            'Product Name', 'Variant Name',
            'Application Fee ($)', 'Application Fee Frequency',
            'Offset Fee ($)', 'Offset Fee Frequency',
            'Annual Fee ($)', 'Monthly Fee ($)', 'Exit Fee ($)', 'Redraw Fee ($)',
            'Other Fees'
        ]]
        
        st.dataframe(fee_focused_df, width='stretch', height=400)
        
        # Fee visualization
        if not filtered_df.empty:
            # Filter out rows with invalid fees
            fee_plot_df = filtered_df[
                (filtered_df['Application Fee ($)'].notna()) & 
                (filtered_df['Application Fee ($)'] > 0)
            ]
            
            if not fee_plot_df.empty:
                fig_fees = px.bar(
                    fee_plot_df,
                    x='Variant Name',
                    y='Application Fee ($)',
                    title=f"{selected_lender} - Application Fees by Variant",
                    text='Application Fee ($)'
                )
                fig_fees.update_layout(height=400)
                st.plotly_chart(fig_fees, use_container_width=True)
            else:
                st.info("No application fee data available for visualization.")
    
    with tab3:
        st.subheader("Rates Analysis")
        
        # Rate columns only
        rate_focused_df = formatted_display_df[[
            'Product Name', 'Variant Name',
            'Interest Rate (%)', 'Comparison Rate (%)',
            'Owner Occupier / Investor', 'Fixed / Variable', 'P&I / Interest Only',
            'Fixed Term', 'Offset Available'
        ]]
        
        st.dataframe(rate_focused_df, width='stretch', height=400)
        
        # Rate visualization
        if len(filtered_df) > 1:
            # Clean data for plotting
            plot_df = filtered_df.copy()
            
            # Handle NaN values in all numeric columns
            plot_df['Application Fee ($)'] = pd.to_numeric(plot_df['Application Fee ($)'], errors='coerce').fillna(0)
            plot_df['Interest Rate (%)'] = pd.to_numeric(plot_df['Interest Rate (%)'], errors='coerce')
            plot_df['Comparison Rate (%)'] = pd.to_numeric(plot_df['Comparison Rate (%)'], errors='coerce')
            
            # Remove rows with missing rate data
            plot_df = plot_df.dropna(subset=['Interest Rate (%)', 'Comparison Rate (%)'])
            
            # Ensure size column has no zeros or negatives for better visualization
            plot_df = plot_df[plot_df['Application Fee ($)'] >= 0]
            plot_df.loc[plot_df['Application Fee ($)'] == 0, 'Application Fee ($)'] = 1  # Minimum size for visibility
            
            if not plot_df.empty:
                fig_rates = px.scatter(
                    plot_df,
                    x='Interest Rate (%)',
                    y='Comparison Rate (%)',
                    color='Owner Occupier / Investor',
                    size='Application Fee ($)',
                    hover_data=['Product Name', 'Variant Name'],
                    title=f"{selected_lender} - Interest vs Comparison Rates"
                )
                fig_rates.update_layout(height=400)
                st.plotly_chart(fig_rates, use_container_width=True)
            else:
                st.info("No rate data available for visualization.")

if __name__ == "__main__":
    main()
