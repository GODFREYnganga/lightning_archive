@echo off
REM Test the updated api_collectors.py with yt-dlp
echo ===== Testing YouTube Download with yt-dlp =====

REM Make sure yt-dlp is installed
echo Installing/Updating yt-dlp...
pip install yt-dlp

echo Running test download...
python test_youtube_download.py

echo.
echo Test completed! Check the output above for results.
pause
