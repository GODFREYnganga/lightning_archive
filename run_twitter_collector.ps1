# Twitter Media Collection Script for Lightning Archive
# This script runs the Twitter collector with RapidAPI integration

Write-Host "===== Lightning Archive: Twitter Media Collection =====" -ForegroundColor Cyan
Write-Host
Write-Host "This script will collect Twitter media related to the NYC lightning strike event" -ForegroundColor White
Write-Host

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "Using $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again."
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: No .env file found." -ForegroundColor Yellow
    Write-Host "Creating a template .env file for you to fill in your API keys."
    Set-Content -Path ".env" -Value "RAPIDAPI_KEY=your_key_here"
    Write-Host
    Write-Host "Please edit the .env file to add your RapidAPI key." -ForegroundColor Yellow
    Write-Host
}

Write-Host "Running Twitter media collection..." -ForegroundColor Cyan
Write-Host

# Run the Twitter collector with options for full workflow
python -m lightning_archive.twitter_collector --query "lightning strike NYC June 26 2024" --date-range "since:2024-06-25 until:2024-06-28" --max-results 20

Write-Host
Write-Host "Twitter collection completed!" -ForegroundColor Green
Write-Host
Write-Host "Results can be found in the data/raw/twitter folder" -ForegroundColor White
Write-Host "Metadata is saved in data/metadata" -ForegroundColor White

# Pause to see the output
Write-Host
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
