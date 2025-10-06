# Twitter API Scraping Script for Lightning Archive
# This script uses RapidAPI to scrape Twitter data

Write-Host "===== Lightning Archive: Twitter API Scraping =====" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will scrape Twitter data related to the NYC lightning strike event"
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
}

Write-Host "Running Twitter API scraping..." -ForegroundColor Cyan
Write-Host ""

# Run the Twitter scraper directly with --scrape option
python -m lightning_archive.twitter_collector --scrape --search-term "nyc lightning (video OR photo)" --date-range "since:2024-06-25 until:2024-06-28"

Write-Host ""
Write-Host "Twitter API scraping completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Raw JSON data is saved in data/raw/twitter_api_responses" -ForegroundColor Cyan
Write-Host ""
Write-Host "To process the data and download media, run the process_twitter_data.ps1 script" -ForegroundColor Cyan
Write-Host "or use: python -m lightning_archive.twitter_collector --process" -ForegroundColor Cyan

# Pause to see the output
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
