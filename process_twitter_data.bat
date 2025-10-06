@echo off
REM Twitter Data Processing Script for Lightning Archive
REM This script processes JSON files from Twitter API and downloads media

echo ===== Lightning Archive: Twitter Data Processing =====
echo.
echo This script will process Twitter data and download media
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    exit /b 1
)

echo.
echo 1. Process all Twitter data files
echo 2. Process a specific Twitter data file
echo.

set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Processing all Twitter data files...
    python -m lightning_archive.twitter_collector --process
) else if "%choice%"=="2" (
    echo.
    set /p filename="Enter the filename to process (from data/raw/twitter_api_responses): "
    echo.
    echo Processing %filename%...
    python -m lightning_archive.twitter_collector --process "data/raw/twitter_api_responses/%filename%"
) else (
    echo.
    echo Invalid choice. Processing all Twitter data files...
    python -m lightning_archive.twitter_collector --process
)

echo.
echo Twitter data processing completed!
echo.
echo Media files are downloaded to data/raw/twitter
echo Metadata is saved in data/metadata/twitter_media_metadata.csv

REM Pause to see the output
pause
