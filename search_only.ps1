# Lightning Archive: Search Only Phase
# This PowerShell script runs just the search phase without downloading any media files

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  LIGHTNING ARCHIVE: SEARCH ONLY PHASE" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Define query parameters
$query = "lightning strike NYC June 26 2024"
$maxResults = 20

Write-Host "`nRunning search-only workflow with query: '$query'" -ForegroundColor Yellow
Write-Host "This will collect metadata from YouTube and Reddit without downloading any media files"

# Run the search-only phase using the main module
Write-Host "`nExecuting main module..." -ForegroundColor Green
python -m lightning_archive --phase search_only --query $query --max-results $maxResults

Write-Host "`nProcess completed!" -ForegroundColor Cyan
Write-Host "Metadata collected and saved to: data/metadata/dataset_master.csv" -ForegroundColor Yellow

Write-Host "`nPress Enter to exit..." -ForegroundColor Gray
Read-Host
