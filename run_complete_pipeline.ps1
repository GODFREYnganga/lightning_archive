Write-Host "===== LIGHTNING ARCHIVE COMPLETE PIPELINE =====" -ForegroundColor Cyan

Write-Host "1. Running search and collection phase..." -ForegroundColor Yellow
python -m lightning_archive --phase collect

Write-Host "Running Twitter collection (if you have Twitter API keys)..." -ForegroundColor Yellow
.\run_twitter_collector.ps1

Write-Host "2. Running download phase..." -ForegroundColor Yellow
python -m lightning_archive --phase download

Write-Host "3. Running frame extraction phase..." -ForegroundColor Yellow
python -m lightning_archive --phase extract

Write-Host "4. Running dataset creation phase..." -ForegroundColor Yellow
python -m lightning_archive --phase dataset

Write-Host "Complete pipeline execution finished!" -ForegroundColor Green
