#!/usr/bin/env python3
"""
Enhanced Term Deposits Dashboard - Variant Level
===============================================

Streamlit dashboard for variant-level term deposit data.
Shows individual rate records with terms, tiers, and conditions.

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
    page_title="🏦 Finder - Enhanced Term Deposits Tracker (Variants)",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_enhanced_term_deposits_data():
    """Load the enhanced variant-level term deposits data"""
    try:
        # Find the most recent enhanced term deposits file
        files = glob.glob("../data/enhanced_term_deposits_*.csv")
        if not files:
            return pd.DataFrame()
        
        latest_file = max(files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        
        # Clean and process data
        df['interest_rate'] = pd.to_numeric(df['interest_rate'], errors='coerce')
        df['base_rate'] = pd.to_numeric(df['base_rate'], errors='coerce')
        df['bonus_rate'] = pd.to_numeric(df['bonus_rate'], errors='coerce')
        df['term_months'] = pd.to_numeric(df['term_months'], errors='coerce')
        df['tier_minimum'] = pd.to_numeric(df['tier_minimum'], errors='coerce')
        df['tier_maximum'] = pd.to_numeric(df['tier_maximum'], errors='coerce')
        df['minimum_deposit'] = pd.to_numeric(df['minimum_deposit'], errors='coerce')
        df['maximum_deposit'] = pd.to_numeric(df['maximum_deposit'], errors='coerce')
        
        # Create enhanced fields
        df['has_rate'] = (df['interest_rate'].notna() & (df['interest_rate'] > 0))
        df['has_bonus'] = (df['bonus_rate'].notna() & (df['bonus_rate'] > 0))
        df['is_promotional'] = df['promotional_rate'].fillna(False)
        df['is_introductory'] = df['introductory_rate'].fillna(False)
        
        # Clean term display
        df['term_display'] = df['term_display'].fillna('Not specified')
        
        # Create deposit range display
        def format_deposit_range(row):
            min_dep = row['tier_minimum'] or row['minimum_deposit']
            max_dep = row['tier_maximum'] or row['maximum_deposit']
            
            if pd.isna(min_dep) and pd.isna(max_dep):
                return 'Any amount'
            elif pd.isna(max_dep):
                return f'${min_dep:,.0f}+'
            elif pd.isna(min_dep):
                return f'Up to ${max_dep:,.0f}'
            else:
                return f'${min_dep:,.0f} - ${max_dep:,.0f}'
        
        df['deposit_range'] = df.apply(format_deposit_range, axis=1)
        
        # Create rate display with bonus info
        def format_rate_display(row):
            if pd.isna(row['interest_rate']) or row['interest_rate'] == 0:
                return 'Call bank'
            
            rate_str = f"{row['interest_rate']:.3f}%"
            
            if row['has_bonus']:
                rate_str += f" (incl. {row['bonus_rate']:.3f}% bonus)"
            
            if row['is_promotional']:
                rate_str += " 🎯 PROMO"
            elif row['is_introductory']:
                rate_str += " 🆕 INTRO"
                
            return rate_str
        
        df['rate_display'] = df.apply(format_rate_display, axis=1)
        
        return df
        
    except Exception as e:
        st.error(f"Error loading enhanced data: {str(e)}")
        return pd.DataFrame()

def format_rate(rate):
    """Format rate for display"""
    if pd.isna(rate) or rate == 0:
        return "Call bank"
    return f"{rate:.3f}%"

def format_currency(amount):
    """Format currency for display"""
    if pd.isna(amount) or amount == 0:
        return "Not specified"
    return f"${amount:,.0f}"

def main():
    """Main dashboard function"""
    
    # Title and header
    st.title("🏦 Finder - Enhanced Term Deposits Tracker")
    st.markdown("### **Variant-Level Analysis with Rate Tiers & Terms**")
    st.markdown("*Individual rate records showing deposit amounts, terms, and conditions*")
    
    # Load enhanced data
    df = load_enhanced_term_deposits_data()
    
    if df.empty:
        st.error("⚠️ No enhanced term deposit data available. Please run the enhanced scraper first.")
        st.stop()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Banks", df['bank_name'].nunique())
    
    with col2:
        banks_with_rates = df[df['has_rate']]['bank_name'].nunique()
        st.metric("Banks with Rates", banks_with_rates)
    
    with col3:
        st.metric("Rate Variants", len(df))
    
    with col4:
        variants_with_rates = len(df[df['has_rate']])
        st.metric("Variants with Rates", f"{variants_with_rates} ({variants_with_rates/len(df)*100:.1f}%)")
    
    # Sidebar filters
    st.sidebar.header("🔍 Enhanced Filters")
    
    # Bank filter
    banks_list = ['All'] + sorted(df['bank_name'].unique())
    selected_bank = st.sidebar.selectbox("**Select Bank**", banks_list)
    
    # Rate availability filter
    rate_filter = st.sidebar.selectbox(
        "**Rate Availability**",
        ['All Variants', 'Rates Available', 'Call for Rates', 'Promotional Rates', 'Bonus Rates']
    )
    
    # Term length filter
    term_options = ['All Terms'] + sorted([t for t in df['term_display'].unique() if t != 'Not specified'])
    selected_term = st.sidebar.selectbox("**Term Length**", term_options)
    
    # Deposit amount filter
    deposit_ranges = ['All Amounts'] + sorted(df['deposit_range'].unique())
    selected_deposit = st.sidebar.selectbox("**Deposit Range**", deposit_ranges)
    
    # Rate range filter
    if len(df[df['has_rate']]) > 0:
        min_rate = float(df[df['has_rate']]['interest_rate'].min())
        max_rate = float(df[df['has_rate']]['interest_rate'].max())
        
        rate_range = st.sidebar.slider(
            "**Interest Rate Range (%)**",
            min_value=min_rate,
            max_value=max_rate,
            value=(min_rate, max_rate),
            step=0.001,
            format="%.3f"
        )
    else:
        rate_range = (0.0, 10.0)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_bank != 'All':
        filtered_df = filtered_df[filtered_df['bank_name'] == selected_bank]
    
    if rate_filter == 'Rates Available':
        filtered_df = filtered_df[filtered_df['has_rate']]
    elif rate_filter == 'Call for Rates':
        filtered_df = filtered_df[~filtered_df['has_rate']]
    elif rate_filter == 'Promotional Rates':
        filtered_df = filtered_df[filtered_df['is_promotional']]
    elif rate_filter == 'Bonus Rates':
        filtered_df = filtered_df[filtered_df['has_bonus']]
    
    if selected_term != 'All Terms':
        filtered_df = filtered_df[filtered_df['term_display'] == selected_term]
    
    if selected_deposit != 'All Amounts':
        filtered_df = filtered_df[filtered_df['deposit_range'] == selected_deposit]
    
    # Apply rate range filter
    if len(filtered_df[filtered_df['has_rate']]) > 0:
        filtered_df = filtered_df[
            (~filtered_df['has_rate']) |  # Keep non-rate records
            ((filtered_df['interest_rate'] >= rate_range[0]) & 
             (filtered_df['interest_rate'] <= rate_range[1]))
        ]
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Variants", "💰 Rate Comparison", "📊 Market Analysis", "🎯 Best Rates"])
    
    with tab1:
        st.subheader(f"Term Deposit Variants - {selected_bank}")
        
        if filtered_df.empty:
            st.warning("No variants match the selected filters.")
        else:
            # Prepare display dataframe
            display_columns = [
                'bank_name', 'product_name', 'rate_display', 'term_display',
                'deposit_range', 'calculation_frequency', 'application_frequency',
                'rate_type', 'additional_info'
            ]
            
            display_df = filtered_df[display_columns].copy()
            display_df.columns = [
                'Bank', 'Product', 'Interest Rate', 'Term', 
                'Deposit Range', 'Calc Frequency', 'Payment Frequency',
                'Rate Type', 'Details'
            ]
            
            # Limit details column length
            display_df['Details'] = display_df['Details'].fillna('').apply(
                lambda x: str(x)[:80] + '...' if len(str(x)) > 80 else str(x)
            )
            
            st.dataframe(display_df, width='stretch', height=500)
            
            # Download option
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                "📄 Download Filtered Data (CSV)",
                csv_data,
                file_name=f"term_deposits_variants_{selected_bank.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with tab2:
        st.subheader("Interest Rate Comparison")
        
        rates_df = filtered_df[filtered_df['has_rate']].copy()
        
        if rates_df.empty:
            st.info("No rate data available for the selected filters.")
        else:
            # Rate vs Term scatter plot
            fig_scatter = px.scatter(
                rates_df,
                x='term_months',
                y='interest_rate',
                color='bank_name',
                size='tier_minimum',
                hover_data=['product_name', 'deposit_range', 'rate_type'],
                title="Interest Rates by Term Length",
                labels={
                    'term_months': 'Term (Months)',
                    'interest_rate': 'Interest Rate (%)',
                    'bank_name': 'Bank',
                    'tier_minimum': 'Min Deposit'
                }
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Rate distribution by bank
            if rates_df['bank_name'].nunique() > 1:
                fig_box = px.box(
                    rates_df,
                    x='bank_name',
                    y='interest_rate',
                    title="Rate Distribution by Bank"
                )
                fig_box.update_xaxes(tickangle=45)
                st.plotly_chart(fig_box, use_container_width=True)
    
    with tab3:
        st.subheader("Market Analysis")
        
        # Term popularity
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Most Popular Terms**")
            term_counts = filtered_df['term_display'].value_counts().head(10)
            if not term_counts.empty:
                fig_terms = px.bar(
                    x=term_counts.values,
                    y=term_counts.index,
                    orientation='h',
                    title="Number of Variants by Term"
                )
                st.plotly_chart(fig_terms, use_container_width=True)
        
        with col2:
            st.markdown("**Rate Type Distribution**")
            rate_type_counts = filtered_df['rate_type'].value_counts()
            if not rate_type_counts.empty:
                fig_types = px.pie(
                    values=rate_type_counts.values,
                    names=rate_type_counts.index,
                    title="Rate Types"
                )
                st.plotly_chart(fig_types, use_container_width=True)
        
        # Deposit tier analysis
        if len(filtered_df[filtered_df['tier_minimum'].notna()]) > 0:
            st.markdown("**Deposit Tiers Analysis**")
            tier_df = filtered_df[filtered_df['tier_minimum'].notna()].copy()
            
            fig_tiers = px.scatter(
                tier_df,
                x='tier_minimum',
                y='interest_rate',
                color='bank_name',
                hover_data=['product_name', 'term_display'],
                title="Interest Rates by Minimum Deposit Amount",
                labels={
                    'tier_minimum': 'Minimum Deposit ($)',
                    'interest_rate': 'Interest Rate (%)'
                }
            )
            fig_tiers.update_xaxes(type="log")
            st.plotly_chart(fig_tiers, use_container_width=True)
    
    with tab4:
        st.subheader("🏆 Best Available Rates")
        
        rates_df = filtered_df[filtered_df['has_rate']].copy()
        
        if rates_df.empty:
            st.info("No rate data available for current selection.")
        else:
            # Best rates by term
            st.markdown("**Highest Rates by Term Length**")
            
            best_by_term = rates_df.loc[rates_df.groupby('term_display')['interest_rate'].idxmax()]
            best_by_term = best_by_term.sort_values('interest_rate', ascending=False)
            
            for _, row in best_by_term.head(10).iterrows():
                col1, col2, col3, col4 = st.columns([2, 2, 3, 3])
                
                with col1:
                    st.metric("Rate", f"{row['interest_rate']:.3f}%")
                
                with col2:
                    st.metric("Term", row['term_display'])
                
                with col3:
                    st.write(f"**{row['bank_name']}**")
                    st.write(row['product_name'][:40] + '...' if len(row['product_name']) > 40 else row['product_name'])
                
                with col4:
                    st.write(f"**Deposit:** {row['deposit_range']}")
                    rate_details = []
                    if row['has_bonus']:
                        rate_details.append(f"Bonus: {row['bonus_rate']:.3f}%")
                    if row['is_promotional']:
                        rate_details.append("🎯 Promotional")
                    if rate_details:
                        st.write(" • ".join(rate_details))
                
                st.markdown("---")
            
            # Summary statistics
            st.markdown("**Rate Statistics**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Highest Rate", f"{rates_df['interest_rate'].max():.3f}%")
            
            with col2:
                st.metric("Average Rate", f"{rates_df['interest_rate'].mean():.3f}%")
            
            with col3:
                promotional_count = len(rates_df[rates_df['is_promotional']])
                st.metric("Promotional Rates", promotional_count)
            
            with col4:
                bonus_count = len(rates_df[rates_df['has_bonus']])
                st.metric("Bonus Rates", bonus_count)
    
    # Footer information
    st.markdown("---")
    st.markdown(f"""
    **📊 Enhanced Data Summary:**
    - **Variant-level analysis**: {len(df)} individual rate records from {df['bank_name'].nunique()} banks
    - **Rate coverage**: {len(df[df['has_rate']])} variants with published rates ({len(df[df['has_rate']])/len(df)*100:.1f}%)
    - **Term variations**: {df['term_display'].nunique()} different term lengths
    - **Deposit tiers**: {len(df[df['tier_minimum'].notna()])} variants with specific deposit requirements
    - **Last updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    """)

if __name__ == "__main__":
    main()


