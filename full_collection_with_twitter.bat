@echo off
REM Full Collection Workflow with Twitter Integration
REM This script runs the complete Lightning Archive collection workflow including Twitter data

echo ===== Lightning Archive: Full Collection Workflow =====
echo.
echo This script will collect data from YouTube, Reddit, and Twitter for the NYC lightning strike event
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    exit /b 1
)

REM Check for the .env file
if not exist .env (
    echo WARNING: No .env file found
    echo Creating a template .env file for you to fill in your API keys
    echo.
    echo YOUTUBE_API_KEY=your_youtube_api_key> .env
    echo REDDIT_CLIENT_ID=your_reddit_client_id>> .env
    echo REDDIT_CLIENT_SECRET=your_reddit_client_secret>> .env
    echo REDDIT_USER_AGENT=your_reddit_user_agent>> .env
    echo RAPIDAPI_KEY=your_rapidapi_key>> .env
    echo.
    echo Please edit the .env file to add your API keys.
    echo.
    pause
    exit /b 1
)

echo Running full collection workflow with Twitter integration...
echo.

REM Run the full collection workflow with Twitter integration
python -c "from lightning_archive.api_collectors import full_collection_workflow; full_collection_workflow(max_youtube_results=20, max_reddit_results=10, include_twitter=True, max_twitter_results=15)"

echo.
echo Full collection workflow completed!
echo.
echo Results can be found in:
echo - data/metadata/dataset_master.csv
echo - data/raw/youtube/
echo - data/raw/twitter/
echo - data/screens/youtube/

REM Pause to see the output
pause
