# 🚀 AWS EC2 Deployment Guide

## Pre-Deployment Checklist

### 1. 📁 **GitHub Repository Setup**
- [ ] GitHub repository created
- [ ] Code pushed to `main` branch
- [ ] Repository URL noted for deployment

### 2. ☁️ **AWS EC2 Instance Setup**

**Launch EC2 Instance:**
- **AMI:** Ubuntu Server 22.04 LTS
- **Instance Type:** t3.medium (2 vCPU, 4GB RAM) or larger
- **Storage:** 20GB GP3 EBS volume
- **Key Pair:** Create/use existing SSH key pair

**Security Group Configuration:**
```
Type            Protocol    Port Range    Source
SSH             TCP         22           Your IP
HTTP            TCP         80           0.0.0.0/0
HTTPS           TCP         443          0.0.0.0/0
Custom TCP      TCP         8501         0.0.0.0/0 (temporary)
Custom TCP      TCP         8505         0.0.0.0/0 (temporary)
```

## 🛠️ Deployment Steps

### Step 1: Connect to EC2 Instance
```bash
# Replace with your key file and EC2 public IP
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### Step 2: Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Step 3: Install Git
```bash
sudo apt install -y git
```

### Step 4: Clone Repository
```bash
# Replace with your actual GitHub repository URL
git clone https://github.com/YOUR-USERNAME/banking-tracker.git
cd banking-tracker
```

### Step 5: Make Script Executable and Run
```bash
chmod +x deploy-to-ec2.sh
./deploy-to-ec2.sh
```

### Step 6: Update Configuration
```bash
# Edit the deployment script to use your domain/IP
sudo nano /etc/nginx/sites-available/banking-tracker

# Replace 'your-domain.com' with your EC2 public IP or domain
# Replace 'your-ec2-ip' with your actual EC2 public IP
```

### Step 7: Restart Services
```bash
sudo systemctl restart nginx
sudo systemctl restart mortgage-dashboard
sudo systemctl restart term-deposits-dashboard
```

## 🌐 Access Your Dashboards

After successful deployment:

- **🏠 Mortgage Dashboard:** `http://your-ec2-public-ip/mortgages`
- **🏦 Term Deposits Dashboard:** `http://your-ec2-public-ip/term-deposits`

## 📊 Monitoring and Maintenance

### Check Service Status
```bash
# Check all services
sudo systemctl status mortgage-dashboard
sudo systemctl status term-deposits-dashboard  
sudo systemctl status nginx

# View real-time logs
sudo journalctl -u mortgage-dashboard -f
sudo journalctl -u term-deposits-dashboard -f
```

### Update Application
```bash
cd /opt/banking-tracker
git pull origin main
sudo systemctl restart mortgage-dashboard term-deposits-dashboard
```

### Monitor System Resources
```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Check running processes
htop
```

## 🔒 Security Hardening

### 1. Setup SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### 2. Configure Firewall
```bash
# Check current status
sudo ufw status

# Ensure proper rules
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw delete allow 8501
sudo ufw delete allow 8505
sudo ufw --force enable
```

### 3. Regular Security Updates
```bash
# Setup automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 🚨 Troubleshooting

### Dashboard Not Loading
```bash
# Check if services are running
sudo systemctl status mortgage-dashboard term-deposits-dashboard

# Restart services if needed
sudo systemctl restart mortgage-dashboard term-deposits-dashboard

# Check nginx configuration
sudo nginx -t
sudo systemctl restart nginx
```

### Port Issues
```bash
# Check what's using ports
sudo netstat -tlnp | grep -E ':8501|:8505|:80'

# Kill processes if needed
sudo pkill -f streamlit
sudo systemctl restart mortgage-dashboard term-deposits-dashboard
```

### Memory Issues
```bash
# Check memory usage
free -h

# If low memory, consider upgrading instance type
# or optimizing the applications
```

### Log Analysis
```bash
# Check application logs
sudo journalctl -u mortgage-dashboard --since "1 hour ago"
sudo journalctl -u term-deposits-dashboard --since "1 hour ago"

# Check nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 📈 Performance Optimization

### 1. **Enable Caching**
Add to your Streamlit apps:
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    # Your data loading function
    pass
```

### 2. **Database Optimization**
Consider using PostgreSQL or Redis for larger datasets:
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Redis
sudo apt install -y redis-server
```

### 3. **Load Balancing** (For High Traffic)
Setup multiple EC2 instances with an Application Load Balancer.

## 🔄 Continuous Deployment

### GitHub Actions Setup
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to EC2

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to EC2
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ubuntu
        key: ${{ secrets.EC2_KEY }}
        script: |
          cd /opt/banking-tracker
          git pull origin main
          sudo systemctl restart mortgage-dashboard term-deposits-dashboard
```

Add to GitHub Secrets:
- `EC2_HOST`: Your EC2 public IP
- `EC2_KEY`: Your private key content

## 💰 Cost Optimization

### **Instance Sizing**
- **Development:** t3.small ($15/month)  
- **Production:** t3.medium ($30/month)
- **High Traffic:** t3.large ($60/month)

### **Storage Optimization**
- Use GP3 instead of GP2 for better price/performance
- Enable EBS optimization
- Consider S3 for large data files

### **Reserved Instances**
Save up to 75% with 1-year or 3-year commitments.

## 📞 Support

If you encounter issues:

1. **Check the logs** first using the commands above
2. **Review the troubleshooting section**
3. **Create an issue** on GitHub with detailed error messages
4. **Include system information** (Ubuntu version, instance type, etc.)

---

**🎉 Congratulations! Your Banking Rate Tracker is now live on AWS EC2!**
