@echo off
REM Twitter Media Collection Script for Lightning Archive
REM This script runs the Twitter collector with RapidAPI integration

echo ===== Lightning Archive: Twitter Media Collection =====
echo.
echo This script will collect Twitter media related to the NYC lightning strike event
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

echo Running Twitter media collection...
echo.

REM Run the Twitter collector with options for full workflow
python -m lightning_archive.twitter_collector --query "lightning strike NYC June 26 2024" --date-range "since:2024-06-25 until:2024-06-28" --max-results 20

echo.
echo Twitter collection completed!
echo.
echo Results can be found in the data/raw/twitter folder
echo Metadata is saved in data/metadata

REM Pause to see the output
pause
