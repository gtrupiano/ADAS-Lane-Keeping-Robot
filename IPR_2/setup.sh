#!/bin/bash

set -e

echo "Updating package lists..."
sudo apt update

echo "Installing only required system packages..."
sudo apt install -y \
    python3-venv \
    python3-picamera2 \
    python3-smbus \
    i2c-tools

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python packages from requirements.txt..."
pip install -r requirements.txt

echo "Setup complete."