@echo off
REM Enhanced search script for Lightning Archive
REM This script runs the data collection with improved search queries

echo ==============================================
echo Lightning Archive - Enhanced Search Collection
echo ==============================================
echo.
echo This script will run the Lightning Archive data collection
echo with enhanced search queries to get more and better results
echo about the NYC lightning event on June 26, 2024.
echo.
echo Press any key to start the collection...
pause

REM Run the full pipeline with enhanced search queries
python -m lightning_archive --query "lightning strike NYC Empire State Building June 26" --max-results 50 --phase collect

echo.
echo Collection completed! Check the data/metadata folder for results.
echo.
echo Press any key to download the media...
pause

REM Download the collected media
python -m lightning_archive --phase download

echo.
echo Media download completed! Press any key to extract frames...
pause

REM Extract frames from the downloaded media
python -m lightning_archive --phase extract

echo.
echo Frame extraction completed! Press any key to create the dataset...
pause

REM Create the final dataset
python -m lightning_archive --phase dataset

echo.
echo Lightning Archive processing completed!
echo The dataset is now ready for COLMAP 3D reconstruction.
echo.
pause
