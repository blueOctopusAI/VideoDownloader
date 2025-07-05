#!/usr/bin/env python3
"""
VideoDownloader Desktop GUI - macOS Compatible Version
Handles tkinter installation automatically
"""

import os
import sys
import subprocess
from pathlib import Path

def install_tkinter_macos():
    """Install tkinter on macOS"""
    print("🔧 Installing tkinter support for macOS...")
    
    try:
        # Try installing python-tk via Homebrew
        result = subprocess.run(['brew', 'install', 'python-tk'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ tkinter installed via Homebrew")
            return True
    except FileNotFoundError:
        pass
    
    # Alternative: Install using system Python with tkinter
    print("⚠️  Homebrew not available or failed. Trying alternative...")
    
    # Check if system Python has tkinter
    try:
        result = subprocess.run(['/usr/bin/python3', '-c', 'import tkinter'], 
                              capture_output=True)
        if result.returncode == 0:
            print("✅ System Python has tkinter. Using system Python...")
            return "system"
    except FileNotFoundError:
        pass
    
    return False

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter
        return True
    except ImportError:
        return False

def main():
    print("🎯 VideoDownloader Desktop Launcher")
    print("=" * 50)
    
    # Check if tkinter is available
    if not check_tkinter():
        print("❌ tkinter not found. This is common on macOS with Homebrew Python.")
        print("🔧 Attempting to fix...")
        
        result = install_tkinter_macos()
        
        if result == "system":
            # Use system Python instead
            script_path = Path(__file__).parent / "main.py"
            print(f"🚀 Launching with system Python...")
            os.execv('/usr/bin/python3', ['/usr/bin/python3', str(script_path)])
        elif result == True:
            print("✅ tkinter installed. Please restart the application.")
            return
        else:
            print("❌ Failed to install tkinter automatically.")
            print("\n🛠️  Manual Fix Options:")
            print("1. Install via Homebrew:")
            print("   brew install python-tk")
            print("\n2. Use system Python (has tkinter built-in):")
            print("   /usr/bin/python3 desktop/main.py")
            print("\n3. Install Python from python.org (includes tkinter)")
            return
    
    # Import and run the main application
    try:
        from main_app import VideoDownloaderGUI
        print("🚀 Starting VideoDownloader...")
        app = VideoDownloaderGUI()
        app.run()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r ../desktop_requirements.txt")

if __name__ == "__main__":
    main()
