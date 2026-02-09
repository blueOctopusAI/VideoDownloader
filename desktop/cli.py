#!/usr/bin/env python3
"""
VideoDownloader CLI — headless command-line interface for yt-dlp downloads.

Usage:
    python desktop/cli.py download URL [--quality best|worst|720p|480p|360p] [--output DIR] [--audio-only] [--format mp4|webm|mkv]
    python desktop/cli.py info URL
"""

import argparse
import json
import sys
from pathlib import Path

import yt_dlp


def load_settings() -> dict:
    """Load settings from the GUI app's settings file if it exists."""
    settings_file = Path.home() / ".videodownloader_settings.json"
    defaults = {
        "output_dir": str(Path.home() / "Downloads" / "VideoDownloader"),
        "quality": "best",
        "format_preference": "mp4",
        "audio_only": False,
    }
    try:
        if settings_file.exists():
            with open(settings_file, "r") as f:
                defaults.update(json.load(f))
    except Exception:
        pass
    return defaults


def build_format_string(quality: str, fmt: str, audio_only: bool) -> str:
    """Build yt-dlp format string from quality/format/audio preferences."""
    if audio_only:
        if fmt == "mp4":
            return "ba[ext=m4a]/ba"
        if fmt == "webm":
            return "ba[ext=webm]/ba"
        return "ba/b"

    if quality == "best":
        if fmt == "mp4":
            return "bv*[ext=mp4][height<=1080]+ba[ext=m4a]/bv*[height<=1080]+ba/b[height<=1080]"
        if fmt == "webm":
            return "bv*[ext=webm]+ba[ext=webm]/bv*+ba"
        if fmt == "mkv":
            return "bv*+ba/b"
        return "bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/b"
    if quality == "worst":
        return "wv*+wa/w"

    height = quality.replace("p", "")
    if fmt == "mp4":
        return f"bv*[height<={height}][ext=mp4]+ba[ext=m4a]/bv*[height<={height}]+ba"
    if fmt == "webm":
        return f"bv*[height<={height}][ext=webm]+ba[ext=webm]/bv*[height<={height}]+ba"
    return f"bv*[height<={height}]+ba"


def cmd_info(args):
    """Print video metadata as JSON."""
    opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(args.url, download=False)

    out = {
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
        "view_count": info.get("view_count"),
        "url": info.get("webpage_url", args.url),
        "thumbnail": info.get("thumbnail"),
        "description": info.get("description", "")[:500],
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_download(args):
    """Download a video/audio file."""
    settings = load_settings()
    output_dir = Path(args.output or settings["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    quality = args.quality or settings.get("quality", "best")
    fmt = args.format or settings.get("format_preference", "mp4")
    audio_only = args.audio_only or settings.get("audio_only", False)

    def progress_hook(d):
        if d["status"] == "downloading":
            pct = d.get("_percent_str", "?%").strip()
            speed = d.get("_speed_str", "")
            eta = d.get("_eta_str", "")
            print(f"\r  {pct}  {speed}  ETA: {eta}  ", end="", flush=True)
        elif d["status"] == "finished":
            print(f"\n  Finished: {Path(d.get('filename', '')).name}")

    ydl_opts = {
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "format": build_format_string(quality, fmt, audio_only),
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
    }

    if not audio_only and fmt in ("mp4", "webm", "mkv"):
        ydl_opts["merge_output_format"] = fmt

    print(f"Downloading: {args.url}")
    print(f"  Quality: {quality} | Format: {fmt} | Audio-only: {audio_only}")
    print(f"  Output: {output_dir}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(args.url, download=False)
        print(f"  Title: {info.get('title', 'Unknown')}")
        ydl.download([args.url])

    print("Done.")


def main():
    parser = argparse.ArgumentParser(
        prog="VideoDownloader CLI",
        description="Headless CLI for downloading videos via yt-dlp",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # info
    info_parser = sub.add_parser("info", help="Get video metadata")
    info_parser.add_argument("url", help="Video URL")

    # download
    dl_parser = sub.add_parser("download", help="Download a video")
    dl_parser.add_argument("url", help="Video URL")
    dl_parser.add_argument("--quality", choices=["best", "worst", "720p", "480p", "360p"])
    dl_parser.add_argument("--output", "-o", help="Output directory")
    dl_parser.add_argument("--audio-only", action="store_true", help="Extract audio only")
    dl_parser.add_argument("--format", choices=["mp4", "webm", "mkv", "any"])

    args = parser.parse_args()

    try:
        if args.command == "info":
            cmd_info(args)
        elif args.command == "download":
            cmd_download(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
