# Twitter Media Collector PowerShell Script

Write-Host "===== Twitter Media Collector =====" -ForegroundColor Cyan
Write-Host "This script collects media from Twitter JSON data files"
Write-Host ""

# Activate Python environment (if using venv/conda)
# & .\venv\Scripts\activate

# Run the Twitter collector
python -m lightning_archive.twitter_collector

Write-Host ""
Write-Host "Completed! Check data/raw/twitter and data/metadata for results." -ForegroundColor Green
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
