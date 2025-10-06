# Download and Extract with Organized Folders
Write-Host "===== LIGHTNING ARCHIVE: DOWNLOAD AND EXTRACT PIPELINE =====" -ForegroundColor Cyan
Write-Host "This script will download media and extract frames into organized folders."

# Step 1: Install yt-dlp (for reliable YouTube downloads)
Write-Host "`n[1/3] Installing yt-dlp..." -ForegroundColor Yellow
pip install --upgrade yt-dlp

# Step 2: Download YouTube videos
Write-Host "`n[2/3] Downloading YouTube videos..." -ForegroundColor Yellow
python -m lightning_archive --phase download

# Step 3: Extract frames with organized folders
Write-Host "`n[3/3] Extracting frames into organized folders..." -ForegroundColor Yellow
python extract_frames_organized.py

Write-Host "`nPipeline completed!" -ForegroundColor Green
Write-Host "Media files have been downloaded to:" -ForegroundColor Yellow
Write-Host "  - YouTube: data/raw/youtube/"
Write-Host "  - Twitter: data/raw/twitter/"
Write-Host "`nFrames have been extracted to:" -ForegroundColor Yellow
Write-Host "  - YouTube frames: data/screens/youtube/(video_id)/"
Write-Host "  - Twitter frames: data/screens/twitter/(media_id)/"

Write-Host "`nEach media file has its own folder containing the extracted frames." -ForegroundColor Cyan
pause
