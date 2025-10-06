#!/usr/bin/env pwsh
# Extract frames from YouTube videos and Twitter media
Write-Host "Running Lightning Archive Frame Extraction Tool..." -ForegroundColor Cyan
Write-Host "This will process YouTube videos and Twitter media to extract lightning frames." -ForegroundColor Cyan
Write-Host ""

python -m lightning_archive.frames_extract

Write-Host ""
Write-Host "Process completed. Check the logs in data/workflow_logs/ for details." -ForegroundColor Green
Read-Host "Press ENTER to exit"
