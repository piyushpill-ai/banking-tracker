# Term Deposits Rate Tracker

Comprehensive term deposit rates and features tracker for Australian banks using Consumer Data Standards (CDS) APIs.

## 📁 Project Structure

```
term-deposits/
├── scripts/           # Data collection scripts
├── dashboard/         # Streamlit dashboard
├── data/             # Collected data files
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd term-deposits
pip install -r requirements.txt
```

### 2. Collect Term Deposit Data
```bash
cd scripts
python3 term_deposits_scraper.py
```

### 3. Launch Dashboard
```bash
cd dashboard
streamlit run term_deposits_dashboard.py --server.port 8502
```

Then visit: **http://localhost:8502**

## 📊 Data Fields Collected

### Rate Information
- **Interest Rate**: Annual interest rate percentage
- **Rate Type**: FIXED, VARIABLE, or other
- **Bonus Rate**: Additional bonus rates if applicable

### Term Information
- **Term Length**: 3 months, 6 months, 1 year, 2 years, etc.
- **Term Months**: Numeric representation for filtering

### Deposit Requirements
- **Minimum Deposit**: Lowest amount required
- **Maximum Deposit**: Highest amount accepted

### Fees
- **Account Fee**: Annual or monthly account maintenance fees
- **Early Withdrawal Fee**: Penalties for early withdrawal

### Additional Information
- **Product Details**: Description and features
- **Eligibility**: Who can apply
- **Application URL**: Direct link to apply

## 🏦 Supported Banks

The scraper processes **120+ Australian banks** including:
- ANZ, CBA, NAB, Westpac (Big 4)
- UBank, ME Bank, ING
- Credit unions and building societies
- Regional and community banks

## 📈 Dashboard Features

### Filtering Options
- **Bank Selection**: Filter by specific financial institution
- **Term Length**: Choose specific term periods
- **Rate Type**: Fixed vs Variable rates
- **Deposit Range**: Filter by minimum deposit amount
- **Interest Rate Range**: Set rate boundaries
- **Product Search**: Search by product name or features

### Analysis Views
- **Complete Table**: All term deposit products
- **Rate Analysis**: Interest rates vs term lengths
- **Deposit Analysis**: Minimum deposit requirements

### Sorting & Comparison
- Sort by interest rate, term length, or minimum deposit
- Interactive charts and visualizations
- Export filtered results

## 🔄 Data Updates

The scraper can be run regularly to get fresh data:
- **Manual**: Run the scraper script manually
- **Scheduled**: Set up cron jobs for automatic updates
- **Real-time**: All data comes directly from bank APIs

## 📝 Notes

- Data quality depends on bank API availability
- Some banks may have rate limits or access restrictions
- Term deposit rates change frequently
- Always verify rates directly with the bank before making decisions

## 🆘 Troubleshooting

### No Data Available
- Run the scraper first: `python3 scripts/term_deposits_scraper.py`
- Check internet connection
- Some bank APIs may be temporarily unavailable

### Dashboard Won't Start
- Ensure port 8502 is available
- Install all requirements: `pip install -r requirements.txt`
- Try a different port: `--server.port 8503`

### Import Errors
- Make sure you're in the correct directory
- Check that `luke_prior_bank_list_1758106523.py` exists in scripts folder

## 📊 Data Files

Generated files are saved in `data/` folder:
- `term_deposits_YYYYMMDD_HHMMSS.csv` - Main data file
- `term_deposits_YYYYMMDD_HHMMSS.json` - JSON format
- `term_deposits_scraper_YYYYMMDD_HHMMSS.log` - Scraping logs

## 🎯 Future Enhancements

- Historical rate tracking
- Rate alerts and notifications
- Comparison with RBA cash rate
- Integration with calendar for maturity tracking
- Advanced portfolio analysis tools


