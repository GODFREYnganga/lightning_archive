# Twitter Data Processing Script for Lightning Archive
# This script processes JSON files from Twitter API and downloads media

Write-Host "===== Lightning Archive: Twitter Data Processing =====" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will process Twitter data and download media"
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Using $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again."
    exit 1
}

Write-Host ""
Write-Host "1. Process all Twitter data files" -ForegroundColor Cyan
Write-Host "2. Process a specific Twitter data file" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Enter your choice (1 or 2)"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "Processing all Twitter data files..." -ForegroundColor Cyan
    python -m lightning_archive.twitter_collector --process
}
elseif ($choice -eq "2") {
    Write-Host ""
    $filename = Read-Host "Enter the filename to process (from data/raw/twitter_api_responses)"
    Write-Host ""
    Write-Host "Processing $filename..." -ForegroundColor Cyan
    python -m lightning_archive.twitter_collector --process "data/raw/twitter_api_responses/$filename"
}
else {
    Write-Host ""
    Write-Host "Invalid choice. Processing all Twitter data files..." -ForegroundColor Yellow
    python -m lightning_archive.twitter_collector --process
}

Write-Host ""
Write-Host "Twitter data processing completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Media files are downloaded to data/raw/twitter" -ForegroundColor Cyan
Write-Host "Metadata is saved in data/metadata/twitter_media_metadata.csv" -ForegroundColor Cyan

# Pause to see the output
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
