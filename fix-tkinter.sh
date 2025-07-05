#!/bin/bash
# Quick fix for tkinter on macOS

echo "🔧 Fixing tkinter for macOS..."

# Check if we have Homebrew
if command -v brew &> /dev/null; then
    echo "📦 Installing python-tk via Homebrew..."
    brew install python-tk
    
    if [ $? -eq 0 ]; then
        echo "✅ tkinter installed successfully!"
        echo "🚀 You can now run: python desktop/main.py"
    else
        echo "⚠️  Homebrew install failed. Trying alternative..."
    fi
else
    echo "❌ Homebrew not found."
fi

echo ""
echo "🛠️  Alternative Solutions:"
echo ""
echo "1. Use system Python (has tkinter built-in):"
echo "   /usr/bin/python3 desktop/main.py"
echo ""
echo "2. Install Python from python.org (includes tkinter):"
echo "   https://python.org/downloads"
echo ""
echo "3. Manual Homebrew install:"
echo "   brew install python-tk"
