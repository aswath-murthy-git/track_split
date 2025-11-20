#!/bin/bash

echo "=================================="
echo "  Track Splitter - Installation"
echo "=================================="
echo ""

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

python3 --version
echo "✓ Python found"
echo ""

# Check pip
echo "Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip not found"
    echo "Please install pip"
    exit 1
fi

echo "✓ pip found"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "=================================="
echo "  Installation Complete!"
echo "=================================="
echo ""
echo "Run: python3 track_split.py"
echo ""