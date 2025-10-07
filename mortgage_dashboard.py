#!/usr/bin/env python3
"""
Mortgage Rate Dashboard - Streamlit App
Interactive dashboard for exploring Australian mortgage rates
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Australian Mortgage Rate Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_mortgage_data():
    """Load the mortgage rate data"""
    try:
        # Load the most recent enhanced mortgage rates file
        df = pd.read_csv('enhanced_mortgage_rates_20250917_212216.csv')
        
        # Clean and standardize the data
        df['Rate (%)'] = pd.to_numeric(df['Rate (%)'], errors='coerce')
        df['Comparison Rate (%)'] = pd.to_numeric(df['Comparison Rate (%)'], errors='coerce')
        
        # Handle missing values
        df['Fixed Term (Months)'] = df['Fixed Term (Months)'].fillna(0)
        df['Tier Name'] = df['Tier Name'].fillna('Standard')
        df['Additional Info'] = df['Additional Info'].fillna('')
        
        # Create variant name from tier name and additional info
        df['Variant Name'] = df.apply(lambda row: 
            f"{row['Tier Name']}" + (f" - {row['Additional Info']}" if row['Additional Info'] else ""), 
            axis=1
        )
        
        # Convert fixed term to readable format
        df['Fixed Term Display'] = df['Fixed Term (Months)'].apply(lambda x: 
            f"{int(x/12)} year{'s' if x/12 != 1 else ''}" if x > 0 else "N/A"
        )
        
        return df
    except FileNotFoundError:
        st.error("Mortgage rate data file not found. Please run the enhanced_rate_scraper.py first.")
        return pd.DataFrame()

def format_rate(rate):
    """Format rate for display"""
    if pd.isna(rate) or rate == 0:
        return "N/A"
    return f"{rate:.3f}%"

def create_lender_summary(df, selected_lender):
    """Create summary metrics for selected lender"""
    lender_data = df[df['Bank Name'] == selected_lender]
    
    if lender_data.empty:
        return None
    
    # Calculate summary statistics
    total_products = lender_data['Product Name'].nunique()
    total_rates = len(lender_data[lender_data['Rate (%)'] > 0])
    avg_variable_rate = lender_data[lender_data['Rate Type'] == 'VARIABLE']['Rate (%)'].mean()
    avg_fixed_rate = lender_data[lender_data['Rate Type'] == 'FIXED']['Rate (%)'].mean()
    
    return {
        'total_products': total_products,
        'total_rates': total_rates,
        'avg_variable_rate': avg_variable_rate,
        'avg_fixed_rate': avg_fixed_rate
    }

def main():
    """Main dashboard function"""
    
    # Title and header
    st.title("🏠 Australian Mortgage Rate Dashboard")
    st.markdown("### Real-Time Mortgage Rate Comparison Tool")
    st.markdown("*Data sourced from Consumer Data Standards (CDS) APIs*")
    
    # Load data
    df = load_mortgage_data()
    
    if df.empty:
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Lender selection
    lenders = sorted(df['Bank Name'].unique())
    selected_lender = st.sidebar.selectbox(
        "Select Lender",
        options=lenders,
        index=0
    )
    
    # Additional filters
    st.sidebar.subheader("Additional Filters")
    
    rate_types = st.sidebar.multiselect(
        "Rate Type",
        options=df['Rate Type'].unique(),
        default=df['Rate Type'].unique()
    )
    
    loan_purposes = st.sidebar.multiselect(
        "Loan Purpose",
        options=df['Loan Purpose'].unique(),
        default=df['Loan Purpose'].unique()
    )
    
    repayment_types = st.sidebar.multiselect(
        "Repayment Type",
        options=df['Repayment Type'].unique(),
        default=df['Repayment Type'].unique()
    )
    
    # Filter data based on selections
    filtered_df = df[
        (df['Bank Name'] == selected_lender) &
        (df['Rate Type'].isin(rate_types)) &
        (df['Loan Purpose'].isin(loan_purposes)) &
        (df['Repayment Type'].isin(repayment_types))
    ]
    
    # Display lender summary
    st.header(f"📊 {selected_lender} - Overview")
    
    summary = create_lender_summary(df, selected_lender)
    if summary:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Products", summary['total_products'])
        
        with col2:
            st.metric("Total Rate Options", summary['total_rates'])
        
        with col3:
            st.metric("Avg Variable Rate", format_rate(summary['avg_variable_rate']))
        
        with col4:
            st.metric("Avg Fixed Rate", format_rate(summary['avg_fixed_rate']))
    
    # Main data table
    st.header(f"📋 {selected_lender} - Mortgage Rates")
    
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Prepare display dataframe
    display_df = filtered_df[[
        'Product Name',
        'Variant Name', 
        'Rate (%)',
        'Comparison Rate (%)',
        'Loan Purpose',
        'Rate Type',
        'Repayment Type',
        'Offset Available',
        'Fixed Term Display',
        'LVR Min (%)',
        'LVR Max (%)'
    ]].copy()
    
    # Rename columns for better display
    display_df = display_df.rename(columns={
        'Product Name': 'Product Name',
        'Variant Name': 'Variant Name',
        'Rate (%)': 'Interest Rate (%)',
        'Comparison Rate (%)': 'Comparison Rate (%)',
        'Loan Purpose': 'Owner Occupier / Investor',
        'Rate Type': 'Fixed / Variable',
        'Repayment Type': 'P&I / Interest Only',
        'Offset Available': 'Offset Account',
        'Fixed Term Display': 'Fixed Term',
        'LVR Min (%)': 'LVR Min (%)',
        'LVR Max (%)': 'LVR Max (%)'
    })
    
    # Format the dataframe for display
    def format_dataframe(df):
        """Format dataframe for better display"""
        formatted_df = df.copy()
        
        # Format rate columns
        for col in ['Interest Rate (%)', 'Comparison Rate (%)']:
            if col in formatted_df.columns:
                formatted_df[col] = formatted_df[col].apply(format_rate)
        
        # Format loan purpose
        if 'Owner Occupier / Investor' in formatted_df.columns:
            formatted_df['Owner Occupier / Investor'] = formatted_df['Owner Occupier / Investor'].str.replace('_', ' ').str.title()
        
        # Format repayment type
        if 'P&I / Interest Only' in formatted_df.columns:
            formatted_df['P&I / Interest Only'] = formatted_df['P&I / Interest Only'].str.replace('_', ' ').str.title()
        
        return formatted_df
    
    # Display the table
    formatted_display_df = format_dataframe(display_df)
    
    # Add search functionality
    search_term = st.text_input("🔍 Search products:", placeholder="Enter product name...")
    if search_term:
        formatted_display_df = formatted_display_df[
            formatted_display_df['Product Name'].str.contains(search_term, case=False, na=False)
        ]
    
    # Sort options
    sort_col1, sort_col2 = st.columns(2)
    with sort_col1:
        sort_by = st.selectbox(
            "Sort by:",
            options=['Interest Rate (%)', 'Comparison Rate (%)', 'Product Name'],
            index=0
        )
    
    with sort_col2:
        sort_order = st.selectbox(
            "Sort order:",
            options=['Ascending', 'Descending'],
            index=0
        )
    
    # Apply sorting
    ascending = sort_order == 'Ascending'
    if sort_by in ['Interest Rate (%)', 'Comparison Rate (%)']:
        # Convert back to numeric for sorting
        sort_col_data = pd.to_numeric(formatted_display_df[sort_by].str.replace('%', '').str.replace('N/A', '0'), errors='coerce')
        formatted_display_df = formatted_display_df.iloc[sort_col_data.argsort()[::1 if ascending else -1]]
    else:
        formatted_display_df = formatted_display_df.sort_values(sort_by, ascending=ascending)
    
    # Display the table
    st.dataframe(
        formatted_display_df,
        use_container_width=True,
        height=400
    )
    
    # Rate visualization
    st.header("📈 Rate Distribution")
    
    if len(filtered_df) > 1:
        # Create rate distribution chart
        fig = px.box(
            filtered_df, 
            x='Rate Type', 
            y='Rate (%)', 
            color='Loan Purpose',
            title=f"{selected_lender} - Rate Distribution by Type and Purpose"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Rate comparison by repayment type
        col1, col2 = st.columns(2)
        
        with col1:
            # Variable rates by repayment type
            variable_rates = filtered_df[filtered_df['Rate Type'] == 'VARIABLE']
            if not variable_rates.empty:
                fig_var = px.scatter(
                    variable_rates,
                    x='Repayment Type',
                    y='Rate (%)',
                    color='Loan Purpose',
                    size='LVR Max (%)',
                    title="Variable Rates by Repayment Type",
                    hover_data=['Product Name', 'Variant Name']
                )
                fig_var.update_layout(height=300)
                st.plotly_chart(fig_var, use_container_width=True)
        
        with col2:
            # Fixed rates by term
            fixed_rates = filtered_df[filtered_df['Rate Type'] == 'FIXED']
            if not fixed_rates.empty:
                fig_fixed = px.scatter(
                    fixed_rates,
                    x='Fixed Term (Months)',
                    y='Rate (%)',
                    color='Loan Purpose',
                    title="Fixed Rates by Term",
                    hover_data=['Product Name', 'Variant Name']
                )
                fig_fixed.update_layout(height=300)
                st.plotly_chart(fig_fixed, use_container_width=True)
    
    # Data export
    st.header("💾 Export Data")
    
    if st.button("Download Filtered Data as CSV"):
        csv = formatted_display_df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name=f"{selected_lender.replace(' ', '_')}_mortgage_rates_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Footer with data info
    st.markdown("---")
    st.markdown(f"""
    **Data Information:**
    - Total records displayed: {len(formatted_display_df)}
    - Data last updated: {filtered_df['Last Updated'].iloc[0] if not filtered_df.empty else 'Unknown'}
    - Source: Consumer Data Standards (CDS) APIs
    
    **Note:** Fees information (offset fees, application fees, ongoing fees) requires additional data collection from product detail APIs.
    """)

# Add fees enhancement suggestion
def show_fees_enhancement_info():
    """Show information about enhancing with fees data"""
    with st.expander("🔧 Enhance with Fees Data"):
        st.markdown("""
        **Missing Fields:**
        - Offset fee and frequency
        - Application fee  
        - Other ongoing fees and frequency
        
        **To add fees data:**
        1. Enhance the scraper to fetch `fees` from product details
        2. Parse fee structures (amount, frequency, feeType)
        3. Add fee columns to the dashboard
        
        **Example fee fields to add:**
        - Application Fee ($)
        - Annual Fee ($)
        - Offset Account Fee ($ per month)
        - Redraw Fee ($)
        - Exit Fee ($)
        """)

if __name__ == "__main__":
    main()
    show_fees_enhancement_info()


