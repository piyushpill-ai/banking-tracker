#!/bin/bash

# AWS EC2 Deployment Script for Australian Banking Rate Tracker
# This script sets up the environment and deploys both dashboards

set -e

echo "🚀 Starting AWS EC2 Deployment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and pip
echo "🐍 Installing Python and dependencies..."
sudo apt install -y python3.11 python3.11-pip python3.11-venv git nginx

# Create application directory
APP_DIR="/opt/banking-tracker"
echo "📁 Setting up application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone repository (you'll need to replace with your GitHub repo URL)
echo "📥 Cloning repository..."
cd /opt
if [ -d "banking-tracker" ]; then
    echo "Directory exists, pulling latest changes..."
    cd banking-tracker
    git pull origin main
else
    # Replace 'your-username' with your actual GitHub username
    git clone https://github.com/your-username/banking-tracker.git
    cd banking-tracker
fi

# Create virtual environment
echo "🔧 Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
echo "📝 Setting up logging..."
mkdir -p logs
mkdir -p data

# Set permissions
sudo chown -R $USER:$USER /opt/banking-tracker

# Create systemd service files for both dashboards
echo "🔧 Creating systemd services..."

# Mortgage Dashboard Service
sudo tee /etc/systemd/system/mortgage-dashboard.service > /dev/null <<EOF
[Unit]
Description=Mortgage Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/banking-tracker
Environment=PATH=/opt/banking-tracker/venv/bin
ExecStart=/opt/banking-tracker/venv/bin/streamlit run enhanced_mortgage_dashboard.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Term Deposits Dashboard Service  
sudo tee /etc/systemd/system/term-deposits-dashboard.service > /dev/null <<EOF
[Unit]
Description=Term Deposits Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/banking-tracker/term-deposits/dashboard
Environment=PATH=/opt/banking-tracker/venv/bin
ExecStart=/opt/banking-tracker/venv/bin/streamlit run hybrid_term_deposits_dashboard.py --server.port 8505 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx reverse proxy
echo "🌐 Setting up Nginx..."
sudo tee /etc/nginx/sites-available/banking-tracker > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or EC2 public IP

    # Mortgage Dashboard
    location /mortgages {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
        
        # Streamlit specific headers
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Server \$host;
    }

    # Term Deposits Dashboard
    location /term-deposits {
        proxy_pass http://localhost:8505;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
        
        # Streamlit specific headers
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Server \$host;
    }

    # Default redirect to mortgage dashboard
    location / {
        return 301 /mortgages;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/banking-tracker /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Start and enable services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable mortgage-dashboard
sudo systemctl enable term-deposits-dashboard
sudo systemctl start mortgage-dashboard
sudo systemctl start term-deposits-dashboard

# Configure firewall
echo "🔒 Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "✅ Checking service status..."
sudo systemctl status mortgage-dashboard --no-pager
sudo systemctl status term-deposits-dashboard --no-pager
sudo systemctl status nginx --no-pager

echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "📊 Your dashboards are available at:"
echo "🏠 Mortgages: http://your-ec2-ip/mortgages"
echo "🏦 Term Deposits: http://your-ec2-ip/term-deposits"
echo ""
echo "📝 To check logs:"
echo "   sudo journalctl -u mortgage-dashboard -f"
echo "   sudo journalctl -u term-deposits-dashboard -f"
echo ""
echo "🔄 To update the application:"
echo "   cd /opt/banking-tracker && git pull && sudo systemctl restart mortgage-dashboard term-deposits-dashboard"
