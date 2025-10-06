# Direct YouTube Download for Lightning Archive
Write-Host "===== Direct YouTube Download for Lightning Archive =====" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "Using $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Make sure yt-dlp is installed
try {
    $ytdlpVersion = python -c "import subprocess; subprocess.run(['yt-dlp', '--version'])"
}
catch {
    Write-Host "Installing yt-dlp..." -ForegroundColor Yellow
    pip install yt-dlp
}

Write-Host "Running direct YouTube downloader script..." -ForegroundColor Yellow
python download_youtube_direct.py

Write-Host ""
Write-Host "Download completed. Next steps:" -ForegroundColor Green
Write-Host "1. Run frame extraction: python -m lightning_archive --phase extract" -ForegroundColor White
Write-Host "2. Run dataset creation: python -m lightning_archive --phase dataset" -ForegroundColor White
