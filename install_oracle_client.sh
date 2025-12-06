#!/bin/bash

# Script to install Oracle Instant Client for python-oracledb thick mode
# This is needed to support older Oracle password verifier types

set -e

echo "Installing Oracle Instant Client..."
echo ""

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Set version
VERSION="21.15"
MAJOR_VERSION="21"

# Create installation directory
INSTALL_DIR="/opt/oracle"
sudo mkdir -p "$INSTALL_DIR"

cd /tmp

if [ "$ARCH" == "x86_64" ]; then
    # Download for x86_64
    echo "Downloading Oracle Instant Client Basic Light for x86_64..."
    wget -q https://download.oracle.com/otn_software/linux/instantclient/2115000/instantclient-basiclite-linux.x64-21.15.0.0.0dbru.zip -O instantclient.zip

    echo "Extracting..."
    sudo unzip -q -o instantclient.zip -d "$INSTALL_DIR"

    # Create symlink for easier access
    sudo ln -sf "$INSTALL_DIR/instantclient_${MAJOR_VERSION}_${MAJOR_VERSION#2}15" "$INSTALL_DIR/instantclient"

    LIB_DIR="$INSTALL_DIR/instantclient_${MAJOR_VERSION}_15"
elif [ "$ARCH" == "aarch64" ] || [ "$ARCH" == "arm64" ]; then
    # Download for ARM64
    echo "Downloading Oracle Instant Client Basic Light for ARM64..."
    wget -q https://download.oracle.com/otn_software/linux/instantclient/2115000/instantclient-basiclite-linux.arm64-21.15.0.0.0dbru.zip -O instantclient.zip

    echo "Extracting..."
    sudo unzip -q -o instantclient.zip -d "$INSTALL_DIR"

    LIB_DIR="$INSTALL_DIR/instantclient_${MAJOR_VERSION}_15"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

# Install required library
echo "Installing libaio1..."
sudo apt-get update -qq
sudo apt-get install -y -qq libaio1

# Configure library path
echo "Configuring library path..."
echo "$LIB_DIR" | sudo tee /etc/ld.so.conf.d/oracle-instantclient.conf > /dev/null
sudo ldconfig

# Clean up
rm instantclient.zip

echo ""
echo "✓ Oracle Instant Client installed successfully!"
echo "  Library directory: $LIB_DIR"
echo ""
echo "To use thick mode, add this to your .env file:"
echo "  ORACLE_CLIENT_LIB=$LIB_DIR"
echo ""
echo "Or export it in your shell:"
echo "  export ORACLE_CLIENT_LIB=$LIB_DIR"

