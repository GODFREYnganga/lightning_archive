@echo off
echo ===== Direct YouTube Download for Lightning Archive =====

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

REM Make sure yt-dlp is installed
python -c "import subprocess; subprocess.run(['yt-dlp', '--version'])" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing yt-dlp...
    pip install yt-dlp
)

echo Running direct YouTube downloader script...
python download_youtube_direct.py

echo.
echo Download completed. Next steps:
echo 1. Run frame extraction: python -m lightning_archive --phase extract
echo 2. Run dataset creation: python -m lightning_archive --phase dataset
