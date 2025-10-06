# Using yt-dlp for YouTube Downloads in Lightning Archive

This guide explains how the Lightning Archive project has been updated to use yt-dlp for more reliable YouTube downloads.

## What is yt-dlp?

yt-dlp is a fork of youtube-dl with additional features and fixes. It's much more reliable than pytube for downloading YouTube videos, especially when dealing with age-restricted content, regional restrictions, or frequently changing YouTube APIs.

## How We've Integrated yt-dlp

The Lightning Archive project has been updated to use yt-dlp in the following components:

1. **api_collectors.py**: The `download_youtube_videos()` function now uses yt-dlp instead of pytube.
2. **download_manager.py**: Updated to always use the yt-dlp version of the downloader.
3. **Direct download scripts**: `download_youtube_direct.py` provides a direct interface to yt-dlp.
4. **All-in-One scripts**: The comprehensive pipeline scripts now include better error handling and fallback to direct methods when module imports fail.

## Using the yt-dlp Integration

### Installing yt-dlp

Before running any download scripts, make sure yt-dlp is installed:

```bash
pip install yt-dlp
```

Or use the provided installation scripts:

```bash
# Windows Command Prompt
install_yt_dlp_now.bat

# PowerShell
.\install_yt_dlp_now.ps1
```

### Running Downloads with yt-dlp

#### Option 1: Using the Module System (Recommended)

```bash
# Windows Command Prompt
download_youtube.bat

# PowerShell
.\download_youtube.ps1
```

This will use the integrated yt-dlp downloader in the Lightning Archive module.

#### Option 2: Direct Download Script

If you encounter any issues with the module system, you can use the direct download script:

```bash
# Windows Command Prompt
direct_youtube_download.bat

# PowerShell
.\direct_youtube_download.ps1
```

#### Option 3: All-in-One Pipeline

To run the complete pipeline with the improved yt-dlp integration:

```bash
# Windows Command Prompt
lightning_archive_all_in_one.bat

# PowerShell
.\lightning_archive_all_in_one.ps1
```

This script includes error handling and will fall back to direct methods if any phase fails.

## Troubleshooting

### Common Issues

1. **yt-dlp not installed**: If you see an error about yt-dlp not being found, run:
   ```bash
   pip install yt-dlp
   ```

2. **Permission errors**: If you encounter permission issues, try running the terminal as administrator.

3. **YouTube API changes**: If downloads start failing, update yt-dlp:
   ```bash
   pip install --upgrade yt-dlp
   ```

4. **Module import errors**: If you see module import errors, use the direct download script instead.

## How yt-dlp Improves the Lightning Archive Project

1. **More reliable downloads**: yt-dlp handles YouTube API changes and restrictions better than pytube.
2. **Better quality selection**: The integration automatically selects the best quality MP4 videos.
3. **Improved error handling**: Better reporting of download failures with detailed error messages.
4. **Fallback mechanisms**: The pipeline now includes fallbacks to direct methods when modules fail.

---

For more information on yt-dlp, visit: https://github.com/yt-dlp/yt-dlp
