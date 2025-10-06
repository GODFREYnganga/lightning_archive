@echo off
REM Extract frames from YouTube videos and Twitter media
echo Running Lightning Archive Frame Extraction Tool...
echo This will process YouTube videos and Twitter media to extract lightning frames.

python -m lightning_archive.frames_extract

echo.
echo Process completed. Check the logs in data/workflow_logs/ for details.
pause
