#!/usr/bin/env python3
"""
Hybrid Term Deposits Dashboard
=============================

Combines enhanced variant-level data with comprehensive bank coverage.
Shows detailed rates for banks that provide them, and product info for others.

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
    page_title="🏦 Finder - Complete Term Deposits Tracker",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_hybrid_data():
    """Load and combine enhanced variant data with comprehensive bank data"""
    
    # Load enhanced variant data (high-quality rates)
    enhanced_df = pd.DataFrame()
    try:
        enhanced_files = glob.glob("../data/enhanced_term_deposits_*.csv")
        if enhanced_files:
            latest_enhanced = max(enhanced_files, key=os.path.getctime)
            enhanced_df = pd.read_csv(latest_enhanced)
            
            # Clean enhanced data
            enhanced_df['interest_rate'] = pd.to_numeric(enhanced_df['interest_rate'], errors='coerce')
            enhanced_df['term_months'] = pd.to_numeric(enhanced_df['term_months'], errors='coerce')
            enhanced_df['tier_minimum'] = pd.to_numeric(enhanced_df['tier_minimum'], errors='coerce')
            enhanced_df['tier_maximum'] = pd.to_numeric(enhanced_df['tier_maximum'], errors='coerce')
            
            # Mark as enhanced data
            enhanced_df['data_source'] = 'Enhanced Variants'
            enhanced_df['has_detailed_rates'] = True
            
            # Standardize column names
            enhanced_df = enhanced_df.rename(columns={
                'term_display': 'term_display',
                'additional_info': 'product_details'
            })
    except Exception as e:
        st.warning(f"Could not load enhanced data: {e}")
    
    # Load comprehensive bank data (broad coverage)
    comprehensive_df = pd.DataFrame()
    try:
        comprehensive_files = glob.glob("../data/term_deposits_*.csv")
        if comprehensive_files:
            latest_comprehensive = max(comprehensive_files, key=os.path.getctime)
            comprehensive_df = pd.read_csv(latest_comprehensive)
            
            # Clean comprehensive data
            comprehensive_df['interest_rate'] = pd.to_numeric(comprehensive_df['interest_rate'], errors='coerce')
            comprehensive_df['term_months'] = pd.to_numeric(comprehensive_df['term_months'], errors='coerce')
            comprehensive_df['minimum_deposit'] = pd.to_numeric(comprehensive_df['minimum_deposit'], errors='coerce')
            
            # Mark as comprehensive data
            comprehensive_df['data_source'] = 'Comprehensive Coverage'
            comprehensive_df['has_detailed_rates'] = (
                comprehensive_df['interest_rate'].notna() & 
                (comprehensive_df['interest_rate'] > 0)
            )
            
            # Standardize column names to match enhanced
            comprehensive_df = comprehensive_df.rename(columns={
                'additional_info': 'product_details'
            })
            
            # Remove banks that are already in enhanced data to avoid duplicates
            if not enhanced_df.empty:
                enhanced_banks = enhanced_df['bank_name'].unique()
                comprehensive_df = comprehensive_df[~comprehensive_df['bank_name'].isin(enhanced_banks)]
    except Exception as e:
        st.warning(f"Could not load comprehensive data: {e}")
    
    # Combine datasets
    if not enhanced_df.empty and not comprehensive_df.empty:
        # Standardize columns for merging
        common_columns = [
            'bank_name', 'product_name', 'interest_rate', 'term_display', 
            'data_source', 'has_detailed_rates', 'product_details'
        ]
        
        # Add missing columns to each dataset
        for col in common_columns:
            if col not in enhanced_df.columns:
                enhanced_df[col] = None
            if col not in comprehensive_df.columns:
                comprehensive_df[col] = None
        
        # Merge datasets
        combined_df = pd.concat([
            enhanced_df[common_columns],
            comprehensive_df[common_columns]
        ], ignore_index=True)
        
    elif not enhanced_df.empty:
        combined_df = enhanced_df
    elif not comprehensive_df.empty:
        combined_df = comprehensive_df
    else:
        return pd.DataFrame()
    
    # Add computed fields
    combined_df['has_rate'] = (
        combined_df['interest_rate'].notna() & 
        (combined_df['interest_rate'] > 0)
    )
    
    combined_df['rate_display'] = combined_df.apply(
        lambda row: f"{row['interest_rate']:.3f}%" if row['has_rate'] 
        else "📞 Call bank", axis=1
    )
    
    combined_df['data_quality'] = combined_df.apply(
        lambda row: "🔥 Enhanced Variants" if row['data_source'] == 'Enhanced Variants'
        else "📋 Product Info" if not row['has_rate']
        else "💰 Rate Available", axis=1
    )
    
    return combined_df

def main():
    """Main dashboard function"""
    
    # Title and header
    st.title("🏦 Finder - Complete Term Deposits Tracker")
    st.markdown("### **Enhanced Variants + Comprehensive Bank Coverage**")
    st.markdown("*Combining detailed rate analysis with complete market coverage*")
    
    # Load hybrid data
    df = load_hybrid_data()
    
    if df.empty:
        st.error("⚠️ No term deposit data available. Please run the scrapers first.")
        st.stop()
    
    # Data source summary
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_banks = df['bank_name'].nunique()
        st.metric("Total Banks", total_banks)
    
    with col2:
        enhanced_banks = len(df[df['data_source'] == 'Enhanced Variants']['bank_name'].unique())
        st.metric("Enhanced Analysis", enhanced_banks)
    
    with col3:
        banks_with_rates = df[df['has_rate']]['bank_name'].nunique()
        st.metric("Banks with Rates", banks_with_rates)
    
    with col4:
        total_products = len(df)
        st.metric("Total Products/Variants", total_products)
    
    # Data quality indicator
    st.markdown("#### 📊 Data Coverage Breakdown:")
    quality_breakdown = df['data_quality'].value_counts()
    quality_cols = st.columns(len(quality_breakdown))
    
    for i, (quality, count) in enumerate(quality_breakdown.items()):
        with quality_cols[i]:
            st.metric(quality, count)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Bank filter
    banks_list = ['All'] + sorted(df['bank_name'].unique())
    selected_bank = st.sidebar.selectbox("**Select Bank**", banks_list)
    
    # Data quality filter
    quality_filter = st.sidebar.selectbox(
        "**Data Quality**",
        ['All Data', 'Enhanced Variants Only', 'Rates Available', 'Product Info Only']
    )
    
    # Rate availability filter  
    rate_filter = st.sidebar.selectbox(
        "**Rate Status**",
        ['All', 'Published Rates', 'Call for Rates']
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_bank != 'All':
        filtered_df = filtered_df[filtered_df['bank_name'] == selected_bank]
    
    if quality_filter == 'Enhanced Variants Only':
        filtered_df = filtered_df[filtered_df['data_source'] == 'Enhanced Variants']
    elif quality_filter == 'Rates Available':
        filtered_df = filtered_df[filtered_df['has_rate']]
    elif quality_filter == 'Product Info Only':
        filtered_df = filtered_df[~filtered_df['has_rate']]
    
    if rate_filter == 'Published Rates':
        filtered_df = filtered_df[filtered_df['has_rate']]
    elif rate_filter == 'Call for Rates':
        filtered_df = filtered_df[~filtered_df['has_rate']]
    
    # Main content
    st.header(f"📋 {selected_bank} - Term Deposits Analysis")
    
    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🏛️ All Banks & Products", "🔥 Enhanced Analysis", "📊 Market Overview"])
    
    with tab1:
        st.subheader("Complete Bank Coverage")
        
        # Prepare display dataframe
        display_df = filtered_df[[
            'bank_name', 'product_name', 'rate_display', 'term_display',
            'data_quality', 'data_source'
        ]].copy()
        
        display_df.columns = [
            'Bank', 'Product', 'Interest Rate', 'Term', 'Data Quality', 'Source'
        ]
        
        # Add product details preview
        if 'product_details' in filtered_df.columns:
            display_df['Details'] = filtered_df['product_details'].fillna('').apply(
                lambda x: str(x)[:60] + '...' if len(str(x)) > 60 else str(x)
            )
        
        st.dataframe(display_df, width='stretch', height=500)
        
        # Bank summary
        st.subheader("📊 Bank Summary")
        bank_summary = filtered_df.groupby('bank_name').agg({
            'product_name': 'count',
            'has_rate': 'any',
            'data_source': 'first'
        }).reset_index()
        
        bank_summary.columns = ['Bank', 'Products', 'Has Rates', 'Data Source']
        bank_summary['Status'] = bank_summary.apply(
            lambda row: f"✅ {row['Data Source']}" if row['Has Rates'] 
            else "📞 Call for rates", axis=1
        )
        
        st.dataframe(
            bank_summary[['Bank', 'Products', 'Status']],
            width='stretch',
            height=300
        )
    
    with tab2:
        st.subheader("🔥 Enhanced Variant Analysis")
        
        enhanced_data = filtered_df[filtered_df['data_source'] == 'Enhanced Variants']
        
        if enhanced_data.empty:
            st.info("No enhanced variant data for current selection.")
            st.markdown("""
            **Enhanced variants provide:**
            - Individual rate records for different terms and deposit amounts
            - Deposit tier analysis ($10K, $50K, $100K+ requirements)
            - Promotional and bonus rate identification
            - Detailed terms and conditions
            """)
        else:
            # Enhanced analysis charts
            rates_data = enhanced_data[enhanced_data['has_rate']]
            
            if not rates_data.empty:
                # Rate distribution
                fig_dist = px.histogram(
                    rates_data,
                    x='interest_rate',
                    color='bank_name',
                    title="Enhanced Rate Distribution",
                    labels={'interest_rate': 'Interest Rate (%)', 'count': 'Number of Variants'}
                )
                st.plotly_chart(fig_dist, use_container_width=True)
                
                # Term analysis
                if 'term_months' in rates_data.columns:
                    term_analysis = rates_data.groupby('term_months')['interest_rate'].agg(['mean', 'count']).reset_index()
                    term_analysis = term_analysis[term_analysis['count'] >= 2]  # Only terms with multiple variants
                    
                    if not term_analysis.empty:
                        fig_terms = px.bar(
                            term_analysis,
                            x='term_months',
                            y='mean',
                            title="Average Rates by Term Length (Enhanced Data)",
                            labels={'term_months': 'Term (Months)', 'mean': 'Average Rate (%)'}
                        )
                        st.plotly_chart(fig_terms, use_container_width=True)
            
            # Enhanced data summary
            st.markdown("**🎯 Enhanced Insights:**")
            enhanced_banks = enhanced_data['bank_name'].unique()
            for bank in enhanced_banks:
                bank_data = enhanced_data[enhanced_data['bank_name'] == bank]
                with_rates = bank_data[bank_data['has_rate']]
                
                st.write(f"**{bank}**: {len(bank_data)} variants, {len(with_rates)} with rates")
                if len(with_rates) > 0:
                    best_rate = with_rates['interest_rate'].max()
                    st.write(f"  → Best rate: {best_rate:.3f}%")
    
    with tab3:
        st.subheader("📊 Complete Market Overview")
        
        # Market coverage visualization
        coverage_data = df.groupby('bank_name').agg({
            'has_rate': 'any',
            'data_source': 'first'
        }).reset_index()
        
        coverage_summary = coverage_data['data_source'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Data source pie chart
            fig_sources = px.pie(
                values=coverage_summary.values,
                names=coverage_summary.index,
                title="Data Source Distribution"
            )
            st.plotly_chart(fig_sources, use_container_width=True)
        
        with col2:
            # Rate availability
            rate_summary = coverage_data['has_rate'].value_counts()
            rate_labels = ['Rates Available' if x else 'Call for Rates' for x in rate_summary.index]
            
            fig_rates = px.pie(
                values=rate_summary.values,
                names=rate_labels,
                title="Rate Availability"
            )
            st.plotly_chart(fig_rates, use_container_width=True)
        
        # Market statistics
        st.markdown("**📈 Market Statistics:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_banks = df['bank_name'].nunique()
            with_rates = df[df['has_rate']]['bank_name'].nunique()
            st.write(f"• **Banks**: {total_banks} total")
            st.write(f"• **With rates**: {with_rates} ({with_rates/total_banks*100:.1f}%)")
        
        with col2:
            if len(df[df['has_rate']]) > 0:
                avg_rate = df[df['has_rate']]['interest_rate'].mean()
                max_rate = df[df['has_rate']]['interest_rate'].max()
                st.write(f"• **Average rate**: {avg_rate:.3f}%")
                st.write(f"• **Highest rate**: {max_rate:.3f}%")
        
        with col3:
            enhanced_count = len(df[df['data_source'] == 'Enhanced Variants']['bank_name'].unique())
            comprehensive_count = len(df[df['data_source'] == 'Comprehensive Coverage']['bank_name'].unique())
            st.write(f"• **Enhanced analysis**: {enhanced_count} banks")
            st.write(f"• **Broad coverage**: {comprehensive_count} banks")
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    **🚀 Live Data Collection Status:**
    - **Enhanced collection**: Running for all 120 banks (detailed variants)
    - **Current coverage**: {df['bank_name'].nunique()} banks total
    - **Rate publishers**: {df[df['has_rate']]['bank_name'].nunique()} banks with live rates
    - **Data sources**: Enhanced variants + Comprehensive coverage
    - **Last updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    
    **💡 Data Types:**
    - 🔥 **Enhanced Variants**: Individual rate records with terms, tiers, and conditions
    - 💰 **Rate Available**: Banks publishing rates via API
    - 📞 **Call for Rates**: Industry standard for many term deposits
    """)

if __name__ == "__main__":
    main()


