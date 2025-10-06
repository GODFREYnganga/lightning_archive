# PowerShell script to run verification and dataset creation
Write-Host "Running verification and dataset creation..." -ForegroundColor Green
python verify_and_create_dataset.py $args
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
