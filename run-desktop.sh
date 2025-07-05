#!/bin/bash
# VideoDownloader Desktop Launcher - macOS Compatible

cd "$(dirname "$0")"

echo "🚀 Starting VideoDownloader Desktop App..."

# Check if we have tkinter issues and offer solutions
check_tkinter() {
    python3 -c "import tkinter" 2>/dev/null
    return $?
}

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

# Install desktop dependencies
echo "📦 Installing desktop dependencies..."
pip install -r desktop_requirements.txt --quiet

# Check for tkinter
if ! check_tkinter; then
    echo "❌ tkinter not available with current Python"
    echo "🔧 This is common on macOS with Homebrew Python"
    echo ""
    echo "🛠️  Quick fixes:"
    echo "1. Install tkinter: ./fix-tkinter.sh"
    echo "2. Use system Python: /usr/bin/python3 desktop/main.py"
    echo "3. Install Python from python.org (includes tkinter)"
    echo ""
    read -p "Try system Python? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Launching with system Python..."
        /usr/bin/python3 desktop/main.py
        exit 0
    else
        echo "Run ./fix-tkinter.sh to install tkinter support"
        exit 1
    fi
fi

# Run the desktop app
echo "🎯 Launching VideoDownloader..."
python desktop/main.py
