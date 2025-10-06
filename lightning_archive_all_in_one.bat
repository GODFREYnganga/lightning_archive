@echo off
REM Lightning Archive: Complete Pipeline with yt-dlp Integration
REM This batch file handles the complete workflow with improved YouTube downloads using yt-dlp

echo ================================================
echo   LIGHTNING ARCHIVE: COMPLETE PIPELINE RUNNER
echo ================================================

REM Define query parameters
set query=lightning strike NYC June 26 2024
set maxResults=20

REM Set up error tracking
set errorCount=0
set warningCount=0

REM Define directories
set dataDir=data
set metadataDir=%dataDir%\metadata
set masterCSV=%metadataDir%\dataset_master.csv

REM Step 1: Check and install dependencies
echo.
echo [1/5] CHECKING DEPENDENCIES...
echo Installing/updating yt-dlp...
pip install --upgrade yt-dlp

echo Installing core dependencies...
pip install -e .
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Some dependencies may be missing. Continuing anyway.
    set /a warningCount+=1
)

REM Step 2: Search and collect metadata
echo.
echo [2/5] RUNNING SEARCH AND COLLECTION PHASE...
python -m lightning_archive --phase search_only --query "%query%" --max-results %maxResults%
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Search phase completed with issues. Continuing anyway.
    set /a warningCount+=1
)

REM Check if metadata file was created
if not exist "%masterCSV%" (
    echo Warning: No metadata file created. Some phases may not work properly.
    set /a warningCount+=1
)

REM Step 3: Download media using yt-dlp
echo.
echo [3/5] DOWNLOADING MEDIA WITH YT-DLP...
if exist "%masterCSV%" (
    python -m lightning_archive --phase download
    if %ERRORLEVEL% NEQ 0 (
        echo Warning: Some downloads may have failed. Trying direct download method...
        set /a warningCount+=1
        python download_youtube_direct.py
    )
) else (
    echo Error: Cannot download without metadata file.
    set /a errorCount+=1
)

REM Step 4: Extract frames from videos
echo.
echo [4/5] EXTRACTING FRAMES...
python -m lightning_archive --phase extract
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Frame extraction may have issues. Trying direct extraction method...
    set /a warningCount+=1
    echo Attempting organized frame extraction as fallback...
    python extract_frames_organized.py
    if %ERRORLEVEL% NEQ 0 (
        echo Attempting simple frame extraction as last resort...
        python extract_frames_direct.py
    )
)

REM Step 5: Create dataset for COLMAP
echo.
echo [5/5] CREATING DATASET...
python -m lightning_archive --phase dataset
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Dataset creation completed with issues.
    set /a warningCount+=1
)

REM Final summary
echo.
echo ===== PIPELINE EXECUTION SUMMARY =====

if %errorCount% EQU 0 if %warningCount% EQU 0 (
    echo ✅ All phases completed successfully!
) else if %errorCount% EQU 0 (
    echo ⚠️ Pipeline completed with %warningCount% warnings.
) else (
    echo ❌ Pipeline completed with %errorCount% errors and %warningCount% warnings.
)

echo.
echo Output locations:
echo  - Metadata: data/metadata/dataset_master.csv
echo  - Raw media: data/raw/youtube/ and data/raw/twitter/
echo  - Extracted frames: data/screens/youtube/[video_id]/ and data/screens/twitter/[media_id]/
echo  - Final COLMAP dataset: data/stills/colmap/
echo  - Logs: data/workflow_logs/

echo.
echo Press any key to exit...
pause > nul
