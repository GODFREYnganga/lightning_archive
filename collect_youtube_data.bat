@echo off
echo ===================================
echo Lightning Archive Collection Tool
echo YouTube and Reddit Data Collection
echo ===================================

echo.
echo Setting up the environment...

:: Ensure Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not found in your PATH.
    echo Please install Python and try again.
    exit /b 1
)

:: Activate virtual environment if it exists, otherwise use system Python
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Install required packages if needed
echo Checking dependencies...
pip install -r requirements.txt --quiet

echo.
echo Starting the collection process...
echo This will:
echo  1. Search YouTube and Reddit for NYC lightning videos (June 26, 2024)
echo  2. Download YouTube videos
echo  3. Extract frames showing lightning strikes
echo.

:: Run the full collection workflow
python -c "from lightning_archive.api_collectors import full_collection_workflow; full_collection_workflow(max_youtube_results=20, max_reddit_results=10)"

echo.
echo ===================================
echo Collection process complete!
echo Results saved to:
echo  - data/metadata/dataset_master.csv
echo  - data/raw/youtube/
echo  - data/screens/youtube/
echo ===================================

pause
