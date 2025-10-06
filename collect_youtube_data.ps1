# Lightning Archive Collection Tool
# YouTube and Reddit Data Collection

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Lightning Archive Collection Tool" -ForegroundColor Cyan
Write-Host "YouTube and Reddit Data Collection" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Setting up the environment..." -ForegroundColor Yellow

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is not found in your PATH." -ForegroundColor Red
    Write-Host "Please install Python and try again." -ForegroundColor Red
    exit 1
}

# Activate virtual environment if it exists, otherwise use system Python
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Install required packages if needed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "Starting the collection process..." -ForegroundColor Green
Write-Host "This will:" -ForegroundColor Yellow
Write-Host " 1. Search YouTube and Reddit for NYC lightning videos (June 26, 2024)" -ForegroundColor Yellow
Write-Host " 2. Download YouTube videos" -ForegroundColor Yellow
Write-Host " 3. Extract frames showing lightning strikes" -ForegroundColor Yellow
Write-Host ""

# Run the full collection workflow
python -c "from lightning_archive.api_collectors import full_collection_workflow; full_collection_workflow(max_youtube_results=20, max_reddit_results=10)"

Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Collection process complete!" -ForegroundColor Green
Write-Host "Results saved to:" -ForegroundColor Yellow
Write-Host " - data/metadata/dataset_master.csv" -ForegroundColor Yellow
Write-Host " - data/raw/youtube/" -ForegroundColor Yellow
Write-Host " - data/screens/youtube/" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Cyan

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
