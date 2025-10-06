@echo off
echo ===== Direct YouTube Download with yt-dlp =====

REM Check if the dataset_master.csv exists
if not exist "data\metadata\dataset_master.csv" (
    echo Error: Metadata file not found.
    echo Please run the collection phase first with: python -m lightning_archive --phase collect
    exit /b 1
)

REM Create output directory
mkdir "data\raw\youtube" 2>nul

echo Reading YouTube URLs from metadata...
REM Use Python to extract YouTube URLs and IDs
python -c "import pandas as pd; df = pd.read_csv('data/metadata/dataset_master.csv'); youtube_df = df[df['platform'] == 'YouTube']; print('\n'.join([f'{row[\"id\"]}|{row[\"url\"]}' for _, row in youtube_df.iterrows()]))" > youtube_urls.txt

echo Found %ERRORLEVEL% YouTube videos to download.

REM Download each YouTube video directly with yt-dlp
for /f "tokens=1,2 delims=|" %%a in (youtube_urls.txt) do (
    set "id=%%a"
    set "url=%%b"
    echo Downloading %%b (ID: %%a)...
    
    REM Check if the file already exists
    if exist "data\raw\youtube\%%a.mp4" (
        echo Video already exists, skipping...
    ) else (
        yt-dlp "%%b" -o "data\raw\youtube\%%a.mp4" -f "best[ext=mp4]" --no-progress --no-warnings
    )
)

del youtube_urls.txt

echo Download complete!
echo You can now proceed with frame extraction using: python -m lightning_archive --phase extract
