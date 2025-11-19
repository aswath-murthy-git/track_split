#!/bin/bash

echo "=================================="
echo "  🎵 Fixing Demucs Installation"
echo "=================================="
echo ""

# Check Python version
echo "📌 Checking Python version..."
python3 --version

# Check if pip is available
echo ""
echo "📌 Checking pip..."
pip3 --version

# Install/Upgrade pip
echo ""
echo "📌 Upgrading pip..."
pip3 install --upgrade pip

# Install PyTorch first (required for Demucs)
echo ""
echo "📌 Installing PyTorch..."
pip3 install torch torchaudio

# Install Demucs
echo ""
echo "📌 Installing Demucs..."
pip3 install demucs

# Install other dependencies
echo ""
echo "📌 Installing other dependencies..."
pip3 install flask werkzeug pydub soundfile numpy

# Install ffmpeg if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "📌 Checking ffmpeg (macOS)..."
    if ! command -v ffmpeg &> /dev/null; then
        echo "⚠️  ffmpeg not found. Installing with Homebrew..."
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "⚠️  Homebrew not found. Please install ffmpeg manually:"
            echo "   Visit: https://ffmpeg.org/download.html"
        fi
    else
        echo "✅ ffmpeg already installed"
    fi
fi

# Verify installations
echo ""
echo "=================================="
echo "  ✅ Verifying Installation"
echo "=================================="

echo ""
echo "Testing Demucs..."
python3 -c "import demucs; print('✅ Demucs installed successfully!')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Demucs installation failed!"
    exit 1
fi

echo ""
echo "Testing PyTorch..."
python3 -c "import torch; print('✅ PyTorch installed successfully!')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ PyTorch installation failed!"
    exit 1
fi

echo ""
echo "Testing Flask..."
python3 -c "import flask; print('✅ Flask installed successfully!')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Flask installation failed!"
    exit 1
fi

echo ""
echo "Testing pydub..."
python3 -c "import pydub; print('✅ Pydub installed successfully!')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Pydub installation failed!"
    exit 1
fi

echo ""
echo "=================================="
echo "  🎉 Installation Complete!"
echo "=================================="
echo ""
echo "You can now run the app:"
echo "  python3 web_app.py"
echo ""