@echo off
echo ===== Installing yt-dlp for Lightning Archive =====

REM Check if yt-dlp is already installed
where yt-dlp >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo yt-dlp is already installed.
    yt-dlp --version
    goto :run_download
)

echo Installing yt-dlp with pip...
pip install yt-dlp

REM Check if installation succeeded
where yt-dlp >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo yt-dlp installed successfully.
    yt-dlp --version
) ELSE (
    echo Failed to install yt-dlp. Please install it manually:
    echo pip install yt-dlp
    exit /b 1
)

:run_download
echo.
echo Now running the YouTube download phase...
python -m lightning_archive --phase download
