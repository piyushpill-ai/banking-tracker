#!/bin/bash

# GitHub Setup and Initial Commit Script
# Run this after creating your GitHub repository

set -e

echo "🚀 Setting up GitHub repository for Banking Rate Tracker..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "🎉 Initial commit: Australian Banking Rate Tracker

Features:
✅ Real-time mortgage rates dashboard with refresh functionality
✅ Term deposits dashboard with variant-level analysis  
✅ CDR API integration for 120+ Australian banks
✅ AWS EC2 deployment scripts
✅ Nginx reverse proxy configuration
✅ Systemd service management
✅ Comprehensive documentation

Ready for production deployment! 🚀"

echo ""
echo "🔗 Next steps:"
echo ""
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: banking-tracker"
echo "   - Make it public or private (your choice)"
echo "   - Don't initialize with README (we already have one)"
echo ""
echo "2. Add your GitHub repository as remote:"
echo "   git remote add origin https://github.com/YOUR-USERNAME/banking-tracker.git"
echo ""
echo "3. Push to GitHub:"
echo "   git push -u origin main"
echo ""
echo "4. Your repository will be ready for AWS deployment!"
echo ""
echo "✅ Git repository is ready for GitHub!"
