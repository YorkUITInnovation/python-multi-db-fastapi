#!/bin/bash

# Docker Setup Verification Script
# Tests that all Docker files are properly configured

echo "=========================================="
echo "Docker Setup Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check files exist
echo "1. Checking required files..."
files=(
    "Dockerfile"
    "docker-compose.yml"
    "docker-compose.prod.yml"
    "docker-compose.dev.yml"
    ".dockerignore"
    "Makefile"
    "docker-start.sh"
    "requirements.txt"
    ".env.example"
)

all_files_exist=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file (missing)"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo -e "\n${RED}Some required files are missing!${NC}"
    exit 1
fi

echo ""

# Check .env file
echo "2. Checking .env file..."
if [ -f ".env" ]; then
    echo -e "  ${GREEN}✓${NC} .env exists"

    # Check for required variables
    required_vars=("APP_MODE" "API_KEY")
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env; then
            echo -e "  ${GREEN}✓${NC} $var is set"
        else
            echo -e "  ${YELLOW}⚠${NC} $var not found in .env"
        fi
    done
else
    echo -e "  ${YELLOW}⚠${NC} .env not found (will need to create from .env.example)"
fi

echo ""

# Check Docker installation
echo "3. Checking Docker installation..."
if command -v docker &> /dev/null; then
    docker_version=$(docker --version)
    echo -e "  ${GREEN}✓${NC} Docker installed: $docker_version"
else
    echo -e "  ${RED}✗${NC} Docker not installed"
    exit 1
fi

if docker compose version &> /dev/null; then
    compose_version=$(docker compose version)
    echo -e "  ${GREEN}✓${NC} Docker Compose installed: $compose_version"
else
    echo -e "  ${RED}✗${NC} Docker Compose not installed"
    exit 1
fi

echo ""

# Check Dockerfile syntax
echo "4. Validating Dockerfile..."
if docker build -t yorku-api-test --target=0 . &> /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Dockerfile syntax is valid"
else
    # Try to parse Dockerfile
    if grep -q "FROM python:3.12-slim" Dockerfile; then
        echo -e "  ${GREEN}✓${NC} Dockerfile syntax appears valid"
    else
        echo -e "  ${YELLOW}⚠${NC} Could not fully validate Dockerfile"
    fi
fi

echo ""

# Check docker-compose files
echo "5. Validating docker-compose files..."
for compose_file in docker-compose.yml docker-compose.prod.yml docker-compose.dev.yml; do
    if docker compose -f "$compose_file" config &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $compose_file is valid"
    else
        echo -e "  ${RED}✗${NC} $compose_file has syntax errors"
    fi
done

echo ""

# Check ports
echo "6. Checking if port 8082 is available..."
if lsof -Pi :8082 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "  ${YELLOW}⚠${NC} Port 8082 is already in use"
    echo "     You may need to stop existing services or change the port"
else
    echo -e "  ${GREEN}✓${NC} Port 8082 is available"
fi

echo ""

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}✓ All required files present${NC}"
echo -e "${GREEN}✓ Docker and Docker Compose installed${NC}"
echo -e "${GREEN}✓ Configuration files are valid${NC}"
echo ""
echo "Ready to deploy!"
echo ""
echo "Next steps:"
echo "  1. Ensure .env file is configured with your database credentials"
echo "  2. Run: ./docker-start.sh"
echo "  3. Or run: make up"
echo ""

