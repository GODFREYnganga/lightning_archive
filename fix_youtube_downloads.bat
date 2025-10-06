@echo off
echo ===== Lightning Archive YouTube Download Fix =====
echo This script will update the pytube library to fix download issues

REM Update pytube first
echo Updating pytube to the latest version...
pip install --upgrade pytube

REM Find the location of pytube
echo Finding pytube installation location...
for /f "tokens=*" %%a in ('pip show pytube ^| findstr "Location"') do set "PYTUBE_LOCATION=%%a"
set "PYTUBE_LOCATION=%PYTUBE_LOCATION:Location: =%"

echo Found pytube at: %PYTUBE_LOCATION%

REM Check if the extract.py file exists
if not exist "%PYTUBE_LOCATION%\pytube\extract.py" (
    echo Error: Could not find extract.py file. Manual fix required.
    goto :eof
)

echo Backing up original extract.py file...
copy "%PYTUBE_LOCATION%\pytube\extract.py" "%PYTUBE_LOCATION%\pytube\extract.py.bak"
echo Backup created at: %PYTUBE_LOCATION%\pytube\extract.py.bak

echo Applying fix to extract.py...
powershell -Command "(Get-Content '%PYTUBE_LOCATION%\pytube\extract.py') -replace 'var_regex = re.compile\(''var ([\w$]+) = \{(.*?)\};'', re.DOTALL\)', 'var_regex = re.compile(''var ([\w$]+) = \{(.*?)\}\;'', re.DOTALL)' | Set-Content '%PYTUBE_LOCATION%\pytube\extract.py'"
powershell -Command "(Get-Content '%PYTUBE_LOCATION%\pytube\extract.py') -replace 'funcName = re.compile\(r''''\[(\''|\"")signature(\''|\"")]\\s*,\\s*([a-zA-Z0-9$]+)\\('', re.DOTALL\)', 'funcName = re.compile(r''''\[(\''|\"")signature(\''|\"")]\\s*,\\s*([a-zA-Z0-9$]+)\\(|\.get\(\''signature\''\"', re.DOTALL)' | Set-Content '%PYTUBE_LOCATION%\pytube\extract.py'"

echo Fix applied! Now try running the download command again:
echo python -m lightning_archive --phase download
echo.
echo If you still have issues, try Solution 3 in the documentation.
