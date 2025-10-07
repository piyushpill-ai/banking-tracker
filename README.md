# 🏦 Australian Banking Rate Tracker

A comprehensive real-time dashboard system for tracking mortgage and term deposit rates from all Australian banks using Consumer Data Right (CDR) APIs.

## 🌟 Features

### 🏠 **Mortgage Dashboard**
- **Real-time rates** from 120+ Australian banks
- **Detailed rate variants** (LVR, fixed terms, loan purpose)
- **Comprehensive fee analysis** (application, offset, ongoing fees)
- **Interactive filtering** by lender, rate type, loan purpose
- **One-click data refresh** from live CDR APIs
- **Exportable data** in CSV/JSON formats

### 🏦 **Term Deposits Dashboard**
- **Complete market coverage** across all banks
- **Deposit tier analysis** ($10K, $50K, $100K+ ranges)
- **Term-specific rates** (3, 6, 12, 24+ months)
- **Promotional rate tracking** and bonus identification
- **Hybrid view** combining detailed and comprehensive data

## 🚀 Live Deployment

### **Quick Deploy to AWS EC2**

1. **Launch EC2 Instance** (Ubuntu 22.04 LTS, t3.medium recommended)
2. **Clone & Deploy:**
```bash
git clone https://github.com/your-username/banking-tracker.git
cd banking-tracker
chmod +x deploy-to-ec2.sh
./deploy-to-ec2.sh
```

3. **Access Dashboards:**
- 🏠 **Mortgages:** `http://your-ec2-ip/mortgages`
- 🏦 **Term Deposits:** `http://your-ec2-ip/term-deposits`

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CDR APIs      │───▶│   Data Scrapers  │───▶│   Streamlit     │
│   (120+ Banks)  │    │   (Enhanced)     │    │   Dashboards    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                ▲                        │
                                │                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   GitHub Repo    │    │   AWS EC2       │
                       │   (Auto Deploy)  │    │   (Production)  │
                       └──────────────────┘    └─────────────────┘
```

## 💻 Local Development

### **Prerequisites**
- Python 3.11+
- Git

### **Setup**
```bash
# Clone repository
git clone https://github.com/your-username/banking-tracker.git
cd banking-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run mortgage dashboard
streamlit run enhanced_mortgage_dashboard.py --server.port 8501

# Run term deposits dashboard (in separate terminal)
cd term-deposits/dashboard
streamlit run hybrid_term_deposits_dashboard.py --server.port 8505
```

### **Access Locally**
- 🏠 **Mortgages:** http://localhost:8501
- 🏦 **Term Deposits:** http://localhost:8505

## 📊 Data Sources

### **Consumer Data Right (CDR) APIs**
- **Coverage:** All 120+ registered banking institutions
- **Data Types:** Products, rates, fees, features
- **Update Frequency:** Real-time via refresh button
- **Compliance:** Follows Australian CDR standards

### **Rate Extraction**
- **Individual variants** as separate records
- **LVR-specific rates** (60%, 70%, 80%, 90%+)
- **Fixed term options** (1-5 years)
- **Purpose-based rates** (Owner Occupier vs Investment)
- **Repayment type variations** (P&I vs Interest Only)

## 🔧 Configuration

### **Environment Variables**
```bash
# Optional: Set custom data refresh intervals
export REFRESH_INTERVAL_MINUTES=60

# Optional: Set custom log levels
export LOG_LEVEL=INFO

# Optional: Set custom data directory
export DATA_DIR=./data
```

### **AWS EC2 Requirements**
- **Instance Type:** t3.medium or larger
- **Storage:** 20GB+ EBS volume
- **Security Groups:** Allow HTTP (80), HTTPS (443), SSH (22)
- **OS:** Ubuntu 22.04 LTS

## 🚀 Deployment Options

### **1. One-Click AWS Deployment**
Use the provided `deploy-to-ec2.sh` script for automatic setup.

### **2. Manual Docker Deployment**
```bash
# Build images
docker build -t mortgage-dashboard .
docker build -t term-deposits-dashboard ./term-deposits

# Run containers
docker run -d -p 8501:8501 mortgage-dashboard
docker run -d -p 8505:8505 term-deposits-dashboard
```

### **3. GitHub Actions CI/CD**
Automated deployment pipeline included for seamless updates.

## 🔄 Data Refresh

### **Automatic Refresh**
- **Dashboard Button:** Click "🔄 Refresh Data" in the UI
- **Process:** Fetches from all 120+ bank APIs
- **Duration:** 2-5 minutes for complete collection
- **Output:** New timestamped data files

### **Programmatic Refresh**
```bash
# Mortgage data
python enhanced_rate_scraper.py

# Term deposits data  
cd term-deposits/scripts
python enhanced_term_deposits_scraper.py
```

## 📈 Performance

### **Data Scale**
- **Mortgage Records:** 5,000+ individual rate variants
- **Term Deposit Records:** 2,000+ rate and tier combinations
- **Bank Coverage:** 120+ institutions
- **Update Speed:** ~30 banks per minute

### **System Requirements**
- **RAM:** 4GB+ recommended
- **CPU:** 2+ cores for parallel API calls
- **Storage:** 1GB+ for data files and logs
- **Network:** Stable internet for CDR API access

## 🔒 Security

### **Data Privacy**
- **No Personal Data:** Only public rate information
- **CDR Compliant:** Follows Australian privacy standards
- **Local Storage:** Data files stored locally/on your server

### **API Security**
- **Rate Limiting:** Respects CDR API rate limits
- **Error Handling:** Graceful handling of API failures
- **Retry Logic:** Automatic retry for transient failures

## 🐛 Troubleshooting

### **Common Issues**

**Dashboard Not Loading:**
```bash
# Check service status
sudo systemctl status mortgage-dashboard
sudo systemctl status term-deposits-dashboard

# View logs
sudo journalctl -u mortgage-dashboard -f
```

**Data Refresh Failing:**
```bash
# Check internet connectivity
curl -I https://api.anz/cds-au/v1/banking/products

# Run scraper manually
python enhanced_rate_scraper.py
```

**Nginx Issues:**
```bash
# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Open** Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Consumer Data Standards Australia** for CDR API specifications
- **Australian banks** for providing open banking data
- **Streamlit** for the excellent dashboard framework
- **Luke Prior** for inspiration on banking data collection

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/your-username/banking-tracker/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-username/banking-tracker/discussions)
- **Documentation:** [Wiki](https://github.com/your-username/banking-tracker/wiki)

---

**Made with ❤️ for the Australian banking transparency**