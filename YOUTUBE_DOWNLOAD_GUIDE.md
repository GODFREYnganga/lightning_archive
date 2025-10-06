# Using yt-dlp for YouTube Downloads

This guide explains how to use yt-dlp instead of pytube for more reliable YouTube video downloads in the Lightning Archive project.

## What is yt-dlp?

yt-dlp is a fork of youtube-dl that is actively maintained and works reliably with YouTube. It handles YouTube's changing API better than pytube, resulting in fewer download errors.

## Setup Instructions

### Option 1: Using the Install Scripts

1. Run the installation script:

   ```bash
   # PowerShell
   .\install_yt_dlp.ps1

   # or Command Prompt
   install_yt_dlp.bat
   ```

2. This script will:
   - Install yt-dlp via pip
   - Set up the download manager to use yt-dlp

3. After installation, run the download phase:
   ```bash
   python -m lightning_archive --phase download
   ```

### Option 2: Manual Installation

1. Install yt-dlp manually:
   ```bash
   pip install yt-dlp
   ```

2. The download_manager.py file is already set up to use yt-dlp if available, falling back to pytube if not.

## Download YouTube Videos Only

To download only YouTube videos without running the full pipeline:

```bash
# PowerShell
.\download_youtube.ps1

# or Command Prompt
download_youtube.bat
```

## Troubleshooting

If you encounter any issues:

1. Make sure yt-dlp is installed:
   ```bash
   pip show yt-dlp
   ```

2. Try running yt-dlp directly from the command line:
   ```bash
   yt-dlp --version
   yt-dlp -F "https://www.youtube.com/watch?v=EXAMPLE"
   ```

3. Check the downloaded videos in the `data/raw/youtube/` directory.

## Why Use yt-dlp Instead of pytube?

- yt-dlp is more actively maintained
- It handles YouTube's API changes faster
- More reliable download capability
- Supports more video formats and quality options

If you're still experiencing issues with downloads, please check for updates to the Lightning Archive project or report the issue in the project repository.
