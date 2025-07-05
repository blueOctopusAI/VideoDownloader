#!/usr/bin/env python3
"""
VideoDownloader Desktop GUI
A modern desktop application for downloading videos using yt-dlp
Built with CustomTkinter for a sleek, modern interface
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from queue import Queue, Empty
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re

import customtkinter as ctk
import yt_dlp
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DownloadItem:
    """Represents a single download item"""
    def __init__(self, url: str, title: str = "Unknown", thumbnail: str = None):
        self.id = f"download_{int(time.time())}_{id(self)}"
        self.url = url
        self.title = title
        self.thumbnail = thumbnail
        self.status = "pending"  # pending, downloading, completed, failed, cancelled
        self.progress = 0.0
        self.speed = ""
        self.eta = ""
        self.file_size = ""
        self.filename = ""
        self.filepath = ""
        self.error = ""
        self.start_time = datetime.now()
        self.end_time = None

class VideoPreviewWindow:
    """Popup window for video preview and format selection"""
    
    def __init__(self, parent, video_info: Dict, callback):
        self.parent = parent
        self.video_info = video_info
        self.callback = callback
        # Store format mappings for selection
        self.format_map = {}  # Maps listbox index to format_id
        
        # Create window
        self.window = ctk.CTkToplevel(parent.root)
        self.window.title("Video Preview")
        self.window.geometry("800x600")
        self.window.transient(parent.root)
        self.window.grab_set()
        
        self.setup_ui()
        self.load_video_info()
    
    def setup_ui(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Video Preview", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 30))
        
        # Content frame for better organization
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Video info frame
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 20))
        
        # Thumbnail and details
        self.thumbnail_label = ctk.CTkLabel(info_frame, text="")
        self.thumbnail_label.pack(side="left", padx=20, pady=20)
        
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        self.title_label = ctk.CTkLabel(
            details_frame, 
            text="", 
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=400
        )
        self.title_label.pack(anchor="w", pady=(0, 10))
        
        self.details_label = ctk.CTkLabel(
            details_frame, 
            text="", 
            font=ctk.CTkFont(size=12),
            wraplength=400
        )
        self.details_label.pack(anchor="w")
        
        # Format selection
        format_frame = ctk.CTkFrame(main_frame)
        format_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        format_label = ctk.CTkLabel(
            format_frame, 
            text="Available Formats", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        format_label.pack(pady=(10, 5))
        
        # Format list
        self.format_listbox = tk.Listbox(
            format_frame,
            bg="#2b2b2b",
            fg="white",
            selectbackground="#1f538d",
            font=("SF Pro Display", 11),
            height=8
        )
        self.format_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame, 
            text="Cancel",
            command=self.close,
            fg_color="gray"
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        download_btn = ctk.CTkButton(
            button_frame, 
            text="Download Selected",
            command=self.download_selected
        )
        download_btn.pack(side="right")
        
        download_best_btn = ctk.CTkButton(
            button_frame, 
            text="Download Best Quality",
            command=self.download_best
        )
        download_best_btn.pack(side="right", padx=(0, 10))
    
    def load_video_info(self):
        # Set title and details
        title = self.video_info.get('title', 'Unknown Title')
        self.title_label.configure(text=title)
        
        # Format details
        duration = self.video_info.get('duration', 0)
        uploader = self.video_info.get('uploader', 'Unknown')
        view_count = self.video_info.get('view_count', 0)
        
        duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
        view_str = f"{view_count:,}" if view_count else "Unknown"
        
        details = f"Uploader: {uploader}\nDuration: {duration_str}\nViews: {view_str}"
        self.details_label.configure(text=details)
        
        # Load thumbnail
        self.load_thumbnail()
        
        # Load formats
        self.load_formats()
    
    def load_thumbnail(self):
        thumbnail_url = self.video_info.get('thumbnail')
        if thumbnail_url:
            try:
                response = requests.get(thumbnail_url, timeout=5)
                img = Image.open(BytesIO(response.content))
                img = img.resize((160, 90), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.thumbnail_label.configure(image=photo, text="")
                self.thumbnail_label.image = photo  # Keep a reference
            except Exception as e:
                print(f"Failed to load thumbnail: {e}")
    
    def load_formats(self):
        formats = self.video_info.get('formats', [])
        
        # Group and sort formats
        video_formats = []
        audio_formats = []
        
        for fmt in formats:
            if fmt.get('vcodec') and fmt.get('vcodec') != 'none':
                video_formats.append(fmt)
            elif fmt.get('acodec') and fmt.get('acodec') != 'none':
                audio_formats.append(fmt)
        
        # Sort by quality
        video_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
        audio_formats.sort(key=lambda x: x.get('abr', 0), reverse=True)
        
        # Clear previous format mappings
        self.format_map.clear()
        listbox_index = 0
        
        # Add to listbox with format mapping
        self.format_listbox.insert(tk.END, "=== VIDEO FORMATS ===")
        listbox_index += 1
        
        for fmt in video_formats[:10]:  # Limit to 10 best
            height = fmt.get('height', 'Unknown')
            ext = fmt.get('ext', 'Unknown')
            filesize = fmt.get('filesize')
            size_str = f" ({filesize//1024//1024}MB)" if filesize else ""
            
            text = f"{height}p {ext.upper()}{size_str}"
            self.format_listbox.insert(tk.END, text)
            # Map this listbox index to the format_id
            self.format_map[listbox_index] = fmt.get('format_id')
            listbox_index += 1
        
        if audio_formats:
            self.format_listbox.insert(tk.END, "")
            listbox_index += 1
            self.format_listbox.insert(tk.END, "=== AUDIO FORMATS ===")
            listbox_index += 1
            
            for fmt in audio_formats[:5]:  # Limit to 5 best
                abr = fmt.get('abr', 'Unknown')
                ext = fmt.get('ext', 'Unknown')
                filesize = fmt.get('filesize')
                size_str = f" ({filesize//1024//1024}MB)" if filesize else ""
                
                text = f"{abr}kbps {ext.upper()}{size_str}"
                self.format_listbox.insert(tk.END, text)
                # Map this listbox index to the format_id
                self.format_map[listbox_index] = fmt.get('format_id')
                listbox_index += 1
    
    def download_selected(self):
        selection = self.format_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a format to download.")
            return
        
        # Get the selected index
        selected_index = selection[0]
        
        # Check if the selected item is a header or empty line
        if selected_index not in self.format_map:
            messagebox.showwarning("Invalid Selection", "Please select a valid format (not a header or empty line).")
            return
        
        # Get the format_id for the selected format
        format_id = self.format_map[selected_index]
        if not format_id:
            messagebox.showwarning("Invalid Format", "Selected format has no valid ID.")
            return
        
        # Pass the specific format_id to the download callback
        self.callback(self.video_info.get('webpage_url', self.video_info.get('url')), {'format_id': format_id})
        self.close()
    
    def download_best(self):
        self.callback(self.video_info.get('webpage_url', self.video_info.get('url')), {'quality': 'best'})
        self.close()
    
    def close(self):
        self.window.destroy()

class DownloadProgressFrame:
    """Frame showing download progress for a single item"""
    
    def __init__(self, parent_frame, download_item: DownloadItem, callback_remove):
        self.download_item = download_item
        self.callback_remove = callback_remove
        
        # Main frame for this download
        self.frame = ctk.CTkFrame(parent_frame)
        self.frame.pack(fill="x", padx=10, pady=5)
        
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        # Top row: title and remove button
        top_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.title_label = ctk.CTkLabel(
            top_frame, 
            text=self.download_item.title,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.title_label.pack(side="left", fill="x", expand=True)
        
        self.status_label = ctk.CTkLabel(
            top_frame,
            text=self.download_item.status.title(),
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.pack(side="right", padx=(10, 5))
        
        self.remove_btn = ctk.CTkButton(
            top_frame,
            text="✕",
            width=30,
            height=30,
            command=self.remove,
            fg_color="red",
            hover_color="darkred"
        )
        self.remove_btn.pack(side="right")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 5))
        self.progress_bar.set(0)
        
        # Bottom row: details
        bottom_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.details_label = ctk.CTkLabel(
            bottom_frame,
            text="Preparing...",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        self.details_label.pack(side="left")
        
        self.url_label = ctk.CTkLabel(
            bottom_frame,
            text=self.download_item.url[:50] + "..." if len(self.download_item.url) > 50 else self.download_item.url,
            font=ctk.CTkFont(size=10),
            text_color="darkgray",
            anchor="e"
        )
        self.url_label.pack(side="right")
    
    def update_display(self):
        # Update status
        status_colors = {
            "pending": "orange",
            "downloading": "lightblue", 
            "completed": "lightgreen",
            "failed": "lightcoral",
            "cancelled": "gray"
        }
        
        self.status_label.configure(
            text=self.download_item.status.title(),
            text_color=status_colors.get(self.download_item.status, "gray")
        )
        
        # Update progress bar
        self.progress_bar.set(self.download_item.progress / 100.0)
        
        # Update details
        if self.download_item.status == "downloading":
            details = f"{self.download_item.progress:.1f}%"
            if self.download_item.speed:
                details += f" • {self.download_item.speed}"
            if self.download_item.eta:
                details += f" • ETA: {self.download_item.eta}"
            if self.download_item.file_size:
                details += f" • {self.download_item.file_size}"
        elif self.download_item.status == "completed":
            details = f"Completed • {self.download_item.filename}"
        elif self.download_item.status == "failed":
            details = f"Failed: {self.download_item.error}"
        else:
            details = "Preparing..."
        
        self.details_label.configure(text=details)
    
    def remove(self):
        self.callback_remove(self.download_item.id)
        self.frame.destroy()

class VideoDownloaderGUI:
    """Main application window"""
    
    def __init__(self):
        self.downloads: Dict[str, DownloadItem] = {}
        self.download_frames: Dict[str, DownloadProgressFrame] = {}
        self.settings = self.load_settings()
        self.current_preview_data = None
        self.preview_items = []
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("VideoDownloader")
        self.root.geometry("800x600")
        
        # Set icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.setup_ui()
        
        # Start update thread
        self.start_update_thread()
    
    def load_settings(self) -> Dict:
        """Load settings from file"""
        settings_file = Path.home() / ".videodownloader_settings.json"
        default_settings = {
            "output_dir": str(Path.home() / "Downloads" / "VideoDownloader"),
            "quality": "best",
            "format_preference": "mp4",
            "audio_only": False,
            "include_subtitles": False,
            "concurrent_downloads": 3,
            "organize_in_folders": False,
            "save_metadata": False
        }
        
        try:
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    default_settings.update(saved_settings)
        except Exception as e:
            print(f"Failed to load settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Save settings to file"""
        settings_file = Path.home() / ".videodownloader_settings.json"
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")
    
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Header with title and settings
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=8, pady=(8, 12))
        
        # Title on left
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎯 VideoDownloader",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=15, pady=12)
        
        # Settings button on top right
        settings_btn = ctk.CTkButton(
            header_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            fg_color="gray",
            height=30,
            width=100,
            font=ctk.CTkFont(size=11)
        )
        settings_btn.pack(side="right", padx=15, pady=12)
        
        # URL input section
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", padx=8, pady=(0, 12))
        
        input_label = ctk.CTkLabel(
            input_frame,
            text="Video URL:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        input_label.pack(anchor="w", padx=15, pady=(12, 4))
        
        url_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        url_frame.pack(fill="x", padx=15, pady=(0, 8))
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="Paste video URL here (YouTube, TikTok, Instagram, etc.)",
            font=ctk.CTkFont(size=11),
            height=32
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.url_entry.bind("<Return>", lambda e: self.analyze_url())
        self.url_entry.bind("<KeyRelease>", self.on_url_change)
        
        paste_btn = ctk.CTkButton(
            url_frame,
            text="Paste",
            width=60,
            height=32,
            font=ctk.CTkFont(size=11),
            command=self.paste_url
        )
        paste_btn.pack(side="right")
        
        # Download type options
        options_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=15, pady=(0, 12))
        
        options_label = ctk.CTkLabel(
            options_frame,
            text="Download Options:",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        options_label.pack(side="left", padx=(0, 15))
        
        self.video_checkbox_var = ctk.BooleanVar(value=True)
        self.video_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="🎥 Video",
            variable=self.video_checkbox_var,
            font=ctk.CTkFont(size=11)
        )
        self.video_checkbox.pack(side="left", padx=(0, 15))
        
        self.audio_checkbox_var = ctk.BooleanVar(value=False)
        self.audio_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="🎵 Audio",
            variable=self.audio_checkbox_var,
            font=ctk.CTkFont(size=11)
        )
        self.audio_checkbox.pack(side="left", padx=(0, 15))
        
        self.metadata_checkbox_var = ctk.BooleanVar(value=False)
        self.metadata_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="📄 Metadata",
            variable=self.metadata_checkbox_var,
            font=ctk.CTkFont(size=11)
        )
        self.metadata_checkbox.pack(side="left")
        
        # Main content area - two columns
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        
        # Left column - Content Preview
        self.preview_frame = ctk.CTkFrame(content_frame)
        self.preview_frame.pack(side="left", fill="both", expand=True, padx=(8, 4), pady=8)
        
        self.setup_preview_area()
        
        # Right column - Downloads Queue
        self.downloads_frame = ctk.CTkFrame(content_frame)
        self.downloads_frame.pack(side="right", fill="both", expand=True, padx=(4, 8), pady=8)
        
        downloads_header = ctk.CTkFrame(self.downloads_frame)
        downloads_header.pack(fill="x", padx=8, pady=(8, 4))
        
        downloads_label = ctk.CTkLabel(
            downloads_header,
            text="Downloads Queue",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        downloads_label.pack(side="left", padx=10, pady=6)
        
        clear_btn = ctk.CTkButton(
            downloads_header,
            text="Clear Completed",
            command=self.clear_completed,
            fg_color="red",
            width=100,
            height=26,
            font=ctk.CTkFont(size=10)
        )
        clear_btn.pack(side="right", padx=10, pady=6)
        
        # Scrollable downloads list
        self.downloads_scroll = ctk.CTkScrollableFrame(self.downloads_frame)
        self.downloads_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Ready",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.status_label.pack(anchor="w", padx=15, pady=(0, 8))
    
    def setup_preview_area(self):
        """Setup the preview content area"""
        # Preview header
        preview_header = ctk.CTkFrame(self.preview_frame)
        preview_header.pack(fill="x", padx=8, pady=(8, 4))
        
        self.preview_title_label = ctk.CTkLabel(
            preview_header,
            text="Content Preview",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.preview_title_label.pack(side="left", padx=10, pady=6)
        
        self.content_type_label = ctk.CTkLabel(
            preview_header,
            text="Enter URL to analyze content",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.content_type_label.pack(side="right", padx=10, pady=6)
        
        # Scrollable preview content
        self.preview_scroll = ctk.CTkScrollableFrame(self.preview_frame)
        self.preview_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 6))
        
        # Selection controls
        selection_frame = ctk.CTkFrame(self.preview_frame)
        selection_frame.pack(fill="x", padx=8, pady=(0, 8))
        
        select_all_btn = ctk.CTkButton(
            selection_frame,
            text="Select All",
            command=self.select_all_items,
            width=80,
            height=26,
            font=ctk.CTkFont(size=10)
        )
        select_all_btn.pack(side="left", padx=8, pady=6)
        
        select_none_btn = ctk.CTkButton(
            selection_frame,
            text="Select None",
            command=self.select_no_items,
            fg_color="gray",
            width=80,
            height=26,
            font=ctk.CTkFont(size=10)
        )
        select_none_btn.pack(side="left", padx=(4, 8), pady=6)
        
        # Add to Queue button
        self.add_to_queue_btn = ctk.CTkButton(
            selection_frame,
            text="Add to Queue →",
            command=self.add_selected_to_queue,
            fg_color="green",
            hover_color="darkgreen",
            width=120,
            height=26,
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.add_to_queue_btn.pack(side="right", padx=8, pady=6)
        
        self.selection_count_label = ctk.CTkLabel(
            selection_frame,
            text="0 items selected",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.selection_count_label.pack(side="right", padx=(10, 4), pady=6)
    
    def on_url_change(self, event=None):
        """Handle URL entry changes - auto-analyze after a short delay"""
        # Cancel any existing after call
        if hasattr(self, '_url_change_after_id'):
            self.root.after_cancel(self._url_change_after_id)
        
        # Set a new delay
        url = self.url_entry.get().strip()
        if url and self.is_valid_url(url):
            self._url_change_after_id = self.root.after(1000, self.analyze_url)  # 1 second delay
    
    def analyze_url(self):
        """Analyze URL and populate content preview"""
        url = self.url_entry.get().strip()
        if not url:
            return
        
        if not self.is_valid_url(url):
            self.content_type_label.configure(text="Invalid URL")
            return
        
        self.content_type_label.configure(text="Analyzing...")
        
        # Get content info in background thread
        threading.Thread(
            target=self._analyze_content_worker,
            args=(url,),
            daemon=True
        ).start()
    
    def add_selected_to_queue(self):
        """Add selected preview items to download queue"""
        if not self.preview_items:
            messagebox.showwarning("No Content", "Please analyze content first.")
            return
        
        selected_items = [item for item in self.preview_items if item.get('selected', False)]
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select items to add to queue.")
            return
        
        # Get selected download options
        download_video = self.video_checkbox_var.get()
        download_audio = self.audio_checkbox_var.get()
        download_metadata = self.metadata_checkbox_var.get()
        
        if not any([download_video, download_audio, download_metadata]):
            messagebox.showwarning("No Options", "Please select at least one download option (Video, Audio, or Metadata).")
            return
        
        # Add items to download queue
        for item in selected_items:
            if download_video:
                video_options = {
                    'type': 'video',
                    'quality': self.settings.get('quality', 'best'),
                    'format_preference': self.settings.get('format_preference', 'mp4')
                }
                self.start_download(item['url'], video_options)
            
            if download_audio:
                audio_options = {
                    'type': 'audio',
                    'audio_only': True
                }
                self.start_download(item['url'], audio_options)
            
            if download_metadata:
                metadata_options = {
                    'type': 'metadata',
                    'metadata_only': True
                }
                self.start_download(item['url'], metadata_options)
        
        # Clear selections
        self.select_no_items()
    
    def paste_url(self):
        """Paste URL from clipboard"""
        try:
            clipboard_text = self.root.clipboard_get()
            if clipboard_text and ("youtube.com" in clipboard_text or "youtu.be" in clipboard_text or "://" in clipboard_text):
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clipboard_text)
                # Trigger analysis
                self.analyze_url()
        except tk.TclError:
            pass  # Clipboard empty or error
    

    
    def select_all_items(self):
        """Select all preview items"""
        for item in self.preview_items:
            item['selected'] = True
        self.update_preview_display()
        self.update_selection_count()
    
    def select_no_items(self):
        """Deselect all preview items"""
        for item in self.preview_items:
            item['selected'] = False
        self.update_preview_display()
        self.update_selection_count()
    
    def update_selection_count(self):
        """Update the selection counter"""
        selected = sum(1 for item in self.preview_items if item.get('selected', False))
        total = len(self.preview_items)
        self.selection_count_label.configure(text=f"{selected} of {total} items selected")
    

    
    def _analyze_content_worker(self, url):
        """Worker thread to analyze content (video, playlist, channel)"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # For playlists/channels
                'playlistend': 50,  # Limit initial analysis
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Analyze content type and show preview
                self.root.after(0, self._show_content_preview, info)
                
        except Exception as e:
            self.root.after(0, lambda: self.content_type_label.configure(text=f"Error: {str(e)[:50]}"))
    
    def _show_content_preview(self, content_info):
        """Show content preview based on type"""
        self.current_preview_data = content_info
        self.preview_items.clear()
        
        # Clear existing preview content
        for widget in self.preview_scroll.winfo_children():
            widget.destroy()
        
        # Determine content type
        is_playlist = content_info.get('_type') == 'playlist'
        entry_count = len(content_info.get('entries', []))
        
        if is_playlist and entry_count > 1:
            content_type = f"Playlist ({entry_count} videos)"
            self._setup_playlist_preview(content_info)
        elif entry_count > 1:
            content_type = f"Channel/Collection ({entry_count} videos)"
            self._setup_playlist_preview(content_info)
        else:
            content_type = "Single Video"
            self._setup_video_preview(content_info)
        
        # Update UI
        self.content_type_label.configure(text=content_type)
        self.update_selection_count()
    
    def _setup_video_preview(self, video_info):
        """Setup preview for single video"""
        self.preview_items.append({
            'url': video_info.get('webpage_url', video_info.get('url')),
            'title': video_info.get('title', 'Unknown Title'),
            'duration': video_info.get('duration'),
            'uploader': video_info.get('uploader'),
            'selected': True,
            'type': 'video'
        })
        self._create_preview_item_ui(self.preview_items[0], 0)
    
    def _setup_playlist_preview(self, playlist_info):
        """Setup preview for playlist/channel"""
        entries = playlist_info.get('entries', [])
        
        for i, entry in enumerate(entries):
            if entry:  # Sometimes entries can be None
                self.preview_items.append({
                    'url': entry.get('url', ''),
                    'title': entry.get('title', f'Video {i+1}'),
                    'duration': entry.get('duration'),
                    'uploader': entry.get('uploader', playlist_info.get('uploader')),
                    'selected': True,
                    'type': 'video'
                })
                self._create_preview_item_ui(self.preview_items[-1], len(self.preview_items)-1)
    
    def _create_preview_item_ui(self, item, index):
        """Create UI element for preview item"""
        item_frame = ctk.CTkFrame(self.preview_scroll)
        item_frame.pack(fill="x", padx=4, pady=2)
        
        # Checkbox and info
        left_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=8, pady=6)
        
        # Checkbox
        checkbox_var = ctk.BooleanVar(value=item['selected'])
        checkbox = ctk.CTkCheckBox(
            left_frame,
            text="",
            variable=checkbox_var,
            command=lambda idx=index: self._toggle_item_selection(idx, checkbox_var.get())
        )
        checkbox.pack(side="left", padx=(0, 8))
        
        # Title and details
        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        # Title with duration inline
        title_text = item['title']
        if item['duration']:
            try:
                duration = int(float(item['duration']))  # Handle both int and float
                duration_str = f"{duration//60}:{duration%60:02d}"
                title_text += f" ({duration_str})"
            except (ValueError, TypeError):
                # Skip duration if it can't be parsed
                pass
        
        title_label = ctk.CTkLabel(
            info_frame,
            text=title_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        # Only show uploader if available
        if item['uploader']:
            uploader_label = ctk.CTkLabel(
                info_frame,
                text=f"By: {item['uploader']}",
                font=ctk.CTkFont(size=9),
                text_color="gray",
                anchor="w"
            )
            uploader_label.pack(anchor="w")
        
        # Store UI reference
        item['ui_frame'] = item_frame
        item['checkbox_var'] = checkbox_var
    
    def _toggle_item_selection(self, index, selected):
        """Toggle selection state of preview item"""
        if index < len(self.preview_items):
            self.preview_items[index]['selected'] = selected
            self.update_selection_count()
    
    def update_preview_display(self):
        """Update the preview display with current selection states"""
        for item in self.preview_items:
            if 'checkbox_var' in item:
                item['checkbox_var'].set(item['selected'])
    
    def start_download(self, url: str, options: Dict):
        """Start a new download"""
        # Create download item
        download_item = DownloadItem(url)
        self.downloads[download_item.id] = download_item
        
        # Create UI frame
        frame = DownloadProgressFrame(
            self.downloads_scroll,
            download_item,
            self.remove_download
        )
        self.download_frames[download_item.id] = frame
        
        # Start download thread
        threading.Thread(
            target=self._download_worker,
            args=(download_item, options),
            daemon=True
        ).start()
        
        self.update_status()
    
    def _download_worker(self, download_item: DownloadItem, options: Dict):
        """Worker thread for downloading"""
        try:
            # Update status
            download_item.status = "downloading"
            
            # Setup output directory
            output_dir = Path(self.settings["output_dir"])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Progress hook
            def progress_hook(d):
                if d['status'] == 'downloading':
                    # Update progress
                    percent_str = d.get('_percent_str', '0%').replace('%', '')
                    try:
                        download_item.progress = float(percent_str)
                    except:
                        pass
                    
                    download_item.speed = d.get('_speed_str', '')
                    download_item.eta = d.get('_eta_str', '')
                    
                    if d.get('total_bytes'):
                        download_item.file_size = f"{d['total_bytes']//1024//1024}MB"
                    
                    if d.get('filename'):
                        download_item.filename = Path(d['filename']).name
                
                elif d['status'] == 'finished':
                    download_item.status = "completed"
                    download_item.progress = 100.0
                    download_item.end_time = datetime.now()
                    if d.get('filename'):
                        download_item.filename = Path(d['filename']).name
                        download_item.filepath = d['filename']
            
            # Setup yt-dlp options with dynamic output template
            # Configure output template based on organize_in_folders setting
            if self.settings["organize_in_folders"]:
                # Organize into sub-folders by playlist/uploader
                outtmpl = str(output_dir / '%(playlist_title,uploader)s/%(title)s.%(ext)s')
            else:
                # Default flat structure
                outtmpl = str(output_dir / '%(title)s.%(ext)s')
            
            ydl_opts = {
                'outtmpl': outtmpl,
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
            }
            
            # Add metadata saving if enabled
            if self.settings["save_metadata"]:
                ydl_opts['writeinfojson'] = True
            
            # Check if a specific format_id was provided in options
            if 'format_id' in options and options['format_id']:
                # Use the specific format requested
                ydl_opts['format'] = options['format_id']
            else:
                # Determine download type and format preferences
                download_type = options.get('type', 'video')
                force_audio_only = options.get('audio_only', False) or self.settings.get("audio_only", False)
                format_pref = options.get('format_preference', self.settings.get("format_preference", "mp4"))
                quality = options.get('quality', self.settings.get("quality", "best"))
                
                # Update download item title to indicate type
                if download_type == 'metadata' or options.get('metadata_only', False):
                    download_item.title = f"[Metadata] {download_item.title}"
                    # For metadata, we just extract info and save it
                    ydl_opts['skip_download'] = True
                    ydl_opts['writeinfojson'] = True
                    ydl_opts['writesubtitles'] = True
                    ydl_opts['writeautomaticsub'] = True
                    ydl_opts['writethumbnail'] = True
                    ydl_opts['writedescription'] = True
                elif download_type == 'audio' or force_audio_only:
                    download_item.title = f"[Audio] {download_item.title}"
                elif download_type == 'video':
                    download_item.title = f"[Video] {download_item.title}"
                
                if download_type == 'audio' or force_audio_only:
                    # Audio-only downloads
                    if format_pref == "mp4":
                        ydl_opts['format'] = 'ba[ext=m4a]/ba'
                    elif format_pref == "webm":
                        ydl_opts['format'] = 'ba[ext=webm]/ba'
                    else:
                        ydl_opts['format'] = 'ba/b'
                else:
                    # Video downloads with audio
                    if quality == "best":
                        if format_pref == "mp4":
                            # Best quality MP4 with fallback
                            ydl_opts['format'] = 'bv*[ext=mp4][height<=1080]+ba[ext=m4a]/bv*[height<=1080]+ba/b[height<=1080]'
                            ydl_opts['merge_output_format'] = 'mp4'
                        elif format_pref == "webm":
                            # Best quality WebM
                            ydl_opts['format'] = 'bv*[ext=webm]+ba[ext=webm]/bv*+ba'
                            ydl_opts['merge_output_format'] = 'webm'
                        elif format_pref == "mkv":
                            # High quality MKV (for those who need it)
                            ydl_opts['format'] = 'bv*+ba/b'
                            ydl_opts['merge_output_format'] = 'mkv'
                        else:  # "any"
                            # Best available format, prefer MP4
                            ydl_opts['format'] = 'bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/b'
                            ydl_opts['merge_output_format'] = 'mp4'
                    elif quality == "worst":
                        ydl_opts['format'] = 'wv*+wa/w'
                    else:
                        # Specific quality with format preference
                        quality_num = quality.replace('p', '')
                        if format_pref == "mp4":
                            ydl_opts['format'] = f'bv*[height<={quality_num}][ext=mp4]+ba[ext=m4a]/bv*[height<={quality_num}]+ba'
                            ydl_opts['merge_output_format'] = 'mp4'
                        elif format_pref == "webm":
                            ydl_opts['format'] = f'bv*[height<={quality_num}][ext=webm]+ba[ext=webm]/bv*[height<={quality_num}]+ba'
                            ydl_opts['merge_output_format'] = 'webm'
                        elif format_pref == "mkv":
                            ydl_opts['format'] = f'bv*[height<={quality_num}]+ba'
                            ydl_opts['merge_output_format'] = 'mkv'
                        else:  # "any"
                            ydl_opts['format'] = f'bv*[height<={quality_num}]+ba'
                
                # Add subtitles if enabled
                if self.settings.get("include_subtitles", False):
                    ydl_opts['writesubtitles'] = True
                    ydl_opts['subtitleslangs'] = ['en']
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First get info to update title
                info = ydl.extract_info(download_item.url, download=False)
                download_item.title = info.get('title', download_item.title)
                
                # Now download
                ydl.download([download_item.url])
            
            if download_item.status != "completed":
                download_item.status = "completed"
                download_item.progress = 100.0
                download_item.end_time = datetime.now()
                
        except Exception as e:
            download_item.status = "failed"
            download_item.error = str(e)
            download_item.end_time = datetime.now()
            print(f"Download failed: {e}")
    
    def remove_download(self, download_id: str):
        """Remove a download from the list"""
        if download_id in self.downloads:
            del self.downloads[download_id]
        if download_id in self.download_frames:
            del self.download_frames[download_id]
        self.update_status()
    
    def clear_completed(self):
        """Clear all completed downloads"""
        to_remove = []
        for download_id, download_item in self.downloads.items():
            if download_item.status in ["completed", "failed", "cancelled"]:
                to_remove.append(download_id)
        
        for download_id in to_remove:
            if download_id in self.download_frames:
                self.download_frames[download_id].frame.destroy()
            self.remove_download(download_id)
    
    def open_settings(self):
        """Open settings window"""
        SettingsWindow(self)
    
    def update_status(self):
        """Update status bar"""
        active_downloads = sum(1 for d in self.downloads.values() if d.status == "downloading")
        completed_downloads = sum(1 for d in self.downloads.values() if d.status == "completed")
        failed_downloads = sum(1 for d in self.downloads.values() if d.status == "failed")
        
        status_text = f"Active: {active_downloads} | Completed: {completed_downloads} | Failed: {failed_downloads}"
        self.status_label.configure(text=status_text)
    
    def start_update_thread(self):
        """Start background thread to update UI"""
        def update_loop():
            while True:
                try:
                    # Update all download frames
                    for frame in self.download_frames.values():
                        self.root.after(0, frame.update_display)
                    
                    # Update status
                    self.root.after(0, self.update_status)
                    
                    time.sleep(0.5)  # Update every 500ms
                except:
                    break
        
        threading.Thread(target=update_loop, daemon=True).start()
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

class SettingsWindow:
    """Settings configuration window"""
    
    def __init__(self, parent: VideoDownloaderGUI):
        self.parent = parent
        
        # Create window
        self.window = ctk.CTkToplevel(parent.root)
        self.window.title("Settings")
        self.window.geometry("600x600")
        self.window.transient(parent.root)
        self.window.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Settings", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 30))
        
        # Content frame for better organization
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Output directory
        dir_frame = ctk.CTkFrame(content_frame)
        dir_frame.pack(fill="x", padx=20, pady=(20, 15))
        
        dir_label = ctk.CTkLabel(
            dir_frame, 
            text="Download Directory:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        dir_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        dir_input_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.dir_entry = ctk.CTkEntry(
            dir_input_frame,
            placeholder_text="Download directory path",
            height=35
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.dir_entry.insert(0, self.parent.settings["output_dir"])
        
        browse_btn = ctk.CTkButton(
            dir_input_frame,
            text="Browse",
            width=100,
            height=35,
            command=self.browse_directory
        )
        browse_btn.pack(side="right")
        
        # Quality and Format section
        quality_format_frame = ctk.CTkFrame(content_frame)
        quality_format_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Quality selection
        quality_label = ctk.CTkLabel(
            quality_format_frame,
            text="Video Quality:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        quality_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.quality_var = ctk.StringVar(value=self.parent.settings["quality"])
        quality_menu = ctk.CTkOptionMenu(
            quality_format_frame,
            variable=self.quality_var,
            values=["best", "worst", "720p", "480p", "360p"],
            height=35,
            width=200
        )
        quality_menu.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Format preference
        format_label = ctk.CTkLabel(
            quality_format_frame,
            text="Preferred Format:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        format_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.format_var = ctk.StringVar(value=self.parent.settings.get("format_preference", "mp4"))
        format_menu = ctk.CTkOptionMenu(
            quality_format_frame,
            variable=self.format_var,
            values=["mp4", "webm", "mkv", "any"]
        )
        format_menu.pack(anchor="w", padx=15, pady=(0, 5))
        
        # Add helpful description
        format_desc = ctk.CTkLabel(
            quality_format_frame,
            text="MP4: Universal compatibility • WebM: Good compression • MKV: High quality • Any: Best available",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            wraplength=450
        )
        format_desc.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Options section
        options_frame = ctk.CTkFrame(content_frame)
        options_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        options_label = ctk.CTkLabel(
            options_frame,
            text="Download Options:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        options_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        self.audio_only_var = ctk.BooleanVar(value=self.parent.settings["audio_only"])
        audio_only_check = ctk.CTkCheckBox(
            options_frame,
            text="Audio only (extract audio from videos)",
            variable=self.audio_only_var,
            font=ctk.CTkFont(size=12)
        )
        audio_only_check.pack(anchor="w", padx=15, pady=5)
        
        self.subtitles_var = ctk.BooleanVar(value=self.parent.settings["include_subtitles"])
        subtitles_check = ctk.CTkCheckBox(
            options_frame,
            text="Include subtitles when available",
            variable=self.subtitles_var,
            font=ctk.CTkFont(size=12)
        )
        subtitles_check.pack(anchor="w", padx=15, pady=5)
        
        self.organize_folders_var = ctk.BooleanVar(value=self.parent.settings["organize_in_folders"])
        organize_folders_check = ctk.CTkCheckBox(
            options_frame,
            text="Organize playlist/channel downloads into sub-folders",
            variable=self.organize_folders_var,
            font=ctk.CTkFont(size=12)
        )
        organize_folders_check.pack(anchor="w", padx=15, pady=5)
        
        self.save_metadata_var = ctk.BooleanVar(value=self.parent.settings["save_metadata"])
        save_metadata_check = ctk.CTkCheckBox(
            options_frame,
            text="Save video metadata (.info.json file)",
            variable=self.save_metadata_var,
            font=ctk.CTkFont(size=12)
        )
        save_metadata_check.pack(anchor="w", padx=15, pady=(5, 15))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            fg_color="gray",
            height=40,
            width=120
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            command=self.save,
            height=40,
            width=150
        )
        save_btn.pack(side="right")
    
    def browse_directory(self):
        """Browse for download directory"""
        directory = filedialog.askdirectory(
            initialdir=self.parent.settings["output_dir"]
        )
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
    
    def save(self):
        """Save settings"""
        self.parent.settings["output_dir"] = self.dir_entry.get()
        self.parent.settings["quality"] = self.quality_var.get()
        self.parent.settings["format_preference"] = self.format_var.get()
        self.parent.settings["audio_only"] = self.audio_only_var.get()
        self.parent.settings["include_subtitles"] = self.subtitles_var.get()
        self.parent.settings["organize_in_folders"] = self.organize_folders_var.get()
        self.parent.settings["save_metadata"] = self.save_metadata_var.get()
        
        self.parent.save_settings()
        self.window.destroy()
    
    def cancel(self):
        """Cancel settings"""
        self.window.destroy()

if __name__ == "__main__":
    # Create and run application
    app = VideoDownloaderGUI()
    app.run()
