# All-in-One Twitter Collection Script for Lightning Archive
# This script scrapes Twitter data and processes it in one go

Write-Host "===== Lightning Archive: Twitter Data Collection =====" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will scrape Twitter data and process it to download media"
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

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: No .env file found." -ForegroundColor Yellow
    Write-Host "Creating a template .env file for you to fill in your API keys."
    "RAPIDAPI_KEY=your_key_here" | Out-File -FilePath ".env"
    Write-Host ""
    Write-Host "Please edit the .env file to add your RapidAPI key." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Running full Twitter data collection workflow..." -ForegroundColor Cyan
Write-Host "This will scrape Twitter data and process it to download media."
Write-Host ""

# Run the Twitter collector with workflow option for complete process
python -m lightning_archive.twitter_collector --workflow `
  --search-term "nyc lightning (video OR photo)" `
  --date-range "since:2024-06-25 until:2024-06-28" `
  --max-results 20

Write-Host ""
Write-Host "Twitter collection completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Media files are downloaded to data/raw/twitter" -ForegroundColor Cyan
Write-Host "Metadata is saved in data/metadata/twitter_media_metadata.csv" -ForegroundColor Cyan

# Pause to see the output
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
