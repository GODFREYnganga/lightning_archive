@echo off
REM Twitter API Scraping Script for Lightning Archive
REM This script uses RapidAPI to scrape Twitter data

echo ===== Lightning Archive: Twitter API Scraping =====
echo.
echo This script will scrape Twitter data related to the NYC lightning strike event
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
)

echo Running Twitter API scraping...
echo.

REM Run the Twitter scraper directly with --scrape option
python -m lightning_archive.twitter_collector --scrape --search-term "nyc lightning (video OR photo)" --date-range "since:2024-06-25 until:2024-06-28"

echo.
echo Twitter API scraping completed!
echo.
echo Raw JSON data is saved in data/raw/twitter_api_responses
echo.
echo To process the data and download media, run the process_twitter_data.bat script
echo or use: python -m lightning_archive.twitter_collector --process

REM Pause to see the output
pause
