#!/usr/bin/env python3
"""
Enhanced Mortgage Dashboard with Real-Time Refresh Capability
Interactive dashboard with refresh button to update data from CDR APIs
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import subprocess
import os
import glob
import time
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="🏠 Finder - Open Banking FHL Rate Tracker",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_latest_mortgage_file():
    """Get the most recent mortgage data file"""
    patterns = [
        'complete_mortgage_data_*.csv',
        'enhanced_mortgage_rates_*.csv'
    ]
    
    latest_file = None
    latest_time = 0
    
    for pattern in patterns:
        files = glob.glob(pattern)
        for file in files:
            file_time = os.path.getmtime(file)
            if file_time > latest_time:
                latest_time = file_time
                latest_file = file
    
    return latest_file

@st.cache_data
def load_complete_mortgage_data(refresh_key=None):
    """Load the complete mortgage data with fees"""
    try:
        # Get the latest data file
        latest_file = get_latest_mortgage_file()
        
        if not latest_file:
            st.error("No mortgage data files found. Please refresh the data first.")
            return pd.DataFrame()
        
        df = pd.read_csv(latest_file)
        
        # Standardize column names based on the file type
        if 'Rate (%)' in df.columns:
            # Enhanced rate file format
            df['Interest Rate (%)'] = pd.to_numeric(df['Rate (%)'], errors='coerce')
            df['Comparison Rate (%)'] = pd.to_numeric(df['Comparison Rate (%)'], errors='coerce')
            df['Owner Occupier / Investor'] = df['Loan Purpose']
            df['Fixed / Variable'] = df['Rate Type']
            df['P&I / Interest Only'] = df['Repayment Type']
            if 'Variant Name' not in df.columns:
                df['Variant Name'] = df.get('Additional Info', 'Standard')
        else:
            # Complete data file format
            df['Interest Rate (%)'] = pd.to_numeric(df['Interest Rate (%)'], errors='coerce')
            df['Comparison Rate (%)'] = pd.to_numeric(df['Comparison Rate (%)'], errors='coerce')
        
        # Clean fee columns if they exist
        fee_columns = [
            'Offset Fee ($)', 'Application Fee ($)', 'Annual Fee ($)', 
            'Monthly Fee ($)', 'Exit Fee ($)', 'Redraw Fee ($)'
        ]
        
        for col in fee_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                df[col] = np.nan
        
        # Handle missing values
        if 'Fixed Term (Months)' in df.columns:
            df['Fixed Term (Months)'] = df['Fixed Term (Months)'].fillna(0)
        else:
            df['Fixed Term (Months)'] = 0
            
        df['Variant Name'] = df['Variant Name'].fillna('Standard')
        
        # Add missing frequency columns if they don't exist
        if 'Offset Fee Frequency' not in df.columns:
            df['Offset Fee Frequency'] = 'Monthly'
        if 'Application Fee Frequency' not in df.columns:
            df['Application Fee Frequency'] = 'One-time'
        if 'Other Ongoing Fees' not in df.columns:
            df['Other Ongoing Fees'] = 'None'
        
        # Convert fixed term to readable format
        df['Fixed Term Display'] = df['Fixed Term (Months)'].apply(lambda x: 
            f"{int(x/12)} year{'s' if x/12 != 1 else ''}" if x > 0 else "N/A"
        )
        
        # Add file info for display
        file_time = datetime.fromtimestamp(os.path.getmtime(latest_file))
        st.info(f"📁 Current data: {latest_file} (Last updated: {file_time.strftime('%Y-%m-%d %H:%M:%S')})")
        
        return df
    except FileNotFoundError:
        st.error("Mortgage data file not found. Please refresh the data first.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def refresh_mortgage_data():
    """Run the enhanced rate scraper to refresh mortgage data"""
    
    progress_container = st.empty()
    status_container = st.empty()
    
    with progress_container.container():
        st.info("🔄 **Refreshing mortgage data from all Australian banks...**")
        progress_bar = st.progress(0)
        
        # Status updates
        status_container.text("🚀 Starting data collection...")
        progress_bar.progress(10)
        
        try:
            # Run the enhanced rate scraper
            status_container.text("📡 Connecting to CDR APIs...")
            progress_bar.progress(20)
            
            # Execute the scraper script
            result = subprocess.run(
                ['python3', 'enhanced_rate_scraper.py'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            progress_bar.progress(80)
            status_container.text("💾 Processing and saving data...")
            
            if result.returncode == 0:
                progress_bar.progress(100)
                status_container.text("✅ Data refresh completed successfully!")
                
                # Clear cache to reload new data
                st.cache_data.clear()
                
                # Show success message
                st.success("🎉 **Data Refreshed Successfully!**")
                st.balloons()
                
                # Extract key info from output
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'Total individual rate records:' in line:
                        st.info(f"📊 {line}")
                    elif 'Records with actual rates:' in line:
                        st.info(f"💰 {line}")
                
                time.sleep(2)  # Brief pause to show success
                st.rerun()  # Refresh the page to show new data
                
            else:
                progress_bar.progress(0)
                status_container.text("❌ Data refresh failed")
                st.error(f"**Data refresh failed:** {result.stderr}")
                
        except subprocess.TimeoutExpired:
            progress_bar.progress(0)
            status_container.text("⏰ Refresh timed out")
            st.error("**Refresh timed out.** The process is taking longer than expected. Please try again.")
            
        except Exception as e:
            progress_bar.progress(0)
            status_container.text("❌ Refresh error")
            st.error(f"**Error during refresh:** {str(e)}")

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
    
    # Refresh button in header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        if st.button("🔄 **Refresh Data**", type="primary", use_container_width=True):
            refresh_mortgage_data()
            return  # Exit to prevent further execution during refresh
    
    with col3:
        st.markdown("**Last Updated:**")
        latest_file = get_latest_mortgage_file()
        if latest_file:
            file_time = datetime.fromtimestamp(os.path.getmtime(latest_file))
            st.text(file_time.strftime('%m/%d %H:%M'))
        else:
            st.text("No data")
    
    # Load complete data (pass a refresh key to bust cache if needed)
    refresh_key = st.session_state.get('refresh_key', 0)
    df = load_complete_mortgage_data(refresh_key=refresh_key)
    
    if df.empty:
        st.warning("⚠️ **No mortgage data available.** Click 'Refresh Data' to fetch the latest rates from all Australian banks.")
        return
    
    # Data summary
    total_records = len(df)
    banks_count = df['Bank Name'].nunique() if 'Bank Name' in df.columns else 0
    records_with_rates = len(df[df['Interest Rate (%)'] > 0]) if 'Interest Rate (%)' in df.columns else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Records", total_records)
    with col2:
        st.metric("🏦 Banks", banks_count)
    with col3:
        st.metric("💰 With Rates", records_with_rates)
    with col4:
        coverage = f"{(records_with_rates/total_records)*100:.1f}%" if total_records > 0 else "0%"
        st.metric("📈 Rate Coverage", coverage)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Lender selection
    lenders = sorted(df['Bank Name'].unique()) if 'Bank Name' in df.columns else []
    if lenders:
        selected_lender = st.sidebar.selectbox(
            "**Select Lender**",
            options=lenders,
            index=0
        )
    else:
        st.error("No bank data available")
        return
    
    # Additional filters
    st.sidebar.subheader("Additional Filters")
    
    # Check if required columns exist
    required_cols = ['Fixed / Variable', 'Owner Occupier / Investor', 'P&I / Interest Only']
    
    rate_types = st.sidebar.multiselect(
        "Rate Type",
        options=df['Fixed / Variable'].unique() if 'Fixed / Variable' in df.columns else [],
        default=df['Fixed / Variable'].unique() if 'Fixed / Variable' in df.columns else []
    )
    
    loan_purposes = st.sidebar.multiselect(
        "Loan Purpose",
        options=df['Owner Occupier / Investor'].unique() if 'Owner Occupier / Investor' in df.columns else [],
        default=df['Owner Occupier / Investor'].unique() if 'Owner Occupier / Investor' in df.columns else []
    )
    
    repayment_types = st.sidebar.multiselect(
        "Repayment Type",
        options=df['P&I / Interest Only'].unique() if 'P&I / Interest Only' in df.columns else [],
        default=df['P&I / Interest Only'].unique() if 'P&I / Interest Only' in df.columns else []
    )
    
    # Offset filter
    offset_filter = st.sidebar.selectbox(
        "Offset Account",
        options=['All', 'Available', 'Not Available'],
        index=0
    )
    
    # Filter data based on selections
    filtered_df = df[df['Bank Name'] == selected_lender]
    
    if rate_types and 'Fixed / Variable' in df.columns:
        filtered_df = filtered_df[filtered_df['Fixed / Variable'].isin(rate_types)]
    if loan_purposes and 'Owner Occupier / Investor' in df.columns:
        filtered_df = filtered_df[filtered_df['Owner Occupier / Investor'].isin(loan_purposes)]
    if repayment_types and 'P&I / Interest Only' in df.columns:
        filtered_df = filtered_df[filtered_df['P&I / Interest Only'].isin(repayment_types)]
    
    # Apply offset filter
    if offset_filter == 'Available' and 'Offset Available' in df.columns:
        filtered_df = filtered_df[filtered_df['Offset Available'] == 'Y']
    elif offset_filter == 'Not Available' and 'Offset Available' in df.columns:
        filtered_df = filtered_df[filtered_df['Offset Available'] == 'N']
    
    # Main data table
    st.header(f"📋 {selected_lender} - Mortgage Rates & Fees")
    
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Prepare display columns (adapt to available columns)
    available_columns = list(filtered_df.columns)
    display_columns = []
    
    # Core columns
    if 'Product Name' in available_columns:
        display_columns.append('Product Name')
    if 'Variant Name' in available_columns:
        display_columns.append('Variant Name')
    if 'Interest Rate (%)' in available_columns:
        display_columns.append('Interest Rate (%)')
    if 'Comparison Rate (%)' in available_columns:
        display_columns.append('Comparison Rate (%)')
    if 'Owner Occupier / Investor' in available_columns:
        display_columns.append('Owner Occupier / Investor')
    if 'Fixed / Variable' in available_columns:
        display_columns.append('Fixed / Variable')
    if 'P&I / Interest Only' in available_columns:
        display_columns.append('P&I / Interest Only')
    if 'Offset Available' in available_columns:
        display_columns.append('Offset Available')
    
    # Fee columns
    fee_columns = ['Offset Fee ($)', 'Application Fee ($)', 'Annual Fee ($)', 
                   'Monthly Fee ($)', 'Exit Fee ($)', 'Redraw Fee ($)']
    for col in fee_columns:
        if col in available_columns:
            display_columns.append(col)
    
    # Additional columns
    additional_columns = ['Offset Fee Frequency', 'Application Fee Frequency', 
                         'Other Ongoing Fees', 'Fixed Term Display', 'LVR Min (%)', 'LVR Max (%)']
    for col in additional_columns:
        if col in available_columns:
            display_columns.append(col)
    
    # Create display dataframe
    display_df = filtered_df[display_columns].copy()
    
    # Rename for display
    if 'Fixed Term Display' in display_df.columns:
        display_df = display_df.rename(columns={'Fixed Term Display': 'Fixed Term'})
    if 'Other Ongoing Fees' in display_df.columns:
        display_df = display_df.rename(columns={'Other Ongoing Fees': 'Other Fees'})
    
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
                lambda x: str(x)[:100] + '...' if len(str(x)) > 100 else x
            )
        
        return formatted_df
    
    # Add search functionality
    search_term = st.text_input("🔍 Search products:", placeholder="Enter product or variant name...")
    if search_term and not display_df.empty:
        search_mask = False
        if 'Product Name' in display_df.columns:
            search_mask |= display_df['Product Name'].astype(str).str.contains(search_term, case=False, na=False)
        if 'Variant Name' in display_df.columns:
            search_mask |= display_df['Variant Name'].astype(str).str.contains(search_term, case=False, na=False)
        if isinstance(search_mask, bool) and not search_mask:
            # No searchable columns found
            pass
        else:
            display_df = display_df[search_mask]
    
    # Sort options
    if not display_df.empty:
        sort_col1, sort_col2 = st.columns(2)
        
        sortable_columns = [col for col in display_df.columns if col in ['Interest Rate (%)', 'Comparison Rate (%)', 'Application Fee ($)', 'Product Name']]
        
        with sort_col1:
            sort_by = st.selectbox(
                "Sort by:",
                options=sortable_columns if sortable_columns else ['Product Name'],
                index=0
            )
        
        with sort_col2:
            sort_order = st.selectbox(
                "Sort order:",
                options=['Ascending', 'Descending'],
                index=0
            )
        
        # Apply sorting
        if sort_by in display_df.columns:
            ascending = sort_order == 'Ascending'
            if sort_by in ['Interest Rate (%)', 'Comparison Rate (%)']:
                # Handle numeric sorting for rates
                sort_col_data = pd.to_numeric(display_df[sort_by], errors='coerce')
                display_df = display_df.iloc[sort_col_data.argsort()[::1 if ascending else -1]]
            elif sort_by == 'Application Fee ($)':
                # Handle numeric sorting for fees
                sort_col_data = pd.to_numeric(display_df[sort_by], errors='coerce')
                display_df = display_df.iloc[sort_col_data.argsort()[::1 if ascending else -1]]
            else:
                display_df = display_df.sort_values(sort_by, ascending=ascending)
    
    # Format and display the table
    if not display_df.empty:
        formatted_display_df = format_complete_dataframe(display_df)
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Complete Table", "💰 Fees Focus", "📈 Rates Focus"])
        
        with tab1:
            st.subheader("Complete Mortgage Information")
            st.dataframe(
                formatted_display_df,
                use_container_width=True,
                height=500
            )
        
        with tab2:
            st.subheader("Fees Analysis")
            
            # Fee columns only
            fee_cols = [col for col in formatted_display_df.columns if '$' in col or 'Fee' in col or 'Other Fees' in col]
            base_cols = ['Product Name', 'Variant Name'] if 'Product Name' in formatted_display_df.columns else []
            fee_focused_df = formatted_display_df[base_cols + fee_cols]
            
            st.dataframe(fee_focused_df, use_container_width=True, height=400)
            
            # Fee visualization
            if 'Application Fee ($)' in filtered_df.columns:
                fee_plot_df = filtered_df[
                    (filtered_df['Application Fee ($)'].notna()) & 
                    (filtered_df['Application Fee ($)'] > 0)
                ]
                
                if not fee_plot_df.empty and len(fee_plot_df) > 1:
                    fig_fees = px.bar(
                        fee_plot_df.head(20),  # Limit to top 20 for readability
                        x='Variant Name' if 'Variant Name' in fee_plot_df.columns else 'Product Name',
                        y='Application Fee ($)',
                        title=f"{selected_lender} - Application Fees by Product",
                        text='Application Fee ($)'
                    )
                    fig_fees.update_layout(height=400)
                    st.plotly_chart(fig_fees, use_container_width=True)
                else:
                    st.info("No application fee data available for visualization.")
        
        with tab3:
            st.subheader("Rates Analysis")
            
            # Rate columns only
            rate_cols = [col for col in formatted_display_df.columns if '%' in col or 'Rate' in col or 'Fixed' in col or 'Variable' in col]
            base_cols = ['Product Name', 'Variant Name'] if 'Product Name' in formatted_display_df.columns else []
            feature_cols = ['Owner Occupier / Investor', 'Fixed / Variable', 'P&I / Interest Only', 'Offset Available']
            feature_cols = [col for col in feature_cols if col in formatted_display_df.columns]
            
            rate_focused_df = formatted_display_df[base_cols + rate_cols + feature_cols]
            
            st.dataframe(rate_focused_df, use_container_width=True, height=400)
            
            # Rate visualization
            if len(filtered_df) > 1 and 'Interest Rate (%)' in filtered_df.columns and 'Comparison Rate (%)' in filtered_df.columns:
                # Clean data for plotting
                plot_df = filtered_df.copy()
                
                # Handle NaN values in all numeric columns
                plot_df['Application Fee ($)'] = pd.to_numeric(plot_df.get('Application Fee ($)', 0), errors='coerce').fillna(0)
                plot_df['Interest Rate (%)'] = pd.to_numeric(plot_df['Interest Rate (%)'], errors='coerce')
                plot_df['Comparison Rate (%)'] = pd.to_numeric(plot_df['Comparison Rate (%)'], errors='coerce')
                
                # Remove rows with missing rate data
                plot_df = plot_df.dropna(subset=['Interest Rate (%)', 'Comparison Rate (%)'])
                
                # Ensure size column has no zeros or negatives for better visualization
                plot_df = plot_df[plot_df['Application Fee ($)'] >= 0]
                plot_df.loc[plot_df['Application Fee ($)'] == 0, 'Application Fee ($)'] = 1  # Minimum size for visibility
                
                if not plot_df.empty and len(plot_df) > 1:
                    color_col = 'Owner Occupier / Investor' if 'Owner Occupier / Investor' in plot_df.columns else None
                    hover_cols = [col for col in ['Product Name', 'Variant Name'] if col in plot_df.columns]
                    
                    fig_rates = px.scatter(
                        plot_df,
                        x='Interest Rate (%)',
                        y='Comparison Rate (%)',
                        color=color_col,
                        size='Application Fee ($)',
                        hover_data=hover_cols,
                        title=f"{selected_lender} - Interest vs Comparison Rates"
                    )
                    fig_rates.update_layout(height=400)
                    st.plotly_chart(fig_rates, use_container_width=True)
                else:
                    st.info("No rate data available for visualization.")
    else:
        st.warning("No data to display with current filters.")

if __name__ == "__main__":
    main()
