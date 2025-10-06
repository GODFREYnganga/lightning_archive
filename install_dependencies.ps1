#!/usr/bin/env pwsh
# Script to install all dependencies for Lightning Archive

Write-Host "Installing Lightning Archive dependencies..." -ForegroundColor Cyan

# Check if pip is available
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "Error: pip not found. Please ensure Python and pip are installed and in your PATH." -ForegroundColor Red
    exit 1
}

# Install main dependencies
Write-Host "Installing main dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install the package in development mode
Write-Host "`nInstalling Lightning Archive in development mode..." -ForegroundColor Yellow
pip install -e .

Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "You can now run Lightning Archive using 'python -m lightning_archive'" -ForegroundColor Cyan

# Optional: Install development dependencies if in dev environment
$installDev = Read-Host "Do you want to install development dependencies? (y/n)"
if ($installDev -eq "y" -or $installDev -eq "Y") {
    Write-Host "`nInstalling development dependencies..." -ForegroundColor Yellow
    pip install -r dev-requirements.txt
    Write-Host "Development dependencies installed." -ForegroundColor Green
}

Write-Host "`nDependency installation complete." -ForegroundColor Cyan
Read-Host "Press ENTER to exit"
