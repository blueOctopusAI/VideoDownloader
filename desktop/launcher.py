#!/usr/bin/env python3
"""
Simple launcher for VideoDownloader Desktop
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Get the script directory
    script_dir = Path(__file__).parent
    main_script = script_dir / "main.py"
    
    if not main_script.exists():
        print("❌ main.py not found!")
        sys.exit(1)
    
    # Run the main application
    try:
        subprocess.run([sys.executable, str(main_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start VideoDownloader: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 VideoDownloader closed")

if __name__ == "__main__":
    main()
