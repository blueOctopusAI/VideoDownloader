# VideoDownloader 🎯

A modern, beautiful desktop application for downloading videos from YouTube, TikTok, Instagram, Twitter, and 1000+ other platforms. Built with Python and CustomTkinter for a sleek, native experience.

![VideoDownloader](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## ✨ Features

### 🎨 **Modern Interface**
- **Dark Theme**: Beautiful, modern dark UI with rounded corners
- **Real-time Progress**: Live progress bars with speed and ETA
- **Smart Layout**: Responsive design that adapts to any screen size
- **Native Feel**: System-integrated dialogs and notifications

### 🚀 **Powerful Downloading**
- **Universal Support**: YouTube, TikTok, Instagram, Twitter, and 1000+ sites
- **Quality Control**: Choose specific video quality or format
- **Audio Extraction**: Download audio-only in MP3, M4A, FLAC formats
- **Subtitle Support**: Automatically download available subtitles
- **Batch Downloads**: Queue multiple videos simultaneously

### 🔧 **Advanced Features**
- **Video Preview**: See thumbnails, metadata, and available formats
- **Smart Clipboard**: Auto-detect and paste video URLs
- **Download Management**: Track and organize downloads
- **Persistent Settings**: Remember preferences across sessions
- **Error Recovery**: Clear error messages and retry options

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** ([Download here](https://python.org))
- **FFmpeg** (for video processing)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd VideoDownloader
   ```

2. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r desktop_requirements.txt
   ```

4. **Launch the application**
   ```bash
   python desktop/main.py
   ```

### One-Line Setup (macOS/Linux)
```bash
chmod +x scripts/run-desktop.sh && ./scripts/run-desktop.sh
```

## 📖 Usage

### Basic Video Download
1. **Launch VideoDownloader**
2. **Paste video URL** in the input field (or click "Paste" button)
3. **Click "Download"** or press Enter
4. **Watch progress** in real-time
5. **Find your video** in the configured download directory

### Video Preview & Format Selection
1. **Paste URL** and click "Preview"
2. **View video info** including thumbnail, duration, uploader
3. **Browse available formats** (different qualities and file types)
4. **Select specific format** or choose "Download Best Quality"

### Settings Configuration
- **Download Directory**: Choose where files are saved
- **Video Quality**: Set default quality (best, 720p, 480p, etc.)
- **Audio Only**: Enable for music downloads
- **Subtitles**: Auto-download subtitles in multiple languages

## 🎯 Interface Overview

```
🎯 VideoDownloader
├── Video URL Input Field        # Paste URLs here
├── [Paste] [Download] [Preview] # Action buttons  
├── [Settings]                   # Configure preferences
└── Downloads Panel              # Track progress
    ├── Active Downloads         # Live progress bars
    ├── Completed Downloads      # Finished videos  
    └── [Clear Completed]        # Cleanup button
```

## ⚙️ Configuration

### Settings Panel
Access via the ⚙️ Settings button:

- **Download Directory**: `~/Downloads/VideoDownloader` (default)
- **Video Quality**: `best`, `worst`, `720p`, `480p`, `360p`
- **Audio Only**: Extract audio files only
- **Include Subtitles**: Download subtitle files

### Keyboard Shortcuts
- **Enter**: Start download
- **Cmd/Ctrl+V**: Paste URL (after clicking input field)
- **Escape**: Close preview/settings windows

### File Organization
```
~/Downloads/VideoDownloader/
├── Video Title 1.mp4
├── Video Title 2.webm  
├── Audio Track.mp3
└── Subtitle File.en.srt
```

## 🛠️ Technical Details

### Built With
- **Python 3.8+**: Core application logic
- **CustomTkinter**: Modern, beautiful GUI framework
- **yt-dlp**: Powerful video extraction library
- **Pillow**: Image processing for thumbnails
- **Requests**: HTTP requests for metadata

### Architecture
```
VideoDownloader/
├── desktop/
│   ├── main.py              # GUI entry point
│   ├── main_app.py          # Full GUI application
│   ├── cli.py               # Headless CLI (no GUI required)
│   ├── launcher.py          # Simple launcher
│   └── launcher_macos.py    # macOS tkinter fix
├── scripts/
│   ├── run-desktop.sh       # Launch script
│   ├── setup.sh             # First-time setup
│   └── fix-tkinter.sh       # macOS tkinter fix
├── docs/
│   └── README.md            # This file
├── venv/                    # Python virtual environment
└── desktop_requirements.txt # Python dependencies
```

### Performance
- **Lightweight**: ~50MB RAM usage
- **Fast Startup**: < 2 second launch time
- **Efficient Downloads**: Multi-threaded processing
- **Low CPU**: Minimal background processing

## 🌐 Supported Platforms

### Video Platforms (1000+ supported)
- **YouTube** (including playlists and channels)
- **TikTok** (videos and user profiles)
- **Instagram** (posts, stories, reels)
- **Twitter/X** (videos and GIFs)
- **Facebook** (public videos)
- **Twitch** (VODs and clips)
- **Vimeo** (public videos)
- **And 1000+ more platforms**

### Operating Systems
- **macOS** 10.14+ (Mojave and later)
- **Windows** 10/11
- **Linux** (Ubuntu, Fedora, etc.)

## 🔧 Advanced Usage

### Headless CLI

VideoDownloader includes a headless CLI for scripting and pipeline integration. No GUI required.

```bash
source venv/bin/activate

# Get video metadata (JSON output)
python desktop/cli.py info "https://youtube.com/watch?v=..."

# Download a video
python desktop/cli.py download "https://youtube.com/watch?v=..."

# Download with options
python desktop/cli.py download "https://youtube.com/watch?v=..." \
  --quality 720p \
  --format mp4 \
  --output ~/Downloads/

# Download audio only
python desktop/cli.py download "https://youtube.com/watch?v=..." --audio-only
```

**CLI Options:**

| Command | Description |
|---------|-------------|
| `info URL` | Print video metadata as JSON (title, duration, uploader, etc.) |
| `download URL` | Download a video/audio file |

**Download Options:**

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--quality` | `best`, `worst`, `720p`, `480p`, `360p` | `best` | Video quality |
| `--format` | `mp4`, `webm`, `mkv`, `any` | `mp4` | Output format |
| `--output, -o` | directory path | `~/Downloads/VideoDownloader/` | Save location |
| `--audio-only` | flag | off | Extract audio only |

The CLI reads settings from `~/.videodownloader_settings.json` (shared with the GUI) but command-line flags override them.

**Pipeline Integration:** This CLI is used by the [video-pipeline](https://github.com/blueOctopusAI/video-pipeline) project for automated download-transcribe-route workflows.

### GUI Launch
```bash
# Direct launch with Python
python desktop/main.py
```

### Custom Download Directory
Set via Settings panel or modify the settings file:
```json
{
  "output_dir": "/path/to/custom/downloads",
  "quality": "best",
  "audio_only": false,
  "include_subtitles": true
}
```

### Batch Processing
1. Download multiple videos by adding URLs one by one
2. All downloads run concurrently
3. Progress tracked individually
4. Failed downloads can be retried

## 🐛 Troubleshooting

### Common Issues

**"FFmpeg not found"**
```bash
# macOS (with Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

**"Module not found" errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r desktop_requirements.txt
```

**Downloads fail or are slow**
- Check internet connection
- Try different video quality settings
- Ensure sufficient disk space
- Some platforms may have rate limiting

**Video not supported**
- Verify the URL is correct and public
- Check if yt-dlp supports the platform
- Some private or region-locked content may not work

### Getting Help
1. Check the error message in the app
2. Verify URL works in a web browser
3. Try different quality settings
4. Check the Downloads folder for partial files

## 🎉 Why Desktop GUI?

### Advantages over Web Interface
- **Native Performance**: No browser overhead
- **Better Integration**: System dialogs and notifications  
- **Offline Capability**: Works without internet for local files
- **Resource Efficient**: Lower memory usage
- **Privacy**: No web tracking, completely local
- **System Integration**: Native file browser integration

### Perfect for Video Downloading
- **File Management**: Direct access to file system
- **Progress Tracking**: Native progress indicators
- **Error Handling**: Better error dialogs
- **Multi-tasking**: Run in background while using other apps
- **Stability**: More stable than browser-based solutions

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **yt-dlp** team for the amazing video extraction library
- **CustomTkinter** for the beautiful, modern GUI framework
- **Python** community for excellent package ecosystem

---

**Happy downloading! 🎬**

> *VideoDownloader - The modern way to download videos*
