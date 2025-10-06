@echo off
REM Download and Extract with Organized Folders
echo ===== LIGHTNING ARCHIVE: DOWNLOAD AND EXTRACT PIPELINE =====
echo This script will download media and extract frames into organized folders.

REM Step 1: Install yt-dlp (for reliable YouTube downloads)
echo.
echo [1/3] Installing yt-dlp...
pip install --upgrade yt-dlp

REM Step 2: Download YouTube videos
echo.
echo [2/3] Downloading YouTube videos...
python -m lightning_archive --phase download

REM Step 3: Extract frames with organized folders
echo.
echo [3/3] Extracting frames into organized folders...
python extract_frames_organized.py

echo.
echo Pipeline completed!
echo Media files have been downloaded to:
echo   - YouTube: data/raw/youtube/
echo   - Twitter: data/raw/twitter/
echo.
echo Frames have been extracted to:
echo   - YouTube frames: data/screens/youtube/(video_id)/
echo   - Twitter frames: data/screens/twitter/(media_id)/
echo.
echo Each media file has its own folder containing the extracted frames.
pause
