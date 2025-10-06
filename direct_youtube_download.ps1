# Direct YouTube Download with yt-dlp
Write-Host "===== Direct YouTube Download with yt-dlp =====" -ForegroundColor Cyan

# Check if the dataset_master.csv exists
if (-not (Test-Path "data\metadata\dataset_master.csv")) {
    Write-Host "Error: Metadata file not found." -ForegroundColor Red
    Write-Host "Please run the collection phase first with: python -m lightning_archive --phase collect" -ForegroundColor Yellow
    exit 1
}

# Create output directory
New-Item -ItemType Directory -Path "data\raw\youtube" -Force | Out-Null

Write-Host "Reading YouTube URLs from metadata..." -ForegroundColor Yellow

# Get YouTube videos from metadata
$datasetCsv = Import-Csv "data\metadata\dataset_master.csv"
$youtubeVideos = $datasetCsv | Where-Object { $_.platform -eq "YouTube" }

Write-Host "Found $($youtubeVideos.Count) YouTube videos to download." -ForegroundColor Green

# Download each YouTube video
foreach ($video in $youtubeVideos) {
    $id = $video.id
    $url = $video.url
    $outputPath = "data\raw\youtube\$id.mp4"
    
    Write-Host "Downloading $url (ID: $id)..." -ForegroundColor Yellow
    
    # Check if the file already exists
    if (Test-Path $outputPath) {
        Write-Host "  Video already exists, skipping..." -ForegroundColor Gray
    } else {
        # Download with yt-dlp
        yt-dlp $url -o $outputPath -f "best[ext=mp4]" --no-progress --no-warnings
    }
}

Write-Host "Download complete!" -ForegroundColor Green
Write-Host "You can now proceed with frame extraction using: python -m lightning_archive --phase extract" -ForegroundColor Cyan
