# Test the updated api_collectors.py with yt-dlp
Write-Host "===== Testing YouTube Download with yt-dlp =====" -ForegroundColor Green

# Make sure yt-dlp is installed
Write-Host "Installing/Updating yt-dlp..." -ForegroundColor Yellow
pip install yt-dlp

Write-Host "Running test download..." -ForegroundColor Yellow
python test_youtube_download.py

Write-Host "`nTest completed! Check the output above for results." -ForegroundColor Green
pause
