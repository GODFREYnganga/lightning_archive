# Lightning Archive YouTube Download Fix Script
Write-Host "===== Lightning Archive YouTube Download Fix =====" -ForegroundColor Cyan
Write-Host "This script will update the pytube library to fix download issues" -ForegroundColor White
Write-Host ""

# Update pytube first
Write-Host "Updating pytube to the latest version..." -ForegroundColor Yellow
pip install --upgrade pytube

# Find the location of pytube
Write-Host "Finding pytube installation location..." -ForegroundColor Yellow
$pytubeInfo = pip show pytube
$pytubeLocation = ($pytubeInfo | Select-String -Pattern "Location: (.*)").Matches.Groups[1].Value

Write-Host "Found pytube at: $pytubeLocation" -ForegroundColor Green

# Check if the extract.py file exists
$extractPath = Join-Path -Path $pytubeLocation -ChildPath "pytube\extract.py"
if (-not (Test-Path $extractPath)) {
    Write-Host "Error: Could not find extract.py file. Manual fix required." -ForegroundColor Red
    exit
}

# Backup original file
Write-Host "Backing up original extract.py file..." -ForegroundColor Yellow
$backupPath = Join-Path -Path $pytubeLocation -ChildPath "pytube\extract.py.bak"
Copy-Item -Path $extractPath -Destination $backupPath
Write-Host "Backup created at: $backupPath" -ForegroundColor Green

# Apply fixes
Write-Host "Applying fix to extract.py..." -ForegroundColor Yellow
$content = Get-Content -Path $extractPath
$content = $content -replace 'var_regex = re.compile\(''var ([\w$]+) = \{(.*?)\};'', re.DOTALL\)', 'var_regex = re.compile(''var ([\w$]+) = \{(.*?)\}\;'', re.DOTALL)'
$content = $content -replace 'funcName = re.compile\(r''''\[(\''|\"")signature(\''|\"")]\\s*,\\s*([a-zA-Z0-9$]+)\\('', re.DOTALL\)', 'funcName = re.compile(r''''\[(\''|\"")signature(\''|\"")]\\s*,\\s*([a-zA-Z0-9$]+)\\(|\.get\(\''signature\''\"', re.DOTALL)'
$content | Set-Content -Path $extractPath

Write-Host ""
Write-Host "Fix applied! Now try running the download command again:" -ForegroundColor Green
Write-Host "python -m lightning_archive --phase download" -ForegroundColor Cyan
Write-Host ""
Write-Host "If you still have issues, try Solution 3 in the documentation." -ForegroundColor Yellow
