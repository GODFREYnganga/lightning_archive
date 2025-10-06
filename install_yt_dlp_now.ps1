# Install and use yt-dlp for Lightning Archive
Write-Host "===== Installing yt-dlp for Lightning Archive =====" -ForegroundColor Cyan

# Check if yt-dlp is already installed
$ytdlpInstalled = $null
try {
    $ytdlpInstalled = Get-Command yt-dlp -ErrorAction Stop
    Write-Host "yt-dlp is already installed." -ForegroundColor Green
    yt-dlp --version
}
catch {
    Write-Host "Installing yt-dlp with pip..." -ForegroundColor Yellow
    pip install yt-dlp

    # Check if installation succeeded
    try {
        $ytdlpInstalled = Get-Command yt-dlp -ErrorAction Stop
        Write-Host "yt-dlp installed successfully." -ForegroundColor Green
        yt-dlp --version
    }
    catch {
        Write-Host "Failed to install yt-dlp. Please install it manually:" -ForegroundColor Red
        Write-Host "pip install yt-dlp" -ForegroundColor White
        exit 1
    }
}

Write-Host ""
Write-Host "Now running the YouTube download phase..." -ForegroundColor Yellow
python -m lightning_archive --phase download
