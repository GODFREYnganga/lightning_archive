@echo off
REM Script to install all dependencies for Lightning Archive

echo Installing Lightning Archive dependencies...

REM Check if pip is available
where pip >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: pip not found. Please ensure Python and pip are installed and in your PATH.
    exit /b 1
)

REM Install main dependencies
echo Installing main dependencies...
pip install -r requirements.txt

REM Install the package in development mode
echo.
echo Installing Lightning Archive in development mode...
pip install -e .

echo.
echo Installation complete!
echo You can now run Lightning Archive using 'python -m lightning_archive'

REM Optional: Install development dependencies if in dev environment
set /p installDev="Do you want to install development dependencies? (y/n) "
if /i "%installDev%"=="y" (
    echo.
    echo Installing development dependencies...
    pip install -r dev-requirements.txt
    echo Development dependencies installed.
)

echo.
echo Dependency installation complete.
pause
