@echo off
REM All-in-One Twitter Collection Script for Lightning Archive
REM This script scrapes Twitter data and processes it in one go

echo ===== Lightning Archive: Twitter Data Collection =====
echo.
echo This script will scrape Twitter data and process it to download media
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo WARNING: No .env file found. 
    echo Creating a template .env file for you to fill in your API keys.
    echo RAPIDAPI_KEY=your_key_here> .env
    echo.
    echo Please edit the .env file to add your RapidAPI key.
    echo.
    pause
    exit /b 1
)

echo Running full Twitter data collection workflow...
echo This will scrape Twitter data and process it to download media.
echo.

REM Run the Twitter collector with workflow option for complete process
python -m lightning_archive.twitter_collector --workflow ^
  --search-term "nyc lightning (video OR photo)" ^
  --date-range "since:2024-06-25 until:2024-06-28" ^
  --max-results 20

echo.
echo Twitter collection completed!
echo.
echo Media files are downloaded to data/raw/twitter
echo Metadata is saved in data/metadata/twitter_media_metadata.csv

REM Pause to see the output
pause
