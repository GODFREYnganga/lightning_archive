# Lightning Archive: Complete Pipeline with yt-dlp Integration and Frame Verification
# This script handles the complete workflow with improved YouTube downloads using yt-dlp
# and verifies frame collection for COLMAP reconstruction

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  LIGHTNING ARCHIVE: COMPLETE PIPELINE RUNNER" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Define query parameters
$query = "lightning strike NYC June 26 2024"
$maxResults = 20

# Set up error tracking
$errorCount = 0
$warningCount = 0

# Define directories
$dataDir = "data"
$metadataDir = Join-Path -Path $dataDir -ChildPath "metadata"
$masterCSV = Join-Path -Path $metadataDir -ChildPath "dataset_master.csv"

# Step 1: Check and install dependencies
Write-Host "`n[1/5] CHECKING DEPENDENCIES..." -ForegroundColor Yellow
try {
    # Make sure yt-dlp is installed
    Write-Host "Installing/updating yt-dlp..." -ForegroundColor Green
    pip install --upgrade yt-dlp
    
    # Check other dependencies
    Write-Host "Installing core dependencies..." -ForegroundColor Green
    pip install -e .
    if (-not $?) {
        Write-Host "Warning: Some dependencies may be missing. Continuing anyway." -ForegroundColor Yellow
        $warningCount++
    }
} catch {
    Write-Host "Error installing dependencies: $_" -ForegroundColor Red
    $errorCount++
}

# Step 2: Search and collect metadata
Write-Host "`n[2/5] RUNNING SEARCH AND COLLECTION PHASE..." -ForegroundColor Yellow
try {
    # Run the search_only phase to collect metadata
    python -m lightning_archive --phase search_only --query $query --max-results $maxResults
    if (-not $?) {
        Write-Host "Warning: Search phase completed with issues. Continuing anyway." -ForegroundColor Yellow
        $warningCount++
    }
    
    # Check if metadata file was created
    if (-not (Test-Path $masterCSV)) {
        Write-Host "Warning: No metadata file created. Some phases may not work properly." -ForegroundColor Yellow
        $warningCount++
    }
} catch {
    Write-Host "Error in search phase: $_" -ForegroundColor Red
    $errorCount++
}

# Step 3: Download media using yt-dlp
Write-Host "`n[3/5] DOWNLOADING MEDIA WITH YT-DLP..." -ForegroundColor Yellow
try {
    # Try to run the download phase
    if (Test-Path $masterCSV) {
        python -m lightning_archive --phase download
        if (-not $?) {
            Write-Host "Warning: Some downloads may have failed. Trying direct download method..." -ForegroundColor Yellow
            $warningCount++
            
            # Try the direct method as fallback
            python download_youtube_direct.py
        }
    } else {
        Write-Host "Error: Cannot download without metadata file." -ForegroundColor Red
        $errorCount++
    }
} catch {
    Write-Host "Error in download phase: $_" -ForegroundColor Red
    Write-Host "Attempting direct download as fallback..." -ForegroundColor Yellow
    try {
        python download_youtube_direct.py
    } catch {
        Write-Host "Error in direct download: $_" -ForegroundColor Red
        $errorCount++
    }
}

# Step 4: Extract frames from videos
Write-Host "`n[4/5] EXTRACTING FRAMES..." -ForegroundColor Yellow
try {
    # Try to run the extract phase
    python -m lightning_archive --phase extract
    if (-not $?) {
        Write-Host "Warning: Frame extraction may have issues. Trying direct extraction method..." -ForegroundColor Yellow
        $warningCount++
        
        # Try the direct method as fallback
        python extract_frames_direct.py
    }
} catch {
    Write-Host "Error in frame extraction: $_" -ForegroundColor Red
    Write-Host "Attempting organized frame extraction as fallback..." -ForegroundColor Yellow
    try {
        python extract_frames_organized.py
    } catch {
        Write-Host "Error in organized frame extraction: $_" -ForegroundColor Red
        
        # Try direct extraction as a last resort
        Write-Host "Attempting simple frame extraction as last resort..." -ForegroundColor Yellow
        try {
            python extract_frames_direct.py
        } catch {
            Write-Host "Error in direct frame extraction: $_" -ForegroundColor Red
            $errorCount++
        }
    }
}

# Step 5: Verify frame collection and create dataset for COLMAP
Write-Host "`n[5/5] VERIFYING FRAME COLLECTION AND CREATING DATASET..." -ForegroundColor Yellow
try {
    # Run verification and dataset creation
    python verify_and_create_dataset.py
    if (-not $?) {
        Write-Host "Warning: Dataset creation completed with issues. Trying standard method..." -ForegroundColor Yellow
        $warningCount++
        
        # Try the standard method as fallback
        python -m lightning_archive --phase dataset
    }
} catch {
    Write-Host "Error in verification and dataset creation: $_" -ForegroundColor Red
    
    # Try the standard method as fallback
    Write-Host "Trying standard dataset creation as fallback..." -ForegroundColor Yellow
    try {
        python -m lightning_archive --phase dataset
    } catch {
        Write-Host "Error in standard dataset creation: $_" -ForegroundColor Red
        $errorCount++
    }
}

# Final summary
Write-Host "`n===== PIPELINE EXECUTION SUMMARY =====" -ForegroundColor Cyan

if ($errorCount -eq 0 -and $warningCount -eq 0) {
    Write-Host "✅ All phases completed successfully!" -ForegroundColor Green
} elseif ($errorCount -eq 0) {
    Write-Host "⚠️ Pipeline completed with $warningCount warnings." -ForegroundColor Yellow
} else {
    Write-Host "❌ Pipeline completed with $errorCount errors and $warningCount warnings." -ForegroundColor Red
}

Write-Host "`nOutput locations:" -ForegroundColor Yellow
Write-Host " - Metadata: data/metadata/dataset_master.csv"
Write-Host " - Raw media: data/raw/youtube/ and data/raw/twitter/"
Write-Host " - Extracted frames: data/screens/youtube/[video_id]/ and data/screens/twitter/[media_id]/"
Write-Host " - Final COLMAP dataset: data/stills/colmap/"
Write-Host " - Logs: data/workflow_logs/"

# Pause to view results
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
