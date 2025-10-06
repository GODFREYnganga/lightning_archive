@echo off
REM Lightning Archive: Search Only Phase
REM This batch file runs just the search phase without downloading any media files

echo ================================================
echo   LIGHTNING ARCHIVE: SEARCH ONLY PHASE
echo ================================================

REM Define query parameters
set query=lightning strike NYC June 26 2024
set maxResults=20

echo.
echo Running search-only workflow with query: '%query%'
echo This will collect metadata from YouTube and Reddit without downloading any media files

REM Run the search-only phase using the main module
echo.
echo Executing main module...
python -m lightning_archive --phase search_only --query "%query%" --max-results %maxResults%

echo.
echo Process completed!
echo Metadata collected and saved to: data/metadata/dataset_master.csv

echo.
pause
