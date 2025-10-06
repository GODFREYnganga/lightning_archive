@echo off
echo ===== Twitter Media Collector =====
echo This script collects media from Twitter JSON data files
echo.

REM Activate Python environment (if using venv/conda)
REM call .\venv\Scripts\activate

REM Run the Twitter collector
python -m lightning_archive.twitter_collector

echo.
echo Completed! Check data/raw/twitter and data/metadata for results.
pause
