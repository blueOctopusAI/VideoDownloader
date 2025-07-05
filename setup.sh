#!/bin/bash
# VideoDownloader Desktop Setup Script for macOS

set -e

echo "🚀 Setting up VideoDownloader Desktop..."

# Check if we're in the right directory
if [ ! -f "setup.sh" ]; then
    echo "❌ Please run this script from the VideoDownloader project root"
    exit 1
fi

# Check Python version
echo "📋 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Found Python $PYTHON_VERSION"

# Check for FFmpeg
echo "📋 Checking FFmpeg installation..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n1 | awk '{print $3}')
    echo "✅ Found FFmpeg $FFMPEG_VERSION"
else
    echo "⚠️  FFmpeg not found. Installing via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
        echo "✅ FFmpeg installed successfully"
    else
        echo "❌ Homebrew not found. Please install FFmpeg manually:"
        echo "   brew install ffmpeg"
        echo "   Or visit: https://ffmpeg.org/download.html"
        exit 1
    fi
fi

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r desktop_requirements.txt

# Test installation
echo "🧪 Testing installation..."
python -c "import customtkinter; import yt_dlp; from PIL import Image; import requests; print('✅ All dependencies installed successfully')"

# Make launch script executable
chmod +x run-desktop.sh

# Create downloads directory
echo "📁 Creating downloads directory..."
mkdir -p ~/Downloads/VideoDownloader
echo "✅ Downloads will be saved to: ~/Downloads/VideoDownloader"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Quick Start:"
echo "   ./run-desktop.sh              # Launch VideoDownloader"
echo "   python desktop/main.py        # Alternative launch method"
echo ""
echo "📁 Download location: ~/Downloads/VideoDownloader"
echo ""
echo "🎉 Ready to download videos!"
