---
name: dev
description: Dev environment manager for starting, stopping, and managing the VideoDownloader application and its dependencies
---

# Dev Skill -- VideoDownloader

## Setup (first time)

```bash
cd /Users/jashanno/Developer/projects/VideoDownloader
./scripts/setup.sh
```

This creates the venv, installs Python dependencies, checks for FFmpeg, and creates the default download directory at `~/Downloads/VideoDownloader`.

## Run the Application

```bash
cd /Users/jashanno/Developer/projects/VideoDownloader
./scripts/run-desktop.sh
```

Or manually:

```bash
cd /Users/jashanno/Developer/projects/VideoDownloader
source venv/bin/activate
python desktop/main.py
```

## Update yt-dlp

When downloads start failing (common -- sites change their APIs frequently):

```bash
source venv/bin/activate
pip install --upgrade yt-dlp
```

## Dependencies

- **Python 3.8+** with tkinter support
- **FFmpeg** (`brew install ffmpeg` on macOS)
- **Python packages**: customtkinter, yt-dlp, pillow, requests (see `desktop_requirements.txt`)

## Troubleshooting

- **tkinter not found on macOS**: Run `./scripts/fix-tkinter.sh` or use system Python: `/usr/bin/python3 desktop/main.py`
- **FFmpeg not found**: `brew install ffmpeg`
- **Module not found**: Ensure venv is activated: `source venv/bin/activate && pip install -r desktop_requirements.txt`

## Notes

- This is a dormant/supporting project. Keep changes minimal.
- The GUI is a single-file monolith (`desktop/main_app.py`). No build step required.
- Downloads go to `~/Downloads/VideoDownloader` by default (configurable in the app settings).
