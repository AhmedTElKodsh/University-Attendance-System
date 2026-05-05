#!/bin/bash
# Production Deployment Helper Script
# This script helps automate production deployment steps
# Run this ON YOUR PRODUCTION SERVER, not in development

set -e  # Exit on error

echo "=========================================="
echo "Mustian Face MVP - Production Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}❌ Do not run this script as root${NC}"
   exit 1
fi

echo -e "${YELLOW}⚠️  This script should be run ON YOUR PRODUCTION SERVER${NC}"
echo -e "${YELLOW}⚠️  Make sure you have reviewed PRODUCTION_DEPLOYMENT_CHECKLIST.md${NC}"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Step 1: Check Python version
echo ""
echo "Step 1: Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python version: $PYTHON_VERSION${NC}"

# Step 2: Check if .env exists
echo ""
echo "Step 2: Checking environment configuration..."
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ backend/.env not found${NC}"
    echo "Creating from .env.production.example..."
    cp backend/.env.production.example backend/.env
    echo -e "${YELLOW}⚠️  Please edit backend/.env with your production values${NC}"
    echo "   Required: SECRET_KEY, DATABASE_URL, CORS_ORIGINS"
    exit 1
else
    echo -e "${GREEN}✅ backend/.env found${NC}"
fi

# Step 3: Check SECRET_KEY
echo ""
echo "Step 3: Validating SECRET_KEY..."
SECRET_KEY=$(grep "^SECRET_KEY=" backend/.env | cut -d '=' -f2)
if [ "$SECRET_KEY" == "REPLACE_WITH_SECURE_RANDOM_KEY_64_CHARS" ] || [ -z "$SECRET_KEY" ]; then
    echo -e "${RED}❌ SECRET_KEY not set or using default${NC}"
    echo "Generate a secure key with:"
    echo "  python3 -c \"import secrets; print(secrets.token_hex(32))\""
    exit 1
else
    echo -e "${GREEN}✅ SECRET_KEY is set${NC}"
fi

# Step 4: Check ENVIRONMENT
echo ""
echo "Step 4: Checking ENVIRONMENT setting..."
ENVIRONMENT=$(grep "^ENVIRONMENT=" backend/.env | cut -d '=' -f2)
if [ "$ENVIRONMENT" != "production" ]; then
    echo -e "${RED}❌ ENVIRONMENT is not set to 'production'${NC}"
    echo "Current value: $ENVIRONMENT"
    exit 1
else
    echo -e "${GREEN}✅ ENVIRONMENT=production${NC}"
fi

# Step 5: Check PostgreSQL
echo ""
echo "Step 5: Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL client installed${NC}"
    
    # Extract database connection details
    DATABASE_URL=$(grep "^DATABASE_URL=" backend/.env | cut -d '=' -f2-)
    if [[ $DATABASE_URL == postgresql://* ]]; then
        echo -e "${GREEN}✅ Using PostgreSQL${NC}"
    else
        echo -e "${RED}❌ Not using PostgreSQL (found: $DATABASE_URL)${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  PostgreSQL client not found${NC}"
    echo "Install with: sudo apt install postgresql-client"
fi

# Step 6: Create virtual environment
echo ""
echo "Step 6: Setting up virtual environment..."
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
fi

# Step 7: Install dependencies
echo ""
echo "Step 7: Installing dependencies..."
source backend/venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r backend/requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 8: Test imports
echo ""
echo "Step 8: Testing critical imports..."
python3 -c "from backend.main import app; from backend.config import settings; print('✅ Imports successful')"

# Step 9: Initialize database
echo ""
echo "Step 9: Database initialization..."
read -p "Initialize database tables? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 -c "from backend.database import create_tables; create_tables(); print('✅ Tables created')"
fi

# Step 10: Create admin user
echo ""
echo "Step 10: Admin user setup..."
read -p "Create admin user? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd backend
    python3 seed.py
    cd ..
    echo -e "${YELLOW}⚠️  IMPORTANT: Change the default admin password!${NC}"
fi

# Step 11: Test application
echo ""
echo "Step 11: Testing application startup..."
echo "Starting test server on port 8000..."
cd backend
timeout 5 uvicorn main:app --host 127.0.0.1 --port 8000 > /dev/null 2>&1 &
TEST_PID=$!
sleep 3

if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo -e "${GREEN}✅ Application starts successfully${NC}"
    kill $TEST_PID 2>/dev/null || true
else
    echo -e "${RED}❌ Application failed to start${NC}"
    kill $TEST_PID 2>/dev/null || true
    exit 1
fi
cd ..

# Summary
echo ""
echo "=========================================="
echo "Deployment Preparation Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}✅ All checks passed${NC}"
echo ""
echo "Next steps:"
echo "1. Change admin password (default: admin123)"
echo "2. Set up systemd service (see PRODUCTION_DEPLOYMENT_CHECKLIST.md)"
echo "3. Configure Nginx reverse proxy"
echo "4. Set up SSL with Let's Encrypt"
echo "5. Configure firewall"
echo "6. Set up monitoring and backups"
echo ""
echo "See PRODUCTION_DEPLOYMENT_CHECKLIST.md for detailed instructions."
echo ""
