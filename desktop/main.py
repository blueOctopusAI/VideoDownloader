#!/usr/bin/env python3
"""
VideoDownloader Desktop - Smart Launcher
Automatically handles tkinter issues on macOS
"""

import sys
import os

def main():
    # Try to import tkinter first
    try:
        import tkinter
        # If successful, run the main app
        from main_app import VideoDownloaderGUI
        app = VideoDownloaderGUI()
        app.run()
        
    except ImportError as e:
        if "tkinter" in str(e) or "_tkinter" in str(e):
            print("🔧 Tkinter issue detected. Trying macOS-specific launcher...")
            # Run the macOS-specific launcher
            from launcher_macos import main as macos_main
            macos_main()
        else:
            print(f"❌ Import error: {e}")
            print("Please install dependencies: pip install -r ../desktop_requirements.txt")
            sys.exit(1)

if __name__ == "__main__":
    main()
