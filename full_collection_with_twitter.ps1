# Full Collection Workflow with Twitter Integration
# This script runs the complete Lightning Archive collection workflow including Twitter data

Write-Host "===== Lightning Archive: Full Collection Workflow =====" -ForegroundColor Cyan
Write-Host
Write-Host "This script will collect data from YouTube, Reddit, and Twitter for the NYC lightning strike event" -ForegroundColor White
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

# Check for the .env file
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: No .env file found" -ForegroundColor Yellow
    Write-Host "Creating a template .env file for you to fill in your API keys" -ForegroundColor Yellow
    Write-Host
    
    @"
YOUTUBE_API_KEY=your_youtube_api_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_reddit_user_agent
RAPIDAPI_KEY=your_rapidapi_key
"@ | Out-File -FilePath ".env" -Encoding utf8
    
    Write-Host "Please edit the .env file to add your API keys." -ForegroundColor Yellow
    Write-Host
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "Running full collection workflow with Twitter integration..." -ForegroundColor Cyan
Write-Host

# Run the full collection workflow with Twitter integration
python -c "from lightning_archive.api_collectors import full_collection_workflow; full_collection_workflow(max_youtube_results=20, max_reddit_results=10, include_twitter=True, max_twitter_results=15)"

Write-Host
Write-Host "Full collection workflow completed!" -ForegroundColor Green
Write-Host
Write-Host "Results can be found in:" -ForegroundColor White
Write-Host "- data/metadata/dataset_master.csv" -ForegroundColor White
Write-Host "- data/raw/youtube/" -ForegroundColor White
Write-Host "- data/raw/twitter/" -ForegroundColor White
Write-Host "- data/screens/youtube/" -ForegroundColor White

# Pause to see the output
Write-Host
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
