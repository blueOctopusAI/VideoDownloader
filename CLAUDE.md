# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A desktop GUI application for downloading videos from YouTube, TikTok, Instagram, Twitter/X, and 1000+ platforms. Built with Python and CustomTkinter for a modern dark-themed native experience. Uses yt-dlp as the download engine.

**Status**: Supporting/dormant. Serves as the download companion for the VideoToTranscript pipeline -- download videos here, generate transcripts there.

**GitHub**: github.com/blueOctopusAI/VideoDownloader

## Stack

- **Language**: Python 3.8+
- **GUI**: CustomTkinter (dark theme, modern widgets)
- **Download engine**: yt-dlp
- **Image handling**: Pillow (thumbnails)
- **HTTP**: Requests
- **System dependency**: FFmpeg (required for video processing)
- **Environment**: Python venv (`venv/`)

## Key Files and Directories

```
VideoDownloader/
├── desktop/                    # Application source
│   ├── main.py                 # Entry point — detects tkinter, launches GUI
│   ├── main_app.py             # Full GUI application (~52KB, single-file)
│   ├── launcher.py             # Simple subprocess launcher
│   └── launcher_macos.py       # macOS-specific tkinter fix launcher
├── scripts/
│   ├── run-desktop.sh          # Main launch script (activates venv, installs deps, runs)
│   ├── setup.sh                # First-time setup (venv, deps, FFmpeg check)
│   └── fix-tkinter.sh          # Fixes tkinter on macOS Homebrew Python
├── docs/
│   └── README.md               # Full user-facing documentation
├── desktop_requirements.txt    # Python deps: customtkinter, yt-dlp, pillow, requests
├── to_delete/                  # Cleanup staging (safe to remove)
└── venv/                       # Python virtual environment (gitignored)
```

## Running the App

```bash
# First-time setup
./scripts/setup.sh

# Launch
./scripts/run-desktop.sh

# Or directly
source venv/bin/activate
python desktop/main.py
```

## Architecture Notes

- The entire GUI is in a single file (`desktop/main_app.py`, ~52KB). The `VideoDownloaderGUI` class owns the window, download queue, settings, and all UI panels.
- Downloads run in background threads with progress callbacks to the UI.
- Settings persist as JSON in the user's home directory.
- macOS has a known tkinter issue with Homebrew Python; the launcher chain (`main.py` -> `launcher_macos.py`) handles this automatically.

## Relationship to VideoToTranscript

VideoDownloader and VideoToTranscript form a two-step pipeline:
1. **VideoDownloader** -- download video/audio files from any platform
2. **VideoToTranscript** -- generate transcripts from those files

Both are SUPPORTING tier projects in the Blue Octopus portfolio. They feed content into the intelligence-hub knowledge base (transcripts go to `knowledge/transcripts/`).

## Development Notes

- This project is dormant. Changes should be minimal and purposeful.
- The main_app.py monolith works but would benefit from decomposition if active development resumes.
- yt-dlp updates frequently; run `pip install --upgrade yt-dlp` if downloads start failing.
